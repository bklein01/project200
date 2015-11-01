"""Game table package.

.. packageauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class Table -- The game table.
    :Enum Table.State -- The game table states.

"""

from core.datamodel import DataModelController, DataModel, Collection
from core.enum import Enum
from core.exceptions import StateError
from core.decorators import classproperty
from game.deck import CardHolder, Deck, Card
from game.player import Player


# noinspection PyAttributeOutsideInit
class Table(DataModelController):
    """Game table.

    Class Properties:
        :type State: Enum -- Enumerated table state types.

    New Parameters:
        players -- The list of players.
        deck -- The game deck.

    Properties:
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

    State = Enum('BETTING', 'PLAYING', 'PAUSED', 'END')

    # noinspection PyCallByClass,PyTypeChecker,PyMethodParameters
    @classproperty
    def MODEL_RULES(cls):
        rules = super(Table, cls).MODEL_RULES
        rules.update({
            'deck': ('deck', DataModel, lambda x: x.model),
            'players': ('players', list, None),
            'kitty': ('kitty', Collection.List,
                      lambda x: dict(x) if x else None),
            'active': ('active', Collection.List,
                       lambda x: dict(x) if x else None),
            'discards': ('discards', Collection.Dict(DataModel),
                         lambda x: x.model),
            'state': ('state', str, None),
            'bets': ('bets', Collection.List, None),
            'player_turn': ('turn', int, None),
            'bet_amount': ('bet_amount', int, None),
            'bet_team': ('bet_team', str, lambda x: 'None' if x is None else x),
            'trump_suit': ('trump_suit', int, None),
            'round_start_player': ('round_start_player', int, None),
            '_prev_state': ('_prev_state', None, None)
        })
        return rules

    # noinspection PyCallByClass,PyTypeChecker,PyMethodParameters
    @classproperty
    def INIT_DEFAULTS(cls):
        defaults = super(Table, cls).INIT_DEFAULTS
        defaults.update({
            'kitty': [None] * 4,
            'active_cards': [None] * 4,
            'state': Table.State.BETTING,
            'turn': 1,
            'round_start_player': 1,
            'bet_team': '',
            'bet_amount': 0,
            'trump_suit': 0,
            '_prev_state': None
        })
        return defaults

    # noinspection PyMethodOverriding
    @classmethod
    def new(cls, players, deck, data_store):
        kwargs = {'players': players,
                  'deck': deck,
                  'discards': {
                      'A': CardHolder.new(None, 'value', data_store),
                      'B': CardHolder.new(None, 'value', data_store)
                  }
        }
        ctrl = super(Table, cls).new(data_store, **kwargs)
        return ctrl

    # noinspection PyMethodOverriding
    @classmethod
    def restore(cls, data_model, data_store):
        ctrl = data_store.get_controller(cls, data_model.uid)
        if ctrl:
            return ctrl
        kwargs = {
            'discards': {
                'A': CardHolder.restore(data_model.discards['A'], data_store),
                'B': CardHolder.restore(data_model.discards['B'], data_store)},
            'kitty': [Card(c) if c else None for c in data_model.kitty],
            'active_cards':
                [Card(c) if c else None for c in data_model.active],
            'state': data_model.state,
            'turn': data_model.player_turn,
            'bet_team': data_model.bet_team,
            'bet_amount': data_model.bet_amount,
            '_prev_state': data_model['_prev_state'],
            'trump_suit': data_model.trump_suit,
            'round_start_player': data_model.round_start_player,
            'deck': Deck.restore(data_model.deck, data_store),
            'players': data_model.players
        }
        super(Table, cls).restore(data_model, data_store, **kwargs)

    @property
    def starting_suit(self):
        return self.active_cards[self.round_start_player].suit

    def pause(self):
        """Pause the game."""
        self._prev_state = self.state
        self.state = Table.State.PAUSED

    def resume(self):
        """Resume the game.

        :raise: StateError if resume called with no previous state.
        """
        if not self._prev_state:
            raise StateError("Cannot resume to unknown state.")
        self.state = self._prev_state
        self._prev_state = None

    def next_turn(self):
        self.player_turn = (self.player_turn + 1) % len(self.players)
        if self.player_turn is self.round_start_player:
            if self.state is Table.State.BETTING:
                pass
            elif self.state is Table.State.PLAYING:
                self._end_round()

    def play_card(self, player_id, card):
        pass

    def _end_round(self):
        suits = [self.starting_suit, self.trump_suit]
        high_card = self.active_cards[self.round_start_player]
        for c in self.active_cards:
            if c is high_card:
                continue
            if (c.suit in suits and
                (suits.index(c.suit) > suits.index(high_card.suit) or
                 (c.suit is high_card.suit and c.value > high_card.value))):
                high_card = c
        index = self.active_cards.index(high_card)
        winner = Player.get(self.players[index], self._data_store)
        for c in self.active_cards:
            self.discards[winner.team].append(c)
            self._update_model_collection('discards', {'action': 'append'})
        self.active_cards = [None] * 4
        if not winner.card_count:
            self.state = Table.State.END
        else:
            self.round_start_player = index




# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
