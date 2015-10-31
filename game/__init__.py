"""Main Game package.

.. packageauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class Game -- The main game controller.

"""

from core.datamodel import DataModelController, Collection, DataModel
from core.dotdict import ImmutableDotDict, DotDict
from core.enum import Enum
from core.exceptions import StateError
from game.thdeck import THDeckOriginal, THDeckSixes
from game.table import Table
from game.player import Player, Spectator
from core.decorators import classproperty
from store import ModelStore as DataStore


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

    State = Enum('CREATED', 'READY', 'RUNNING', 'PAUSED')
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
            'players': ('players', Collection.List(DataModel), lambda x: x.model),
            'state': ('state', str, None),
            'table': ('table', DataModel, lambda x: x.model),
            'points': ('points', Collection.Dict(int), None),
            'spectators': ('spectators', Collection.List(DataModel),
                           lambda x: x.model),
            'options': ('options', Collection.Dict, lambda x: dict(x))
        })
        return rules

    # noinspection PyCallByClass,PyTypeChecker,PyMethodParameters
    @classproperty
    def INIT_DEFAULTS(cls):
        defaults = super(Game, cls).INIT_DEFAULTS
        defaults.update({
            'players': [],
            'spectators': [],
            'state': Game.State.CREATED,
            'points': {'A': 0, 'B': 0},
            'options': DotDict(Game.DEFAULT_OPTIONS),
            'table': None
        })
        return defaults

    # noinspection PyMethodOverriding
    @classmethod
    def new(cls, creating_user, data_store, options=None, **kwargs):
        ctrl = super(Game, cls).new(data_store, **kwargs)
        ctrl.options.update(options)
        ctrl.add_player(creating_user, 'A')
        return ctrl

    # noinspection PyMethodOverriding
    @classmethod
    def restore(cls, data_model, data_store):
        ctrl = data_store.get_controller(cls, data_model.uid)
        if ctrl:
            return ctrl
        kwargs = {
            'players':
                [Player.restore(x, data_store)
                 for x in data_model.players],
            'spectators':
                [Spectator.restore(x, data_store)
                 for x in data_model.spectators],
            'state': data_model.state,
            'table': Table.restore(data_model.table, data_store),
            'points': data_model.points,
            'options': DotDict(data_model.options)
        }
        super(Game, cls).restore(data_model, data_store, **kwargs)

    def active_players(self, team=None):
        if team:
            len([1 for p in self.players
                 if p.team == team and not p.abandoned])
        return len([1 for p in self.players if not p.abandoned])

    def new_game(self):
        """Start a new game.

        :raise: StateError if `Game` is not `Ready`.
        """
        if self.state is not Game.State.READY:
            raise StateError("Cannot start game while in state: " + self.state)
        if self.options.sixes:
            deck = THDeckSixes()
        else:
            deck = THDeckOriginal()
        self.table = Table(self.players, deck)
        self.table.on_change('*', (
            lambda model, key, instruction:
                self._call_listener('table', instruction, {'property': key})))
        self.state = Game.State.RUNNING

    def remove_player(self, p):
        """Removes player from game.

        :param p: Player -- The `Player` to remove.
        """
        if self.state is Game.State.RUNNING:
            p.abandoned = True
            self.table.pause()
            self.state = Game.State.PAUSED
        elif self.state is Game.State.READY:
            index = self.players.index(p)
            self.players.remove(p)
            Player.delete(p.uid, self._data_store)
            self._update_model_collection('players', {'action': 'remove',
                                                      'index': index})
            self.state = Game.State.CREATED

    def remove_player_by_user_id(self, user_id):
        """Remove player from game by `User.user_id`.

        :param user_id: int -- The ID of the user to remove.
        :raise: ValueError if user is not a player.
        """
        for p in self.players:
            if p.user.uid == user_id:
                return self.remove_player(p)
        raise ValueError("User is not a player in this game.")

    def add_player(self, user, team):
        """Add a player to the game.

        :param user: User -- The player's `User` object.
        :param team: str -- The team to join ('A' or 'B').
        :raise: ValueError if `Game` is not in a state to add players, or the
            table is already full.
        """
        if self.active_players() == 4:
            raise ValueError("Game is full. Cannot add player.")
        if self.active_players(team) == 2:
            raise ValueError("Team `" + team + "` is full. Cannot add player.")
        if self.state is Game.State.CREATED:
            self.players.append(Player(user, team))
            if self.active_players() == 4:
                self.state = Game.State.READY
        elif self.state is Game.State.PAUSED:
            for p in self.players:
                if p.abbandoned and p.team is team:
                    p.new_user(user)
                    if self.active_players() == 4:
                        self.state = Game.State.Running
                        self.table.resume()
                    break
        else:
            raise StateError("Cannot add new player in state: " + self.state)

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

# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
