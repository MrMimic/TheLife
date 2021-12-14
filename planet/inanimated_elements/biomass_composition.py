from dataclasses import dataclass
from typing import List

from planet.inanimated_elements.composition import Component


@dataclass
class Nutrient(Component):

    name: str
    """ Name of the nutrient"""

    percentage: float
    """ Percentage of the nutrient in the planet """

    energy: int
    """ Energy restaured by consuming this nutrient """


class Biomass:
    def __init__(self) -> None:
        self.components: List[Nutrient] = [
            Nutrient(name="Carbon", percentage=0.7, energy=4),
            Nutrient(name="Nitrogen", percentage=0.3, energy=2)
        ]