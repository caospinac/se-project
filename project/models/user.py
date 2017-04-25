from pony.orm import *

from .base import SciNet


class User(SciNet.Entity):
	_table_ = '_user'

    useId = PrimaryKey(LongStr, lazy=False)
    useType = Required(LongStr, default='res')
    useNickName = Required(LongStr, unique=True)
    useState = Required(LongStr, default='active')
    useArea = Required(LongStr)
    usePassword = Required(LongStr)
    
    university = Required('University')
	querys = Set('Query')