import config, asyncio, sys, os, mod_pyrogram
from pyrogram import Client, idle

# from config import API_ID, API_HASH, TOKEN


async def run_client(client):
    try:
        await client.start()
    except AttributeError as e:
        return print(str(e).split(". ")[0])
    client.set_parse_mode("combined")

    await idle()

    #    client = Client("Phoenix", API_ID, API_HASH, bot_token=TOKEN, plugins=dict(root="plugins", exclude=disabled_plugins))
    client = Client("Phoenix")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_client(client))
