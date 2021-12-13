import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4

from utils.logger import get_logger


@dataclass
class Earth(object):
    """ The diameter of the generated world (km)"""
    diameter: int = 12742
    """ The mass of the generated world (kg) """
    mass: int = 5.97237e24
    """ The population of the planet (cells, peoples, etc) """
    population: List[Any] = field(default_factory=list)
    """ Air composition (%) """
    def __init__(self, configuration) -> None:
        self.configuration = configuration
        self.run_folder = os.path.join(self.configuration.program.root_path, "runs",
                                       datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        self.log_folder = os.path.join(self.run_folder, "logs")
        os.makedirs(self.log_folder)

        # Planet components
        self.air: Dict[str, float] = {"nitrogen": 78.0, "oxygen": 21.0, "argon": 1.0, "carbon_dioxyde": 0.04}
        self.food: Dict[str, float] = {}

        # Planet logger
        self.planet_name = f"{self.__class__.__name__}_{uuid4()}"
        self.logger = get_logger(self.log_folder, self.planet_name)
        self.logger.info(f"Planet {self.planet_name} created")

    def populate(self, organism: Any):
        # The organism type is provided for now
        max_population = self.configuration.world.population.limit
        self.population = [organism(self.run_folder, self.configuration) for _ in range(max_population)]
        self.logger.info(f"Planet populated with {max_population} {organism.__name__} individuals")

    def live(self, day_number: int):
        self.logger.info(f"Starting day {day_number}")
        for individual in self.population:

            # Get ennergy (breathe / eat)
            individual.breathe(self.air)
            # individual.eat(self.food)

            # Mutate and get acquired genes
            individual.mutate()

            # Process environment with genes (need energy)

            # Reproduce

            # Sleep
            individual.sleep()
