from types import SimpleNamespace
from typing import List

from planet.living_things.cells import Cell
from planet.living_things.dna.genes import Gene


class AnimalCell(Cell):
    """
    A cell needs enough space to live
    """
    def __init__(self, run_path: str, configuration: SimpleNamespace) -> None:
        # Store cell type
        self.cell_type = "animal"
        # Possible genes for this cell. Aquired by DNA mutation.
        # Genes are only present at start if you get lucky during DNA initialisation.
        self.gene_pool: List[Gene] = [
            Gene(name="NAR1", process_component="nitrogen", sequence="AATCGA"),
            Gene(name="OX42", process_component="oxygen", sequence="ATTGCA"),
            Gene(name="ARgo12", process_component="argon", sequence="AATCGACC"),
            Gene(name="CD0CD", process_component="carbon_dioxyde", sequence="AATCGAAAC")
        ]
        # Initialise cell
        super().__init__(run_path, configuration)
