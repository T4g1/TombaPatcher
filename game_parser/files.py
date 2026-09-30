from pathlib import Path

from game_parser.mkpsxiso import dumpsxiso, mkpsxiso
from game_parser.fla import load_flas_with_lbas
from game_parser.ld import load_ld, FileInfo
from game_parser.gam import ungam, gam, GAM_SUFFIX, UNGAM_SUFFIX, is_gam

from common import (
    to_basepath,
    get_suffix_from_type,
    all,
    ISO_PATH,
    LD_PATH,
    GAM_PATH,
    XML_PATH,
    ENTRY_PATH,
    SYS_PATH,
)


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
    dumpsxiso(gamepath, ISO_PATH)

    flas = load_flas_with_lbas(ENTRY_PATH, XML_PATH)

    for ld_file in SYS_PATH.rglob("LD*.BIN"):
        files = load_ld(ld_file)

        source_file: Path | None = None
        offset: int = 0
        file_count: int = 0
        for file in files:
            if file.index != 0:
                offset = 0
                file_count = 0
                fla = flas[file.index]

                assert fla.path
                source_file = ISO_PATH / fla.path

                print(f"Loading from: {source_file}...")

                if is_gam(source_file):
                    gam_path = to_basepath(source_file, GAM_PATH).with_suffix(
                        UNGAM_SUFFIX
                    )

                    ungam(source_file, gam_path)
                    source_file = gam_path

            assert source_file

            text_suffix = get_suffix_from_type(file.type)

            output_path = to_basepath(source_file, LD_PATH).with_suffix(
                f".{file_count}.{file.type:04X}{text_suffix}"
            )

            load_file(source_file, output_path, file, offset)

            file_count += 1
            offset += file.size


def pack(resultpath: Path):
    flas = load_flas_with_lbas(ENTRY_PATH, XML_PATH)

    for ld_file in SYS_PATH.rglob("LD*.BIN"):
        files = load_ld(ld_file)

        for file in files:
            if file.index != 0:
                offset: int = 0
                file_count: int = 0
                fla = flas[file.index]

                assert fla.path
                archive_path = ISO_PATH / fla.path

                if is_gam(archive_path):
                    archive_path = to_basepath(archive_path, GAM_PATH).with_suffix(
                        UNGAM_SUFFIX
                    )

            assert archive_path

            text_suffix = get_suffix_from_type(file.type)

            processed_dir = LD_PATH / archive_path.parent.name
            input_path = (
                processed_dir
                / archive_path.with_suffix(
                    f".{file_count}.{file.type:04X}{text_suffix}"
                ).name
            )

            assert input_path.exists()

            save_file(input_path, archive_path, file, offset, append=file_count != 0)

            file_count += 1
            offset += file.size

    # Re-pack GAM files
    count = 10
    for path in GAM_PATH.rglob(all(UNGAM_SUFFIX)):
        output_path = to_basepath(path, ISO_PATH).with_suffix(GAM_SUFFIX)
        gam(path, output_path)

        count -= 1
        if count == 0:
            break

    mkpsxiso(resultpath)


if __name__ == "__main__":
    game_path = Path(
        "C:/Users/T4g1/Documents/Roms/PSX/Tomba! (USA) [SCUS-94236] Redump/Tomba! (USA).cue"
    )
    patched_path = game_path.parent / f"{game_path.stem}.patched{game_path.suffix}"

    unpack(game_path)
    pack(patched_path)
