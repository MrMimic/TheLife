import os
from dataclasses import dataclass, field
from datetime import datetime
from types import SimpleNamespace
from typing import Any, List
from uuid import uuid4

from utils.drawers import Drawer
from utils.logger import get_logger

from planet.inanimated_elements.air_composition import Atmosphere, Element
from planet.inanimated_elements.biomass_composition import Biomass, Nutrient


@dataclass
class Earth(object):

    diameter: int = 12742
    """ The diameter of the generated world (km)"""

    mass: int = 5.97237e24
    """ The mass of the generated world (kg) """

    population: List[Any] = field(default_factory=list)
    """ The population of the planet (cells, peoples, etc) """
    def __init__(self, configuration: SimpleNamespace) -> None:
        self.configuration = configuration
        self.run_folder = os.path.join(self.configuration.program.root_path, "runs",
                                       datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        self.log_folder = os.path.join(self.run_folder, "logs")
        self.draw_folder = os.path.join(self.run_folder, "draws", "earth")
        for folder in [self.log_folder, self.draw_folder]:
            os.makedirs(folder)

        # Planet components
        self.atmosphere: List[Element] = Atmosphere()
        self.biomass: List[Nutrient] = Biomass()

        # Planet logger
        self.planet_name = f"{self.__class__.__name__}_{uuid4()}"
        print(self.configuration.program.logs.level)
        self.logger = get_logger(log_folder=self.log_folder,
                                 log_name=self.planet_name,
                                 log_level=self.configuration.program.logs.level.upper())
        self.logger.info(f"Planet {self.planet_name} created")

        # Planet drawer
        self.drawer = Drawer(self.draw_folder, self.configuration)

    def populate(self, organism: Any):
        """
        Populate the planet with defined organisms.

        Args:
            organism (Any): the organism to populate the planet with.
        """
        # The organism type is provided for now
        max_population = self.configuration.world.population.limit
        self.population = [organism(self.run_folder, self.configuration) for _ in range(max_population)]
        self.logger.info(f"Planet populated with {max_population} {organism.__name__} individuals")

    def live(self, day_number: int):
        """
        Make the planet to live for a given period.

        Args:
            day_number (int): the actual number of days lived.
        """
        if len([individual for individual in self.population if individual.is_alive]) > 0:

            self.logger.info(f"Starting day {day_number}")
            for individual in self.population:

                # Some are dying in the process of living
                if individual.is_alive:

                    # Get ennergy (breathe / eat)
                    individual.breathe(air_composition=self.atmosphere.elements)
                    individual.eat(biomass_composition=self.biomass.components)

                    # Mutate and get acquired genes
                    individual.mutate()

                    # Process environment with genes (need energy)
                    individual.move()

                    # Reproduce

                    # Sleep / die
                    individual.sleep(day=day_number)

            # Draw the world at the end of each day
            self.drawer.draw_world(day=day_number, world=self)

        # Draw a GIF representing the world during the run
        if day_number == self.configuration.world.life.days:
            self.drawer.create_world_gif()
