import os

from libs.eth_async.utils.utils import update_dict
from libs.eth_async.utils.files import touch, write_json, read_json

from data import config


def create_files():
    touch(path=config.FILES_DIR)

    if not os.path.exists(config.PRIVATE_FILE):
        with open(config.PRIVATE_FILE, "w") as f:
            pass

    if not os.path.exists(config.PROXY_FILE):
        with open(config.PROXY_FILE, "w") as f:
            pass

    if not os.path.exists(config.WITHDRAW_FILE):
        with open(config.WITHDRAW_FILE, "w") as f:
            pass

    if not os.path.exists(config.RESERVE_PROXY_FILE):
        with open(config.RESERVE_PROXY_FILE, "w") as f:
            pass

    if not os.path.exists(config.ENV_FILE):
        with open(config.ENV_FILE, "w") as f:
            pass

    try:
        current_settings: dict | None = read_json(path=config.SETTINGS_FILE)
    except Exception:
        current_settings = {}

    settings = {
        "withdraw": True,
        "bridge": {"use_base": True, "use_arbitrum": True, "use_optimism": True, "max_eth_for_bridge": 0.001},
        "wallets": {
            "range": {
                "start": 0,
                "end": 0,
            },
            "startup_delay": {
                "min": 0,
                "max": 7200,
            },
            "transactions_delay": {
                "min": 0,
                "max": 30,
            },
        },
        "resources": {
            "auto_replace": True,
            "max_failures": 3,
        },
    }
    write_json(
        path=config.SETTINGS_FILE,
        obj=update_dict(modifiable=current_settings, template=settings),
        indent=2,
    )


create_files()
