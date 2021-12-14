#!/usr/bin/env python

from planet.earth import Earth
from planet.living_things.animals.animal_cells import AnimalCell
from utils.configuration import read_configuration

if __name__ == "__main__":
    configuration = read_configuration("configuration.yaml")
    world = Earth(configuration)
    world.populate(AnimalCell)
    for day in range(1, configuration.world.life.days + 1):
        world.live(day)
