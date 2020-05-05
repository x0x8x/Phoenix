import logging, traceback, sys, os, html, textwrap, asyncio
from io import StringIO
from contextlib import redirect_stdout

from pyrogram import Client, filters
from pyrogram.types import Message

from pyrogram.errors.exceptions.bad_request_400 import (
    MessageNotModified,
    MessageTooLong,
    AboutTooLong,
)
from pyrogram.errors.exceptions.flood_420 import FloodWait

from config import sudoers, cmds
from utils import meval


@Client.on_message(filters.command("eval", prefixes=".") & filters.user(sudoers))
async def eval(client, message):
    text = message.text[6:]
    caption = (
        "<b>Evaluated expression:</b>\n<code>{}</code>\n\n<b>Result:</b>\n".format(text)
    )
    preserve_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        res = str(await meval(text, locals()))
    except Exception:
        caption = (
            "<b>Evaluation failed:</b>\n<code>{}</code>\n\n<b>Result:</b>\n".format(
                text
            )
        )
        etype, value, tb = sys.exc_info()
        res = "".join(traceback.format_exception(etype, value, None, 0))
        sys.stdout = preserve_stdout
    try:
        val = sys.stdout.getvalue()
    except AttributeError:
        val = None
    sys.stdout = preserve_stdout
    try:
        await message.reply(caption + f"<code>{html.escape(res)}</code>")

    except MessageTooLong:
        res = textwrap.wrap(res, 4096 - len(caption))
        await message.reply(caption + f"<code>{res[0]}</code>")
        for part in res[1::]:
            await asyncio.sleep(2)
            await message.reply(f"<code>{part}</code>")

        else:
            await message.reply_text(caption)


@Client.on_message(filters.command("exec", prefixes=".") & filters.user(sudoers))
async def exec(client, message):
    strio = io.StringIO()
    code = message.text.split(maxsplit=1)[1]
    exec(
        "async def __ex(client, message): "
        + " ".join("\n " + l for l in code.split("\n"))
    )
    with redirect_stdout(strio):
        try:
            await locals()["__ex"](client, message)
        except:
            return await message.reply_text(
                html.escape(traceback.format_exc()), parse_mode="HTML"
            )

    if strio.getvalue():
        out = f"<code>{html.escape(strio.getvalue())}</code>"
    else:
        out = "Command executed."
    await message.reply_text(out, parse_mode="HTML")
