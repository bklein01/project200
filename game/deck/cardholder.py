"""Card holder.

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class CardHolder -- The basic card container M/C.

"""

import random
from core.datamodel import (Collection, DataModel, DataModelController)
from core.decorators import classproperty
from game.deck.card import Card


# noinspection PyStatementEffect
class CardHolder(DataModelController):
    """Card container.

    Class Properties:
        :type MODEL RULES: dict -- The DataModel rule set.
        :type SORT_COMP_METHODS: dict -- Sort methods.

    Init Parameters:
        cards -- Optional list of cards to init with.
        sort_method -- Optional method with which to sort cards.
        ascending_order -- Ascending/descending sort option.

    Properties:
        :type self.cards: list -- List of held cards.
        :type self.sort_method: str | None -- The name of the sort method to use.
        :type self.sort_ascend: bool -- Whether to sort in ascending order.
        :type self.card_count: int -- The number of cards currently held.

    Public Methods:
        change_sort -- Update sorting rules.
        add_card -- Create new card and insert it if sort_method defined,
            otherwise append it to card list.
        append_card -- Append new card to card list.
        insert_card -- Insert new card into sorted/specified order.
        sort -- Sort entire card list.
        shuffle -- Shuffle entire card list.
        dump_cards -- Dump entire card list.

    """

    # noinspection PyPep8Naming,PyMethodParameters,PyCallByClass,PyTypeChecker
    @classproperty
    def MODEL_RULES(cls):
        """The rule set for the underlying `DataModel`.

        New Model Keys:
            :key cards: Collection.List(DataModel) -- The list of cards.
            :key sort: str | None -- The sorting compare method name.
            :key ascend: bool -- Sorting option for ascending order.
        """
        return {
            'cards': ('cards', Collection.List(DataModel), lambda x: x.model),
            'sort': ('sort_method', None, None),
            'ascend': ('sort_ascend', bool, None)
        }

    SORT_COMP_METHODS = {
        'suit':
            (lambda a, b: -1 if a.suit < b.suit
                else 1 if a.suit > b.suit
                else -1 if a.value < b.value
                else 1 if a.value > b.value
                else 0),
        'value':
            (lambda a, b: -1 if a.value < b.value
                else 1 if a.value > b.value
                else -1 if a.suit < b.suit
                else 1 if a.suit > b.suit
                else 0)
    }

    def __init__(self, cards=None, sort_method=None, ascending_order=False):
        """CardHolder init.

        :param cards: list -- Optional list of cards to init with.
        :param sort_method: str -- Optional method with which to sort cards.
        :param ascending_order: bool -- Ascending/descending sort option.
        """
        if cards is None:
            cards = []
        self.cards = cards
        self.sort_method, self.sort_ascend = sort_method, ascending_order
        super(CardHolder, self).__init__(self.__class__.MODEL_RULES)

    @property
    def card_count(self):
        return len(self.cards)

    def add_card(self, suit, value):
        """Create and add new card to holder.

        If sort_method defined, new card will be inserted in sorted order.
        Otherwise, it will be appended to the end of the card list.

        :param suit: Card.Suit/int
        :param value: Card.Value/int
        :return: int -- The index of the newly added card.
        """
        card = Card(suit, value)
        if self.sort_method:
            return self.insert_card(card)
        return self.append_card(card)

    def change_sort(self, new_method=None, ascending=None):
        """Modify sort method and re-sort cards.

        :param new_method: str -- Optional new sorting method to use.
        :param ascending: bool - Ascending/descending sort option.
        """
        changed = False
        if new_method:
            self.sort_method = self.__class__.SORT_COMP_METHODS[new_method]
            changed = True
        if ascending is not None:
            changed = True
            self.sort_ascend = ascending
        if changed:
            self.sort()

    def remove_card(self, card):
        if type(card) is int:
            card = self.cards.index(card)
        if not card:
            raise ValueError("Card not found in holder.")
        self.cards.remove(card)

    def append_card(self, card):
        """Add card to end of cards holder. Does not sort.

        :param card: Card -- The card object to add.
        """
        self.cards.append(card)
        self._update_model_collection('cards', {'action': 'append'})
        return self.card_count - 1

    def insert_card(self, card, index=None):
        """Insert card in specified index, or sorted order.

        If no index supplied, card will be inserted in the predefined sorted
        order, which assumes the holder is already sorted.

        :param card: Card -- The card object to insert
        :return: int -- The index of the new card.
        """
        if not self.card_count:
            return self.append_card(card)
        if index is None:
            if not self.sort_compare:
                raise IndexError("No compare method set for CardHolder. "
                                 "Index required.")
            index = 0
            comp = self.__class__.SORT_COMP_METHODS[self.sort_compare]
            comp_val = 1 if self.sort_ascend else -1
            while comp(card, self.cards[index]) == comp_val:
                index += 1
        self.cards.insert(index, card)
        self._update_model_collection('cards', {'action': 'insert',
                                                'index': index})
        return index

    def sort(self):
        """Sorts cards list."""
        if not self.compare:
            raise AttributeError("No compare method set for CardHolder; "
                                 "cannot sort.")
        self.cards.sort(self.__class__.SORT_COMP_METHODS[self.sort_compare])
        self._update_model('cards')

    def shuffle(self):
        """Shuffle cards list."""
        random.shuffle(self.cards)
        self._update_model('cards')

    def dump_cards(self):
        """Dump cards list.

        :return: list -- Dumped cards.
        """
        cards = self.cards
        self.cards = []
        return cards

    def __iter__(self):
        return (card for card in self.cards)



