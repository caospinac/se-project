from pony.orm import *

from .base import SciNet


class Graph(SciNet.Entity):
    graId = PrimaryKey(str, 32)
    graContent = Required(str)

    query = Required('Query')
    result = Optional('Result')
