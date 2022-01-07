from types import SimpleNamespace
from typing import List

from planet.living_things.cells import Cell
from planet.living_things.dna.genes import Gene


class AnimalCell(Cell):
    """
    A cell needs enough space to live
    """
    def __init__(self, run_path: str, configuration: SimpleNamespace) -> None:
        # Possible genes for this cell. Aquired by DNA mutation.
        # Genes are only present at start if you get lucky during DNA initialisation.
        gene_pool: List[Gene] = [
            # Gas processing from the atmosphere
            Gene(name="NAR1", process_component="nitrogen", sequence="AATCGA", compopent_from="air"),
            Gene(name="OX42", process_component="oxygen", sequence="ATTGCA", compopent_from="air"),
            Gene(name="ARgo12", process_component="argon", sequence="AATCGACC", compopent_from="air"),
            Gene(name="CD0CD", process_component="carbon_dioxyde", sequence="AATCGAAAC", compopent_from="air"),
            # Component processing from the biomass
            Gene(name="NAR24", process_component="nitrogen", sequence="AATCGACTG", compopent_from="biomass"),
            Gene(name="CarBas3", process_component="carbon", sequence="ATTATTGAC", compopent_from="biomass"),
        ]
        # Initialise cell
        super().__init__(run_path, configuration, gene_pool)
