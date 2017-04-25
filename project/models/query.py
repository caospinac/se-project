from datetime import datetime

from pony.orm import *

from .base import SciNet


class Query(SciNet.Entity):
    queId = PrimaryKey(int, auto=True)
    queDate = Required(datetime, sql_default='CURRENT_TIMESTAMP')
    queTopic = Required(LongStr)
    queDescription = Optional(LongStr)

    user = Required('User')
    file = Required('File')
    graph = Optional('Graph')
