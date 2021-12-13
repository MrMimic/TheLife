#!/usr/bin/env python

import json
from types import SimpleNamespace

import yaml

from planet.earth import Earth
from planet.living_things.animals.animal_cells import AnimalCell


def read_configuration(config_file):
    """
    Reads the configuration file and returns a dictionary with the configuration
    """
    with open(config_file, "r") as stream:
        try:
            conf = yaml.safe_load(stream)
            # Yaml dict to python object
            return json.loads(json.dumps(conf), object_hook=lambda d: SimpleNamespace(**d))
        except yaml.YAMLError as error:
            print(error)


def generates_world(configuration):
    """
    Generates the world according to the configuration.
    """
    world = Earth(configuration)
    world.populate(AnimalCell)
    return world


if __name__ == "__main__":
    configuration = read_configuration("configuration.yaml")
    world = generates_world(configuration)
    for day in range(1, 31):
        world.live(day)
