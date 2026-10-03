from pathlib import Path

from game_parser.fla import flas_load_with_lbas, FLA
from game_parser.ld import ld_load_all, FileInfo
from game_parser.gam import UNGAM_SUFFIX, is_gam

from common import (
    to_basepath,
    get_suffix_from_type,
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
) -> bool:
    """Returns True if the file saved differs from the given file info
    In which case, the file info is updated with the new value"""
    print(
        f"Saving {outputpath}: 0x{info.index:03X} of type 0x{info.type:04X} at {offset} of size {info.size}..."
    )

    info_changed = False

    with open(filepath, "rb") as f:
        data = f.read()

    if len(data) != info.size:
        info.size = len(data)
        info_changed = True

        if info.width != 0 or info.height != 0:
            # TODO: Find a way to update width/height too
            raise ValueError("Changing image size is not yet supported")

    mode = "wb"
    if append:
        mode = "a+b"

    with open(outputpath, mode) as f:
        f.write(data)

    return info_changed


def unpack(
    base: Path, to: Path, files: list[FileInfo], gam_path: Path, flas: dict[int, FLA]
):
    source_file: Path | None = None
    offset: int = 0
    file_count: int = 0
    for file in files:
        if file.index != 0:
            offset = 0
            file_count = 0
            fla = flas[file.index]

            assert fla.path
            source_file = base / fla.path

            print(f"Loading from: {source_file}...")

            if is_gam(source_file):
                # Assume UNGAM is already done
                source_file = to_basepath(source_file, gam_path).with_suffix(
                    UNGAM_SUFFIX
                )

        assert source_file

        text_suffix = get_suffix_from_type(file.type)

        output_path = to_basepath(source_file, to).with_suffix(
            f".{file_count}.{file.type:04X}{text_suffix}"
        )

        load_file(source_file, output_path, file, offset)

        file_count += 1
        offset += file.size


def pack(
    base: Path, to: Path, files: list[FileInfo], gam_path: Path, flas: dict[int, FLA]
) -> list[FileInfo]:
    """Re-construct each file info into the corresponding LD entry
    Returns a list of FileInfo entries that have changed"""
    updates = []

    for file in files:
        if file.index != 0:
            offset: int = 0
            file_count: int = 0
            fla = flas[file.index]

            assert fla.path
            archive_path = to / fla.path

            if is_gam(archive_path):
                archive_path = to_basepath(archive_path, gam_path).with_suffix(
                    UNGAM_SUFFIX
                )

        assert archive_path

        text_suffix = get_suffix_from_type(file.type)

        processed_dir = base / archive_path.parent.name
        input_path = (
            processed_dir
            / archive_path.with_suffix(
                f".{file_count}.{file.type:04X}{text_suffix}"
            ).name
        )

        assert input_path.exists()

        if save_file(input_path, archive_path, file, offset, append=file_count != 0):
            updates.append(file)

        file_count += 1
        offset += file.size

    return updates


if __name__ == "__main__":
    flas = flas_load_with_lbas(ENTRY_PATH, XML_PATH)
    infos = ld_load_all(ISO_PATH, LD_PATH, SYS_PATH, flas, GAM_PATH)
    unpack(ISO_PATH, LD_PATH, infos, GAM_PATH, flas)
    pack(LD_PATH, ISO_PATH, infos, GAM_PATH, flas)
