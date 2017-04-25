from pony.orm import *
from .base import SciNet


class File(SciNet.Entity):
    filId = PrimaryKey(str, 32)
    filName = Required(str, 32)
    filContent = Required(str)

    query = Optional('Query')
