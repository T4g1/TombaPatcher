from pathlib import Path

from common import logger


def find_binary():
    needle = bytes.fromhex("0ff002ff140ff002ff0f1400")
    base = Path("retail/iso")
    for file in base.rglob("*.*"):
        with open(file, "rb") as f:
            data = f.read()

        result = data.find(needle)
        if result > 0:
            logger.info(file, f"{result:08X}")


if __name__ == "__main__":
    logger.info("test")
    find_binary()
