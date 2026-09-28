import re
from pathlib import Path

from game_parser.mkpsxiso import unpack as dumpsxiso
from game_parser.lba import load_lbas
from game_parser.fla import load_flas
from game_parser.ld import load_ld, FileInfo
from game_parser.gam import unpack as unpack_gam

PATTERN_TO_SUFFIX: dict[str, str] = {
    "6.FF": "RLE",
    "5080": "RLE",
}


def get_suffix(search_key: str):
    for pattern, suffix in PATTERN_TO_SUFFIX.items():
        if re.match(pattern, search_key):
            return suffix

    return search_key


def load_file(filepath: Path, outputpath: Path, info: FileInfo, offset: int):
    print(
        f"Loading file 0x{info.index:03X} of type 0x{info.type:04X} at {offset} of size {info.size}..."
    )

    with open(filepath, "rb") as f:
        f.seek(offset)
        data = f.read(info.size)

    with open(outputpath, "wb") as output:
        output.write(data)


def save_file(filepath: Path, outputpath: Path, info: FileInfo, offset: int):
    print(
        f"Saving file 0x{info.index:03X} of type 0x{info.type:04X} at {offset} of size {info.size}..."
    )

    with open(filepath, "rb") as f:
        data = f.read()

    # TODO: Reverse LD files better to be able to rebuild them too
    # Can't change anything from LD files
    assert len(data) == info.size

    with open(outputpath, "a+b") as f:
        f.write(data)


def unpack(gamepath: Path):
    print("Dump ISO...")
    dumpath = Path("output/files")
    dumpsxiso(gamepath, dumpath)

    print("Load LBA...")
    xmlpath = Path("output/tomba.xml")
    lbas = load_lbas(xmlpath)

    print("Load LFA...")
    mainpath = dumpath / "SCUS_942.36"
    flas = load_flas(mainpath)

    print("Merging LBA and FLA")
    for fla in flas.values():
        fla.path = lbas[fla.lba]

    syspath = dumpath / "SYS"
    for ldpath in syspath.rglob("*.BIN"):
        print(f"Load LD: {ldpath}...")
        files = load_ld(ldpath)

        filepath: Path | None = None
        offset: int = 0
        file_count: int = 0
        for file in files:
            if file.index != 0:
                offset = 0
                file_count = 0
                fla = flas[file.index]

                assert fla.path
                filepath = dumpath / fla.path

                print(f"Loading from: {filepath}...")

                if filepath.suffix == ".GAM":
                    unpackedpath = Path("output/unpacked") / filepath.parent.name
                    unpackedpath.mkdir(parents=True, exist_ok=True)
                    unpackedpath = unpackedpath / filepath.name

                    print(f"Unpacking to: {unpackedpath}...")
                    unpack_gam(filepath, unpackedpath)
                    filepath = unpackedpath

            assert filepath

            type_suffix = f"{file.type:04X}"
            text_suffix = get_suffix(type_suffix)

            outputpath = Path("output/processed") / filepath.parent.name
            outputpath.mkdir(parents=True, exist_ok=True)
            outputpath = (
                outputpath / filepath.with_suffix(f".{file_count}.{text_suffix}").name
            )

            load_file(filepath, outputpath, file, offset)

            file_count += 1
            offset += file.size


def pack(outputpath: Path):
    # TODO: repack all files
    pass


if __name__ == "__main__":
    gamepath = Path(
        "C:/Users/T4g1/Documents/Roms/PSX/Tomba! (USA) [SCUS-94236] Redump/Tomba! (USA).cue"
    )
    resultpath = gamepath.parent / f"{gamepath.stem}.patched{gamepath.suffix}"
    unpack(gamepath)

    # pack(resultpath)
