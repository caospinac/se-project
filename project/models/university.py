from pony.orm import *

from .base import SciNet


class University(SciNet.Entity):
    uniId = PrimaryKey(LongStr, lazy=False)
    uniName = Required(LongStr)
    
    users = Set(User)