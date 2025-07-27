from libs.eth_async.utils.files import read_json
from libs.eth_async.data.models import RawContract, DefaultABIs
from libs.eth_async.classes import Singleton

from data.config import ABIS_DIR


class Contracts(Singleton):
    WPLUME = RawContract(
        title="WPLUME",
        address="0xEa237441c92CAe6FC17Caaf9a7acB3f953be4bd1",
        abi=read_json(path=(ABIS_DIR, "wplume.json")),
    )
