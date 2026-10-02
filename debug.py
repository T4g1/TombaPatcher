from common import LD_PATH

if __name__ == "__main__":
    needle = bytes.fromhex("04010000000007000301000000000600")
    for file in LD_PATH.rglob("*.*"):
        with open(file, "rb") as f:
            data = f.read()

        result = data.find(needle)
        if result > 0:
            print(file, f"{result:08X}")
