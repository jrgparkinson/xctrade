""" Load equations """
import json
import logging

LOGGER = logging.getLogger(__name__)

# PATH = "../src/utils/math.json"
PATH = "src/utils/math.json"


def get_equation(eq: str):
    with open(PATH, "r") as f:
        eqs = json.load(f)
        # LOGGER.info(eqs)
        return eqs[eq]
