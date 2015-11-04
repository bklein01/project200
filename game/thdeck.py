"""The Two-Hundred (200) Game Playing Decks.

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class THDeckOriginal -- The original 200 card deck.
    :class THDeckSixes -- The 200 card deck with sixes.

"""

from game.deck import Deck
from game.deck.card import Card
from core.decorators import classproperty


class THDeckSixes(Deck):
    """Two-Hundred (200) game deck with sixes."""

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    def DEFAULT_DECK(cls):
        std_deck = super(THDeckSixes, cls).DEFAULT_DECK
        for suit in Card.Suit:
            std_deck[suit] = [c for c in std_deck[suit]
                              if c not in [Card.Value.TWO,
                                           Card.Value.THREE,
                                           Card.Value.FOUR]]
        return std_deck


class THDeckOriginal(THDeckSixes):
    """Two-Hundred (200) original game deck."""

    # noinspection PyMethodParameters,PyPep8Naming
    @classproperty
    def DEFAULT_DECK(cls):
        std_deck = super(THDeckOriginal, cls).DEFAULT_DECK
        for suit in Card.Suit:
            std_deck[suit].remove(Card.Value.SIX)
        return std_deck

