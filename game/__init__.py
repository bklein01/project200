"""Main Game package.

.. packageauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class Game -- The main game controller.

"""

from combomethod import combomethod
from core.datamodel import DataModelController, Collection, DataModel
from core.dotdict import DotDict
from core.enum import Enum
from core.exceptions import StateError
from game.thdeck import THDeckOriginal, THDeckSixes
from game.table import Table
from game.player import Player, Spectator
from game.deck.card import Card
from core.decorators import classproperty


# noinspection PyAttributeOutsideInit
class Game(DataModelController):
    """Main Game controller class.

    Class Properties:
        :type State: Enum -- Game state enumerated values.
        :type SpecMode: Enum -- Spectator mode option values.
        :type DEFAULT_OPTIONS: DotDict -- Game option defaults.
        :type MODEL_RULES: dict -- Rule set for underlying `DataModel`.

    Class Methods:
        load -- Load new Game object from existing DataModel.
        get -- Load new Game object from existing game_id.

    New Parameters:
        creating_user -- The user that created the game room.
        data_store -- The DataStore controller.
        options -- Optional keyword options to override the defaults.

    Properties:
        :type options: dict -- List of game options.
        :type creator: User -- The user that created the game room.
        :type players: list -- List of active `Player` ids.
        :type points: dict -- Score sheet for current game.
        :type table: Table -- The game table.
        :type state: Game.State/str -- The current game state.
        :type spectators: list -- List of active `Spectator` ids.

    Public Methods:
        new_game -- Start a new game to `options.win_amount` points.
        remove_player -- Remove player from game.
        remove_player_by_user_id -- Remove player by the user_id.
        add_player -- Add new player to game.
        add_spectator -- Add new spectator to game.
        remove_spectator -- Remove spectator from the game.
        remove_spectator_by_user_id -- Remove spectator by user_Id.

    """

    State = Enum('CREATED', 'READY', 'RUNNING', 'PAUSED', 'END')
    SpecMode = Enum('NOSPEC', 'STANDARD', 'ACTIVE', 'ALL')

    DEFAULT_OPTIONS = {
        'sixes': False,
        'spec_mode': 'STANDARD',
        'spec_allow_chat': True,
        'spec_max': 4,
        'win_amount': 200
    }

    # noinspection PyCallByClass,PyTypeChecker,PyMethodParameters
    @classproperty
    def MODEL_RULES(cls):
        rules = super(Game, cls).MODEL_RULES
        rules.update({
            'players': ('players', Collection.List(DataModel),
                        lambda x: x.model if x else DataModel.Null),
            'state': ('state', str, None),
            'table': ('table', DataModel, lambda x: x.model if x else DataModel.Null),
            'points': ('points', Collection.Dict(int), None),
            'spectators': ('spectators', Collection.List(DataModel),
                           lambda x: x.model if x else DataModel.Null),
            'options': ('options', Collection.Dict, None)
        })
        return rules

    # noinspection PyCallByClass,PyTypeChecker,PyMethodParameters
    @classproperty
    def INIT_DEFAULTS(cls):
        defaults = super(Game, cls).INIT_DEFAULTS
        defaults.update({
            'players': [None] * 4,
            'spectators': [],
            'state': Game.State.CREATED,
            'points': {'A': 0, 'B': 0},
            'options': DotDict(Game.DEFAULT_OPTIONS),
            'table': None
        })
        return defaults

    # noinspection PyMethodParameters
    @combomethod
    def delete_cache(rec, data_store, uid=None):
        if isinstance(rec, Game):
            for p in rec.players:
                if p:
                    p.delete_cache(data_store)
            for s in rec.spectators:
                s.delete_cache(data_store)
            if rec.table:
                rec.table.delete_cache(data_store)
        super(Game, rec).delete_cache(data_store, uid)

    # noinspection PyMethodParameters
    @combomethod
    def delete(rec, data_store, uid=None):
        """Delete controller members before deleting self."""
        if isinstance(rec, Game):
            for p in rec.players:
                if p:
                    p.delete(data_store)
            for s in rec.spectators:
                s.delete(data_store)
            if rec.table:
                rec.table.delete(data_store)
        super(Game, rec).delete(data_store, uid)

    # noinspection PyMethodOverriding
    @classmethod
    def new(cls, creating_user, data_store, options=None, **kwargs):
        if not options:
            options = {}
        ctrl = super(Game, cls).new(data_store, **kwargs)
        ctrl.options.update(options)
        ctrl.add_player(creating_user, 0)
        return ctrl

    # noinspection PyMethodOverriding
    @classmethod
    def restore(cls, data_store, data_model):
        kwargs = {
            'players':
                [Player.restore(data_store, x) if x is not DataModel.Null
                 else None for x in data_model.players],
            'spectators':
                [Spectator.restore(data_store, x)
                 for x in data_model.spectators],
            'state': data_model.state,
            'table': (Table.restore(data_store, data_model.table)
                      if data_model.table is not DataModel.Null else None),
            'points': data_model.points,
            'options': DotDict(data_model.options)
        }
        return super(Game, cls).restore(data_store, data_model, **kwargs)

    def active_players(self, team=None):
        if team:
            len([1 for p in self.players
                 if p and p.team == team and not p.abandoned])
        return len([1 for p in self.players if p and not p.abandoned])

    def new_game(self):
        """Start a new game.

        :raise: StateError if `Game` is not `Ready`.
        """
        if self.state not in (Game.State.READY, Game.State.END):
            raise StateError("Cannot start game while in state: " + self.state)
        if self.options.sixes:
            deck = THDeckSixes.new(self._data_store)
        else:
            deck = THDeckOriginal.new(self._data_store)
        self.points = {'A': 0, 'B': 0}
        self.table = Table.new([p.uid for p in self.players],
                               deck, self._data_store)
        self.table.on_change('*', (
            lambda model, key, instruction:
                self._call_listener(
                    'table', instruction, {'property': key})))
        self.table.on_change('state', (
            lambda model, key, instruction:
                self._table_round_end(model)
                if model.state is Table.State.END else 0))
        self.table.setup()
        self.state = Game.State.RUNNING

    def _table_round_end(self, model):
        scores = {
            'A': _points_calc(model.discards['A'].cards),
            'B': _points_calc(model.discards['B'].cards)
        }
        if scores[model.bet_team] >= model.bet_amount:
            # bet round win
            for p in self.players:
                if p.team is model.bet_team:
                    p.statistics.won_bet_round(model.bet_amount)
                else:
                    p.statistics.lost_counter_round()
            self._update_points(**scores)
        else:
            # counter round win
            s = scores[model.bet_team]
            for p in self.players:
                if p.team is model.bet_team:
                    p.statistics.lost_bet_round()
                else:
                    p.statistics.won_counter_round(100 - s)
            scores[model.bet_team] = -1 * model.bet_amount
            self._update_points(**scores)
        if self.points['A'] >= self.options.win_amount:
            self._end_game('A')
        elif self.points['B'] >= self.options.win_amount:
            self._end_game('B')
        else:
            self.table.restart()

    def _end_game(self, winning_team):
        losing_team = 'B' if winning_team is 'A' else 'A'
        teams = {
            'A': [p for p in self.players if p.team is 'A'],
            'B': [p for p in self.players if p.team is 'B']
        }
        elos = {
            'A': _avg_elo(*teams['A']),
            'B': _avg_elo(*teams['B'])
        }
        for i in xrange(2):
            teams[winning_team][i].statistics.update_casual_game_stats(
                self.uid, teams[winning_team][(i + 1) % 2].uid,
                elos[losing_team], True)
            teams[losing_team][i].statistics.update_casual_game_stats(
                self.uid, teams[losing_team][(i + 1) % 2].uid,
                elos[winning_team], False)
        self.state = Game.State.END

    def remove_player(self, p):
        """Removes player from game.

        :param p: Player -- The `Player` to remove.
        """
        if self.state in (Game.State.RUNNING, Game.State.PAUSED):
            p.abandoned = True
            self._update_model('players')
            self.table.pause()
            self.state = Game.State.PAUSED
        elif self.state in (Game.State.READY, Game.State.END,
                            Game.State.CREATED):
            index = self.players.index(p)
            self.players[index] = None
            p.delete(self._data_store)
            self._update_model_collection('players', {'action': 'remove',
                                                      'index': index})
            self.state = Game.State.CREATED

    def remove_player_by_user_id(self, user_id):
        """Remove player from game by `User.user_id`.

        :param user_id: str -- The ID of the user to remove.
        :raise: ValueError if user is not a player.
        """
        for p in self.players:
            if p and p.user.uid == user_id and not p.abandoned:
                return self.remove_player(p)
        raise ValueError("User is not a player in this game.")

    def add_player(self, user, slot):
        """Add a player to the game.

        :param user: User -- The player's `User` object.
        :param team: str -- The team to join ('A' or 'B').
        :raise: ValueError if `Game` is not in a state to add players, or the
            table is already full.
        """
        if slot not in range(4):
            raise ValueError("Invalid player slot provided.")
        if self.players[slot] and not self.players[slot].abandoned:
            raise ValueError("Slot is taken. Cannot add player.")
        for p in self.players:
            if p and not p.abandoned and p.user.uid is user.uid:
                raise ValueError("User already apart of game.")
        team = 'A' if slot in (0, 2) else 'B'
        if self.state is Game.State.CREATED:
            self.players[slot] = Player.new(user, team, self._data_store)
            self._update_model('players')
            if self.active_players() == 4:
                self.state = Game.State.READY
        elif self.state is Game.State.PAUSED and self.players[slot].abandoned:
            self.players[slot].new_user(user)
            self._update_model('players')
            if self.active_players() == 4:
                self.state = Game.State.RUNNING
                self.table.resume()
        # should never get here

    def add_spectator(self, user):
        """Add a spectator to the game.

        :param user: User -- The spectator's `User` object.
        :raise: ValueError if `Game` does not allow spectators, or spectator
            slots have been filled.
        """
        if self.options.spec_mode is Game.SpecMode.NOSPEC:
            raise ValueError("This game does not allow spectators.")
        if len(self.spectators) >= self.options.spec_max:
            raise ValueError("This game has reached the max allowed "
                             "spectators.")
        self.spectators.append(Spectator(user))
        self._update_model_collection('spectators', {'action': 'append'})

    def remove_spectator(self, spec):
        """Remove spectator from game.

        :param spec: Spectator -- The spectator to remove.
        """
        index = self.spectators.index(spec)
        self.spectators.remove(spec)
        self._update_model_collection('spectators', {'action': 'remove',
                                                     'index': index})
        Spectator.delete(spec.uid, self._data_store)

    def remove_spectator_by_user_id(self, user_id):
        """Remove spectator from game by `User.user_id`.

        :param user_id: int -- The ID of the user to remove.
        :raise: ValueError if the user is not a spectator in the game.
        """
        for spec in self.spectators:
            if spec.user.uid == user_id:
                return self.remove_spectator(spec)
        raise ValueError("User is not a spectator in this game.")


def _points_calc(cards):
    """Calculate team score from discard pile.

    Counts 5 points for every `FIVE` and 10 points for every `ACE` or `TEN`.

    :param cards: The team's discard pile.
    :return: int -- Team's final score.
    """
    return sum([5 if c.value is Card.Value.FIVE else
                10 if c.value in (Card.Value.TEN, Card.Value.ACE) else
                0 for c in cards])


def _avg_elo(*args):
    """Calculates the average (weighted) elo for one or more players."""
    elo = 0.0
    games = 0
    for p in args:
        _games = p.statistics.games_won + p.statistics.games_lost
        elo += p.statistics.elo * _games
        games += _games
    return elo / games


# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
