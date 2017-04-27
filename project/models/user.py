from pony.orm import *

from .base import SciNet


class User(SciNet.Entity):
    _table_ = '_user'

    useId = PrimaryKey(str, 32)
    useType = Required(str, 3, default='res')
    useName = Required(str, 40)
    useLastName = Required(str, 40)
    useState = Required(str, 10, default='active')
    useArea = Required(str, 32, default='Not specified')
    useEmail = Required(str, 64)
    usePassword = Required(str)

    university = Required('University')
    querys = Set('Query')
