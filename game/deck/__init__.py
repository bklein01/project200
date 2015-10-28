"""Game card deck package.

.. packageauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class Deck
    :module cardholder
    :module card

"""

from core.decorators import classproperty
from game.deck.cardholder import CardHolder
from game.deck.card import Card


class Deck(CardHolder):
    """Card deck.

    Class Properties:
        :type DEFAULT_DECK: dict -- The default cards with which to initialize
            the deck.

    Init Parameters:
        cards -- Optional list of cards to use instead of the default.

    Public Methods:
        deal -- Deals one or more cards off the deck.

    Private Methods:
        _pop_card -- Pops a card off the card list.

    """

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    def DEFAULT_DECK(cls):
        return {
            Card.Suit.SPADES: [value for value in Card.Value
                               if value is not Card.Value.JOKER],
            Card.Suit.HEARTS: [value for value in Card.Value
                               if value is not Card.Value.JOKER],
            Card.Suit.CLUBS: [value for value in Card.Value
                              if value is not Card.Value.JOKER],
            Card.Suit.DIAMONDS: [value for value in Card.Value
                                 if value is not Card.Value.JOKER]
        }

    def __init__(self, cards=None):
        """Deck init.

        :param cards: list | None - Optional list of cards to init with.
        """
        if cards is None:
            default = self.__class__.DEFAULT_DECK
            cards = []
            for suit in Card.Suit:
                cards += [Card(suit, val) for val in default[suit]]
        super(Deck, self).__init__(cards)
        self.shuffle()

    def _pop_card(self):
        """Pop card of top of deck.

        :return: Card -- The popped card.
        """
        if not self.card_count:
            raise IndexError("Cannot deal card from empty deck.")
        index = self.card_count - 1
        self._update_model_collection('cards', {'action': 'remove',
                                                'index': index})
        return self.cards.pop()

    def deal(self, count=1):
        """Deal one or more cards from deck.

        :param count: int -- The amount of cards to deal.
        :return: Card | list -- A popped card if count is 1, otherwise a list
            of popped cards.
        """
        if count is 1:
            return self._pop_card()
        return [self._pop_card() for _ in xrange(count - 1)]

# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
