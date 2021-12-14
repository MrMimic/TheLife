from dataclasses import dataclass


@dataclass
class Gene:
    """
    Class representing a gene.
    """
    name: str
    """ Name of the gene"""

    process_component: str
    """ Name of the chemical component this gene process """

    compopent_from: str
    """ Component coming from which medium """

    sequence: str
    """ Genetic sequence of the gene"""

    acquired: bool = False
    """ Whether this gene has been acquired byt the cell """
