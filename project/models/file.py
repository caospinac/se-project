from pony.orm import *
from .base import SciNet


class File(SciNet.Entity):
    filId = PrimaryKey(LongStr, lazy=False)
    filName = Required(LongStr)
    filContent = Required(LongStr)

    query = Optional('Query')
