"""Card holder.

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:

"""

from core.datamodel import (
    Collection, DataModel, DataModelController, classproperty)


# noinspection PyStatementEffect
class CardHolder(DataModelController):

    # noinspection PyPep8Naming,PyMethodParameters,PyCallByClass,PyTypeChecker
    @classproperty
    def MODEL_RULES(cls):
        return {
            'cards': ('cards', Collection.List(DataModel), lambda x: x.model),
            'sort': ('sort_method', str)
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

    def change_sort(self, new_method=None, ascending=None):
        """Modify sort method and re-sort cards.

        :param new_method: str -- Optional new sorting method to use.
        :param ascending: bool - Ascending/descending sort option.
        """
        changed = False
        if new_method:
            self.sort['compare'] = self.__class__.SORT_COMP_METHODS[new_method]
            changed = True
        if ascending is not None:
            changed = True
            self.sort['ascending'] = ascending
        if changed:
            self.sort()

    def append_card(self, card):
        """Add card to end of cards holder. Does not sort.

        :param card: Card -- The card object to add.
        """
        self.cards.append(card)
        self._update_model_collection('cards', {'action': 'append'})

    def insert_card(self, card):
        """Insert card in sorted order. (Assumes pre-sorted list).

        :param card:
        :return:
        """
