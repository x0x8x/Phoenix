import logging, traceback, sys, os, html, textwrap, asyncio
from io import StringIO

from pyrogram import Client, Filters, Message
from pyrogram.errors.exceptions.bad_request_400 import (
    MessageNotModified,
    MessageTooLong,
    AboutTooLong,
)
from pyrogram.errors.exceptions.flood_420 import FloodWait

from config import sudoers, cmds
from utils import meval


@Client.on_message(
    Filters.command("eval", prefixes=".") & Filters.user(sudoers) & Filters.me
)
async def eval(client, message):
    text = message.text[6:]
    caption = "<b>Evaluated expression:</b>\n<code>{}</code>\n\n<b>Result:</b>\n".format(
        text
    )
    preserve_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        res = str(await meval(text, locals()))
    except Exception:
        caption = "<b>Evaluation failed:</b>\n<code>{}</code>\n\n<b>Result:</b>\n".format(
            text
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
        await message.edit(caption + f"<code>{html.escape(res)}</code>")

    except MessageTooLong:
        res = textwrap.wrap(res, 4096 - len(caption))
        await message.reply(caption + f"<code>{res[0]}</code>")
        for part in res[1::]:
            await asyncio.sleep(2)
            await message.reply(f"<code>{part}</code>")

        else:
            await message.reply_text(caption)


@Client.on_message(
    Filters.command("exec", prefixes=".") & Filters.user(sudoers) & Filters.me
)
async def exec(client, message):
    from meval import meval

    text = message.text[6:]
    try:
        await meval(text, locals())
    except Exception as e:
        print(e)

