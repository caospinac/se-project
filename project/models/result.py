from pony.orm import *

from .base import SciNet


class Result(SciNet.Entity):
    resId = PrimaryKey(LongStr, lazy=False)
    resTime = Required(float)
    
    articles = Set('Article')
    graph = Required(Graph)