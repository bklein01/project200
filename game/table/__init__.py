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

    State = Enum('CREATED', 'BETTING', 'PLAYING', 'PAUSED', 'END')

    # noinspection PyCallByClass,PyTypeChecker,PyMethodParameters
    @classproperty
    def MODEL_RULES(cls):
        rules = super(Table, cls).MODEL_RULES
        rules.update({
            'deck': ('deck', DataModel,
                     lambda x: x.model if x else DataModel.Null),
            'players': ('players', list, None),
            'kitty': ('kitty', Collection.List,
                      lambda x: dict(x) if x else None),
            'active_cards': ('active_cards', Collection.List,
                       lambda x: dict(x) if x else None),
            'discards': ('discards', Collection.Dict(DataModel),
                         lambda x: x.model if x else DataModel.Null),
            'state': ('state', str, None),
            'betters': ('betters', Collection.List(int), None),
            'player_turn': ('player_turn', int, None),
            'bet_amount': ('bet_amount', int, None),
            'bet_team': ('bet_team', str, lambda x: 'None' if x is None else x),
            'trump_suit': ('trump_suit', int, None),
            'round_start_player': ('round_start_player', int, None),
            'round': ('round', int, None),
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
            'state': Table.State.CREATED,
            'player_turn': 1,
            'round_start_player': 1,
            'bet_team': '',
            'betters': [0, 1, 2, 3],
            'bet_amount': 0,
            'trump_suit': 0,
            'round': 1,
            '_prev_state': None
        })
        return defaults

    # noinspection PyMethodOverriding
    @classmethod
    def new(cls, players, deck, data_store, **kwargs):
        kwargs.update({'players': players,
                  'deck': deck,
                  'discards': {
                      'A': CardHolder.new(None, data_store, sort_method='value'),
                      'B': CardHolder.new(None, data_store, sort_method='value')
                  }
        })
        ctrl = super(Table, cls).new(data_store, **kwargs)
        return ctrl

    # noinspection PyMethodOverriding
    @classmethod
    def restore(cls, data_model, data_store, **kwargs):
        ctrl = data_store.get_controller(cls, data_model.uid)
        if ctrl:
            return ctrl
        kwargs.update({
            'discards': {
                'A': CardHolder.restore(data_model.discards['A'], data_store),
                'B': CardHolder.restore(data_model.discards['B'], data_store)},
            'kitty': [Card(c) if c else None for c in data_model.kitty],
            'active_cards':
                [Card(c) if c else None for c in data_model.active],
            'state': data_model.state,
            'player_turn': data_model.player_turn,
            'bet_team': data_model.bet_team,
            'bet_amount': data_model.bet_amount,
            '_prev_state': data_model['_prev_state'],
            'trump_suit': data_model.trump_suit,
            'round_start_player': data_model.round_start_player,
            'round': data_model.round,
            'deck': Deck.restore(data_model.deck, data_store),
            'players': data_model.players
        })
        super(Table, cls).restore(data_model, data_store, **kwargs)

    def restart(self):
        if self.state is not Table.State.END:
            raise StateError("Cannot restart a game from state: " + self.state)
        self.state = Table.State.CREATED
        self.round += 1
        self.deck.rebuild(self.dicsards['A'], self.discards['B'])
        self._update_model('deck')
        self._update_model('discards')
        self.kitty = [None] * 4,
        self.active_cards = [None] * 4
        self.betters = [0, 1, 2, 3]
        self.bet_team = '',
        self.bet_amount = 0,
        self.trump_suit = 0,
        self.round_start_player = self.round % 4
        self.setup()

    def setup(self):
        if self.state is not Table.State.CREATED:
            raise StateError('Table must be CREATED to be setup.')
        self.deck.shuffle()
        self.kitty = self.deck.deal(4)
        while self.deck.has_cards:
            for pid in self.players:
                card = self.deck.deal()
                Player.get(pid, self._data_store).hand.insert_card(card)
        self._update_model('deck')
        self.state = Table.State.BETTING
        self.player_turn = self.round_start_player

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

    def next_turn(self, add=1):
        next_turn = (self.player_turn + add) % len(self.players)
        if self.state is Table.State.BETTING and len(self.betters) is 1:
            self._end_betting()
        elif self.state is Table.State.BETTING and next_turn not in self.betters:
            self.next_turn(add + 1)
        elif (self.state is Table.State.PLAYING and
                next_turn is self.round_start_player):
            self._end_round()
        else:
            self.player_turn = next_turn

    def bet(self, player_id, amount):
        if (self.state is not Table.State.BETTING or
                player_id is not self.players[self.player_turn]):
            raise StateError("It is not the player's turn to bet.")
        if not amount:
            i = self.betters.index(self.player_turn)
            del self.betters[i]
            self._update_model_collection('betters', {'action': 'remove',
                                                      'index': i})
        elif (amount % 5) is not 0:
            raise ValueError("Amount must be a multiple of 5.")
        elif amount <= self.bet_amount:
            raise ValueError("Amount cannot be less than current bid.")
        else:
            self.bet_amount = amount
        self.next_turn()

    def play_card(self, player_id, card):
        if not self.trump_suit:
            raise StateError("Cannot play card before trump suit is set.")
        if (self.state is not Table.State.PLAYING or
                player_id is not self.players[self.player_turn]):
            raise StateError("It is not the player's turn to play a card.")
        p = Player.get(player_id, self._data_store)
        if p:
            c = p.hand.remove_card(card)
        if not p or not c:
            raise ValueError("Invalid player or card supplied to play_card.")
        self.active_cards[self.player_turn] = c
        self._update_model('active_cards')
        self.next_turn()

    def set_trump_suit(self, player_id, suit):
        if (self.state is not Table.State.PLAYING or
                player_id is not self.players[self.player_turn] or
                player_id is not self.players[self.round_start_player] or
                self.trump_suit is not 0):
            raise StateError("It is not the player's turn to pick a trump suit.")
        self.trump_suit = suit

    def _end_betting(self):
        self.round_start_player = self.betters[0]
        p = Player.get(self.players[self.betters[0]], self._data_store)
        self.bet_team = p.team
        for c in self.kitty:
            p.hand.insert_card(c)
        self.kitty = [None] * 4
        self.state = Table.State.PLAYING
        self.player_turn = self.round_start_player

    def _end_round(self):
        high_card = self.active_cards[self.round_start_player]
        suits = [high_card.suit, self.trump_suit]
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
        if not winner.hand.card_count:
            self.state = Table.State.END
        else:
            self.round_start_player = index
            self.player_turn = index


# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
