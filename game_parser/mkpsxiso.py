import subprocess

from pathlib import Path

XML_NAME = "tomba.xml"


def unpack(filepath: Path, destination: Path):
    """Given a ISO or BIN/CUE file:
    Extracts all files from it"""
    cmd = [
        "dumpsxiso",
        "-x",
        str(destination),
        "-s",
        f"output/{XML_NAME}",
        str(filepath),
    ]

    try:
        subprocess.run(cmd, shell=True)
    except subprocess.CalledProcessError as exception:
        raise Exception(exception)


def pack(outputpath: Path):
    """Given a list of files:
    Pack a ISO or BIN/CUE form them"""
    suffix = ".bin"
    if outputpath.suffix == ".iso":
        suffix = ".iso"

    cmd = [
        "mkpsxiso",
        "-o",
        str(outputpath.with_suffix(suffix)),
        "-c",
        str(outputpath.with_suffix(".cue")),
        "-y",
        f"output/{XML_NAME}",
    ]

    try:
        subprocess.run(cmd, shell=True)
    except subprocess.CalledProcessError as exception:
        raise Exception(exception)
