
import json
from types import SimpleNamespace

import yaml

def read_configuration(config_file: str):
    """
    Reads the configuration file and returns a dictionary.
    """
    with open(config_file, "r") as stream:
        try:
            conf = yaml.safe_load(stream)
            # Yaml dict to python object
            return json.loads(json.dumps(conf), object_hook=lambda d: SimpleNamespace(**d))
        except yaml.YAMLError as error:
            print(error)
