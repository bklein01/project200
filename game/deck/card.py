"""Playing card.

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class Card -- The playing card M/C.
"""

from core.datamodel import DataModelController, classproperty
from core.enum import EnumInt


class Card(DataModelController):

    Suit = EnumInt('SPADES', 'HEARTS', 'CLUBS', 'DIAMONDS')

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    def MODEL_RULES(cls):
        return {
            'suit': ('suit', str, None),
            'value': ('value', int, None)
        }

    def __init__(self, suit, value):
        self.suit, self.value = suit, value
        super(Card, self).__init__(self.__class__.MODEL_RULES)

    def __setattr__(self, key, value):
        if hasattr(self, key):
            raise ValueError('Card object cannot be changed once assigned.')
        super(Card, self).__setattr__(key, value)

