from pony.orm import *

from .base import SciNet


class Result(SciNet.Entity):
    resId = PrimaryKey(str, 32)
    resTime = Required(float)

    articles = Set('Article')
    graph = Required('Graph')
