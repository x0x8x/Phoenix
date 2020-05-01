import config, asyncio. sys, os


async def run_client(client):
    try:
        await client.start()
    except AttributeError as e:
        return print(
            str(e).split(". ")[0]
            + f". Run '{os.path.basename(sys.executable)} setup.py' first."
        )
    client.set_parse_mode("combined")

    await client.idle()


loop = asyncio.get_event_loop()
loop.run_until_complete(run_client(config.client))
