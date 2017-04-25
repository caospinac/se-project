from pony.orm import *

from .base import SciNet


class Graph(SciNet.Entity):
    graId = PrimaryKey(LongStr, lazy=False)
    graCount = Required(float)

    query = Required('Query')
    result = Optional('Result')
