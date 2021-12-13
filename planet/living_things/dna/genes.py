from dataclasses import dataclass


@dataclass
class Gene:
    """
    Class representing a gene.
    """
    name: str
    process_component: str
    sequence: str
    acquired: bool = False
