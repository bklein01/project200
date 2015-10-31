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

    Init Keyword Parameters:
        suit -- The suit of the card.
        value -- The face value of the card.
        card -- The card dict, rather than individual suit and value.

    Properties:
        :type suit: Card.Value/int -- The suit of the card.
        :type value: Card.Suit/int -- The card face value.
    """

    Suit = EnumInt('DIAMONDS', 'CLUBS', 'HEARTS', 'SPADES')

    Value = EnumInt('JOKER', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN',
                    'EIGHT', 'NINE', 'TEN', 'JACK', 'QUEEN', 'KING', 'ACE')

    def __init__(self, **kwargs):
        """Card init.

        :param suit: Card.Suit/int -- The card suit.
        :param value: Card.Value/int -- The card face value.
        """
        if 'card' in kwargs:
            super(Card, self).__init__(kwargs['card'])
        elif 'value' in kwargs and 'suit' in kwargs:
            super(Card, self).__init__({
                'suit': kwargs['suit'],
                'value': kwargs['value']
            })
        else:
            raise InitError('Card requires either card or suit,value args.')

    def __setattr__(self, key, value):
        if hasattr(self, key):
            raise ValueError('Card object cannot be changed once assigned.')
        super(Card, self).__setattr__(key, value)



