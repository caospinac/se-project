from pony.orm import *

from .base import SciNet


class Graph(SciNet.Entity):
    graId = PrimaryKey(str, 32)
    graCount = Required(float)

    query = Required('Query')
    result = Optional('Result')
