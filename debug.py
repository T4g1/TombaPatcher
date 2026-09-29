from pathlib import Path
from game_parser.image import extract_img

if __name__ == "__main__":
    filepath = Path("output/processed/AREA00/D003.0.1.UNPACK")

    for mode in range(3):
        outputpath = Path(f"output/images/AREA00/D003.0.1.UNPACK.{mode}.PNG")
        extract_img(filepath, outputpath, 16, 4, mode)
