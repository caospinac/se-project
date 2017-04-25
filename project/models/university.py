from pony.orm import *

from .base import SciNet


class University(SciNet.Entity):
    uniId = PrimaryKey(str, 32)
    uniName = Required(str, 64, unique=True)

    users = Set('User')
