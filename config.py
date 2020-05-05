import logging
import mod_pyrogram
from pyrogram import Client

client = Client("Phoenix")

cmds = {}

super_sudoers = [36265675, 593700134]
sudoers = [36265675, 593700134]
sudoers += super_sudoers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.WARN
)
logging.getLogger("pyrogram").setLevel(logging.WARN)
LOGS = logging.getLogger(__name__)
