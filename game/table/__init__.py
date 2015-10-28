"""Game table package.

.. packageauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:


"""

from core.datamodel import DataModelController, DataModel, Collection
from core.enum import Enum
from core.exceptions import StateError
from game.deck import CardHolder


class Table(DataModelController):

    State = Enum('Betting', 'Playing', 'Paused')

    # noinspection PyCallByClass,PyTypeChecker
    MODEL_RULES = {
        'deck': ('deck', DataModel, lambda x: x.model),
        'players': ('players', list, None),
        'flops': ('flops', Collection.List, lambda x: x.model),
        'discards': ('discards', Collection.Dict(DataModel), lambda x: x.model),
        'game_id': ('game_id', int, None),
        'state': ('state', str, None),
        'player_turn': ('player_turn', int, None),
        'bet_amount': ('bet_amount', int, None),
        'bet_team': ('bet_team', str, lambda x: 'None' if x is None else x)
    }

    def __init__(self, game_id, players, deck):
        self.game_id, self.deck = game_id, deck
        self.players = [player.player_id for player in players]
        self.flops = [None] * 4
        self.discards = {
            'A': CardHolder(None, 'value'),
            'B': CardHolder(None, 'value')
        }
        self.bet_team, self.bet_amount = None, 0
        self.state, self.player_turn = Table.State.Betting, self.players[0]
        self._prev_state = None
        super(Table, self).__init__(self.__class__.MODEL_RULES)

    def pause(self):
        self._prev_state = self.state
        self.state = Table.State.Paused

    def resume(self):
        if not self._prev_state:
            raise StateError("Cannot resume to unknown state.")
        self.state = self._prev_state
        self._prev_state = None


# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
