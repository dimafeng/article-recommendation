from abc import ABC, abstractmethod

from article_recs.context import Context


class Scorer(ABC):
    def __init__(self, context: Context):
        self._context = context

    @abstractmethod
    def score(self):
        pass