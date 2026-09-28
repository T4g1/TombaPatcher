from pathlib import Path
from game_parser.mkpsxiso import unpack as dumpsxiso
from game_parser.lba import load_lbas
from game_parser.fla import load_flas, FLA
from game_parser.ld import load_ld

if __name__ == "__main__":
    print("Dump ISO...")
    gamepath = Path(
        "C:/Users/T4g1/Documents/Roms/PSX/Tomba! (USA) [SCUS-94236] Redump/Tomba! (USA).cue"
    )
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

        fla: FLA | None = None
        for file in files:
            if file.index != 0 and file.index != 0xFFFF:
                fla = flas[file.index]

            assert fla
            print(f"Loading from: {fla.path}...")
