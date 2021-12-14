from dataclasses import dataclass
from typing import List

from planet.inanimated_elements.composition import Component


@dataclass
class Element(Component):
    name: str
    """ Name of the element """

    symbol: str
    """ Symbol of the element """

    percentage: float
    """ Percentage of the element in the atmosphere """

    energy: int
    """ Energy restaured by breathing this gas """

    comes_from: str
    """ Where the element comes from """


class Atmosphere:
    def __init__(self):
        self.elements: List[Element] = [
            Element(name="Nitrogen", symbol="N", percentage=78.0, energy=8, comes_from="atmosphere"),
            Element(name="Oxygen", symbol="O", percentage=21.0, energy=2, comes_from="atmosphere"),
            Element(name="Argon", symbol="Ar", percentage=1.0, energy=1, comes_from="atmosphere"),
            Element(name="Carbon Dioxyde", symbol="Cd", percentage=0.04, energy=8, comes_from="atmosphere")
        ]
