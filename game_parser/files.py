import re
from pathlib import Path

from game_parser.mkpsxiso import unpack as dumpsxiso, pack as mkpsxiso
from game_parser.fla import load_flas_with_lbas
from game_parser.ld import load_ld, FileInfo
from game_parser.gam import unpack as unpack_gam, pack as pack_gam

from common import to_basepath

PATTERN_TO_SUFFIX: dict[str, str] = {"60FF": "RLE", "62FF": "RLE", "D1FF": "WFM"}


def get_suffix(search_key: str):
    for pattern, suffix in PATTERN_TO_SUFFIX.items():
        if re.match(pattern, search_key):
            return "." + suffix

    return ""


def load_file(filepath: Path, outputpath: Path, info: FileInfo, offset: int):
    print(
        f"Loading {outputpath}: file 0x{info.index:03X} of type 0x{info.type:04X} at {offset} of size {info.size}..."
    )

    assert info.size > 0

    with open(filepath, "rb") as f:
        f.seek(offset)
        data = f.read(info.size)

    assert len(data) == info.size

    with open(outputpath, "wb") as output:
        output.write(data)


def save_file(
    filepath: Path, outputpath: Path, info: FileInfo, offset: int, append: bool = True
):
    print(
        f"Saving {outputpath}: 0x{info.index:03X} of type 0x{info.type:04X} at {offset} of size {info.size}..."
    )

    with open(filepath, "rb") as f:
        data = f.read()

    # TODO: Reverse LD files better to be able to rebuild them too
    # Can't change anything from LD files
    assert len(data) == info.size

    mode = "wb"
    if append:
        mode = "a+b"

    with open(outputpath, mode) as f:
        f.write(data)


def unpack(gamepath: Path):
    processedpath = Path("output/processed")

    print("Dump ISO...")
    dumpath = Path("output/files")
    dumpsxiso(gamepath, dumpath)

    xmlpath = Path("output/tomba.xml")
    mainpath = dumpath / "SCUS_942.36"
    flas = load_flas_with_lbas(mainpath, xmlpath)

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
                    unpackedpath = to_basepath(filepath, Path("output/ugam"))

                    print(f"Unpacking to: {unpackedpath}...")
                    unpack_gam(filepath, unpackedpath)
                    filepath = unpackedpath

            assert filepath

            type_suffix = f"{file.type:04X}"
            text_suffix = get_suffix(type_suffix)

            outputpath = processedpath / filepath.parent.name
            outputpath.mkdir(parents=True, exist_ok=True)
            outputpath = (
                outputpath
                / filepath.with_suffix(f".{file_count}.{type_suffix}{text_suffix}").name
            )

            load_file(filepath, outputpath, file, offset)

            file_count += 1
            offset += file.size


def pack(resultpath: Path):
    dumpath = Path("output/files")
    processedpath = Path("output/processed")
    xmlpath = Path("output/tomba.xml")
    mainpath = dumpath / "SCUS_942.36"
    flas = load_flas_with_lbas(mainpath, xmlpath)

    ugampath = Path("output/ugam")

    syspath = dumpath / "SYS"
    for ldpath in syspath.rglob("*.BIN"):
        print(f"Load LD: {ldpath}...")
        files = load_ld(ldpath)

        for file in files:
            if file.index != 0:
                offset: int = 0
                file_count: int = 0
                fla = flas[file.index]

                assert fla.path
                archivepath = dumpath / fla.path

                if archivepath.suffix == ".GAM":
                    archivepath = to_basepath(archivepath, ugampath)

            assert archivepath

            type_suffix = f"{file.type:04X}"
            text_suffix = get_suffix(type_suffix)

            processed_dir = processedpath / archivepath.parent.name
            inputpath = (
                processed_dir
                / archivepath.with_suffix(
                    f".{file_count}.{type_suffix}{text_suffix}"
                ).name
            )

            assert inputpath.exists()

            save_file(inputpath, archivepath, file, offset, append=file_count != 0)

            file_count += 1
            offset += file.size

    # Re-pack GAM files
    count = 10
    for path in ugampath.rglob("*.GAM"):
        print(f"Packing: {path}...")
        outputpath = to_basepath(path, dumpath)
        pack_gam(path, outputpath)

        count -= 1
        if count == 0:
            break

    # Re-build ISO/BIN
    print("Dump ISO...")
    mkpsxiso(resultpath)


if __name__ == "__main__":
    gamepath = Path(
        "C:/Users/T4g1/Documents/Roms/PSX/Tomba! (USA) [SCUS-94236] Redump/Tomba! (USA).cue"
    )
    resultpath = gamepath.parent / f"{gamepath.stem}.patched{gamepath.suffix}"
    unpack(gamepath)

    pack(resultpath)
