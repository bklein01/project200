"""Game table package.

.. packageauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class Table -- The game table.
    :Enum Table.State -- The game table states.

"""

from core.datamodel import DataModelController, DataModel, Collection
from core.enum import Enum
from core.exceptions import StateError
from game.deck import CardHolder


class Table(DataModelController):
    """Game table.

    Class Properties:
        :type State: Enum -- Enumerated table state types.
        :type MODEL_RULES: dict -- Rule set for underlying `DataModel`.

    Init Parameters:
        game_id -- The unique ID of the parent Game object.
        players -- The list of players.
        deck -- The game deck.

    Properties:
        :type game_id: -- The unique ID of the parent Game object.
        :type kitty: list -- The table's kitty (extra cards for highest bidder).
        :type active: list -- The cards played for each round.
        :type players: list -- Table's player IDs.
        :type discards: dict -- The team's discard piles.
        :type bet_team: str -- The team with the highest/winning bid.
        :type bet_amount: int -- The highest/winning bid.
        :type deck: Deck -- The table's card deck.
        :type state: Table.State/str -- The table state.
        :type player_turn: int -- The ID of the player who's turn it is.

    Public Methods:
        pause -- Pauses the gameplay.
        resume -- Resumes the gameplay.

    """

    State = Enum('Betting', 'Playing', 'Paused')

    # noinspection PyCallByClass,PyTypeChecker
    MODEL_RULES = {
        'deck': ('deck', DataModel, lambda x: x.model),
        'players': ('players', list, None),
        'kitty': ('kitty', Collection.List, lambda x: x.model),
        'active': ('active', Collection.List, lambda x: x.model),
        'discards': ('discards', Collection.Dict(DataModel), lambda x: x.model),
        'game_id': ('game_id', int, None),
        'state': ('state', str, None),
        'player_turn': ('player_turn', int, None),
        'bet_amount': ('bet_amount', int, None),
        'bet_team': ('bet_team', str, lambda x: 'None' if x is None else x)
    }

    def __init__(self, game_id, players, deck):
        """Table init.

        :param game_id: int -- The unique ID of the parent Game object.
        :param players: list -- List of game `Player`s.
        :param deck: Deck -- The game deck.
        """
        self.game_id, self.deck = game_id, deck
        self.players = [player.player_id for player in players]
        self.kitty, self.active = [None] * 4, [None] * 4
        self.discards = {
            'A': CardHolder(None, 'value'),
            'B': CardHolder(None, 'value')
        }
        self.bet_team, self.bet_amount = None, 0
        self.state, self.player_turn = Table.State.Betting, self.players[0]
        self._prev_state = None
        super(Table, self).__init__(self.__class__.MODEL_RULES)

    def pause(self):
        """Pause the game."""
        self._prev_state = self.state
        self.state = Table.State.Paused

    def resume(self):
        """Resume the game.

        :raise: StateError if resume called with no previous state.
        """
        if not self._prev_state:
            raise StateError("Cannot resume to unknown state.")
        self.state = self._prev_state
        self._prev_state = None


# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
