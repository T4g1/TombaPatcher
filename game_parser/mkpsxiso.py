import subprocess

from pathlib import Path

from common import logger, ISO_PATH, XML_PATH


def dumpsxiso(filepath: Path, destination: Path):
    """Given a ISO or BIN/CUE file:
    Extracts all files from it"""
    logger.info(f"ISO/BIN: Dumping to {destination}...")

    cmd = [
        "dumpsxiso",
        "-l",
        "-x",
        str(destination),
        "-s",
        XML_PATH,
        str(filepath),
    ]

    try:
        subprocess.run(cmd, shell=True)
    except subprocess.CalledProcessError as exception:
        raise Exception(exception)


def mkpsxiso(outputpath: Path) -> Path:
    """Given a list of files:
    Pack a ISO or BIN/CUE form them"""
    logger.info(f"ISO/BIN: Constructing {outputpath}...")

    suffix = ".bin"
    if outputpath.suffix == ".iso":
        suffix = ".iso"

    resultpath = outputpath.with_suffix(suffix)

    cmd = [
        "mkpsxiso",
        "-o",
        str(resultpath),
        "-c",
        str(outputpath.with_suffix(".cue")),
        "-y",
        XML_PATH,
    ]

    try:
        subprocess.run(cmd, shell=True)
    except subprocess.CalledProcessError as exception:
        raise Exception(exception)

    return resultpath


if __name__ == "__main__":
    game_path = Path(
        "C:/Users/T4g1/Documents/Roms/PSX/Tomba! (USA) [SCUS-94236] Redump/Tomba! (USA).cue"
    )
    patched_path = game_path.parent / f"{game_path.stem}.patched{game_path.suffix}"

    dumpsxiso(game_path, ISO_PATH)
    mkpsxiso(patched_path)
