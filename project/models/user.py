from pony.orm import *

from .base import SciNet


class User(SciNet.Entity):
    _table_ = '_user'

    useId = PrimaryKey(str, 32)
    useType = Required(str, default='res')
    useNickName = Required(str, unique=True)
    useState = Required(str, default='active')
    useArea = Required(str)
    usePassword = Required(str)

    university = Required('University')
    querys = Set('Query')
