"""Playing card.

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class Card -- The playing card M/C.
    :Enum Card.Suit -- Enumerated suit types.
    :Enum Card.Value -- Enumerated face values.
"""

from core.datamodel import DataModelController
from core.decorators import classproperty
from core.enum import EnumInt


class Card(DataModelController):
    """Playing card structure.

    Class Properties:
        :type Suit: EnumInt -- Enumerated card Suit types.
        :type Value: EnumInt -- Enumerated card values.
        :type MODEL_RULES: dict -- The set of rules for the `DataModel`.

    Init Parameters:
        suit -- The suit of the card.
        value -- The face value of the card.
    """

    Suit = EnumInt('DIAMONDS', 'CLUBS', 'HEARTS', 'SPADES')

    Value = EnumInt('JOKER', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN',
                    'EIGHT', 'NINE', 'TEN', 'JACK', 'QUEEN', 'KING', 'ACE')

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    def MODEL_RULES(cls):
        """The rule set for the underlying `DataModel`.

        New Model Keys:
            :key suit: int -- The Card.Suit value.
            :key value: int -- The Card.Value value.
        """
        return {
            'suit': ('suit', int, None),
            'value': ('value', int, None)
        }

    def __init__(self, suit, value):
        """Card init.

        :param suit: Card.Suit/int -- The card suit.
        :param value: Card.Value/int -- The card face value.
        """
        self.suit, self.value = suit, value
        super(Card, self).__init__(self.__class__.MODEL_RULES)

    def __setattr__(self, key, value):
        if hasattr(self, key):
            raise ValueError('Card object cannot be changed once assigned.')
        super(Card, self).__setattr__(key, value)

