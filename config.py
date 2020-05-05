import logging

# --- Bot token from Bot Father
TOKEN = "1234567890:BOT_TOKEN"

# --- Log Settings
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.WARN
)

logging.getLogger("pyrogram").setLevel(logging.WARN)

LOGS = logging.getLogger(__name__)

# --- Chat used for logs

log_chat = "self"

# --- Sudoers and super sudoers
super_sudoers = ["self"]
sudoers = [593700134]
sudoers += super_sudoers


# --- Prefixes for commands, e.g: /command and !command
prefix = ["."]
cmds = {}

# --- List of disabled plugins
disabled_plugins = []
