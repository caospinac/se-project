from pony.orm import *

from .base import SciNet


class Reference(SciNet.Entity):
    refId = PrimaryKey(int, auto=True)
    articles = Set('Article')
