import yaml

path = "config/gtm.yml"


class Config:

    API = {}

    DATABASE = {}

    PAIRS = []

    BRIDGE = None

    @staticmethod
    def read_config():

        with open(path) as yml:
            config = yaml.safe_load(yml)

        Config.API = config["API"]
        Config.DATABASE = config["DATABASE"]
        Config.PAIRS = config["PAIRS"].split()
        Config.BRIDGE = config["BRIDGE"]
