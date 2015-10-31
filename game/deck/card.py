"""Playing card.

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class Card -- The playing card M/C.
    :Enum Card.Suit -- Enumerated suit types.
    :Enum Card.Value -- Enumerated face values.
"""

from core.dotdict import ImmutableDotDict
from core.exceptions import InitError
from core.enum import EnumInt


class Card(ImmutableDotDict):
    """Playing card structure.

    Class Properties:
        :type Suit: EnumInt -- Enumerated card Suit types.
        :type Value: EnumInt -- Enumerated card values.

    Init Parameters:
        card_or_suit -- The card dict or the suit of the card.
        value -- If suit provided, the face value of the card.

    Properties:
        :type suit: Card.Value/int -- The suit of the card.
        :type value: Card.Suit/int -- The card face value.
    """

    Suit = EnumInt('DIAMONDS', 'CLUBS', 'HEARTS', 'SPADES')

    Value = EnumInt('JOKER', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN',
                    'EIGHT', 'NINE', 'TEN', 'JACK', 'QUEEN', 'KING', 'ACE')

    def __init__(self, card_or_suit, value=None):
        """Card init.

        :param card_or_suit: Card.Suit/int | dict -- The card dict or the
            suit of the card.
        :param value: Card.Value/int | None -- If suit provided, the face
            value of the card.
        """
        if not value:
            super(Card, self).__init__(card_or_suit)
        else:
            super(Card, self).__init__({
                'suit': card_or_suit,
                'value': value
            })

    def __setattr__(self, key, value):
        if hasattr(self, key):
            raise ValueError('Card object cannot be changed once assigned.')
        super(Card, self).__setattr__(key, value)



