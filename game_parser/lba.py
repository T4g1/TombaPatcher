from pathlib import Path
import xml.etree.ElementTree as ET

from common import logger


def load_lbas(xmlpath: Path) -> dict[int, str]:
    """
    Parses a mkpsxiso XML configuration to extract Logical Block Addresses (LBA)
    """
    logger.info("LBA: Loading")

    lbas: dict[int, str] = {}

    tree = ET.parse(xmlpath)
    root = tree.getroot()

    def parse_node(element: ET.Element, current_path: str):
        for child in element:
            if child.tag in ("file", "dir"):
                name = child.get("name", "")
                offs_str = child.get("offs")

                # Construct the full ISO path
                node_path = f"{current_path}/{name}" if current_path else name

                if offs_str is not None:
                    address = int(offs_str)

                    lbas[address] = node_path

                if child.tag == "dir":
                    parse_node(child, node_path)

    dir_tree = root.find(".//directory_tree")
    if dir_tree is not None:
        # mkpsxiso directory_tree root can also have a starting sector offset
        tree_offs = dir_tree.get("offs")
        if tree_offs is not None:
            address = int(tree_offs)
            lbas[address] = ""

        parse_node(dir_tree, current_path="")

    return lbas


if __name__ == "__main__":
    lbas = load_lbas(Path("output/tomba.xml"))

    for address, path in lbas.items():
        logger.info(f"{address}: {path}")
