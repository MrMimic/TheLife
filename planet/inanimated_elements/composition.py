from abc import ABC
from dataclasses import dataclass


@dataclass
class Component(ABC):

    name: str
    """ Name of the component"""

    percentage: float
    """ Percentage of the component in the planet """

    energy: int
    """ Energy restaured by consuming this component """
