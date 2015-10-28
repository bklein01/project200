"""Main Game package.

.. packageauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class Game -- The main game controller.

"""

from core.datamodel import DataModelController, Collection, DataModel
from core.dotdict import DotDict
from core.enum import Enum
from core.exceptions import StateError
from game.thdeck import THDeckOriginal, THDeckSixes
from game.table import Table
from game.player import Player, Spectator
# from core.decorators import classproperty


class Game(DataModelController):
    """Main Game controller class.

    Class Properties:
        :type State: Enum -- Game state enumerated values.
        :type SpecMode: Enum -- Spectator mode option values.
        :type DEFAULT_OPTIONS: DotDict -- Game option defaults.
        :type MODEL_RULES: dict -- Rule set for underlying `DataModel`.

    Init Parameters:
        creating_user -- The user that created the game room.
        options -- Keword options to override the defaults.

    Properties:
        :type game_id: int -- The unique Game ID.
        :type options: dict -- List of game options.
        :type creator: User -- The user that created the game room.
        :type players: list -- List of active `Player`s.
        :type points: dict -- Score sheet for current game.
        :type table: Table -- The game table.
        :type state: Game.State/str -- The current game state.
        :type spectators: list -- List of active `Spectator`s.

    Public Methods:
        new_game -- Start a new game to `options.win_amount` points.
        remove_player -- Remove player from game.
        remove_player_by_user_id -- Remove player by the user_id.
        add_player -- Add new player to game.
        add_spectator -- Add new spectator to game.
        remove_spectator -- Remove spectator from the game.
        remove_spectator_by_user_id -- Remove spectator by user_Id.

    """

    State = Enum('Created', 'Ready', 'Running', 'Paused')
    SpecMode = Enum('NoSpectators', 'Standard', 'ActivePlayer', 'AllInfo')

    DEFAULT_OPTIONS = DotDict({
        'sixes': False,
        'spec_mode': 'Standard',
        'spec_allow_chat': True,
        'spec_max': 4,
        'win_amount': 200
    })

    # noinspection PyCallByClass,PyTypeChecker
    MODEL_RULES = {
        'game_id': ('game_id', int, None),
        'players': ('players', Collection.List(DataModel), lambda x: x.model),
        'owner_id': ('creator', int, lambda x: x.id),
        'state': ('state', str, None),
        'table': ('table', DataModel, lambda x: x.model),
        'points': ('points', Collection.Dict(int), None),
        'spectators': ('spectators', Collection.List(DataModel),
                       lambda x: x.model)
    }

    def __init__(self, creating_user, options=None):
        """Game init.

        :param creating_user: User -- User that created the game room.
        :param options: dict -- Optional overrides for default options.
        """
        self.game_id = id(self)  # TODO: Unique game_id generator
        self.options = self.__class__.DEFAULT_OPTIONS
        if options:
            self.options.update(options)
        self.creator = creating_user
        self.players = [Player(creating_user, 'A')]
        self.points = {'A': 0, 'B': 0}
        self.table = None
        self.state = Game.State.Created
        self.spectators = []
        super(Game, self).__init__(self.__class__.MODEL_RULES)

    def new_game(self):
        """Start a new game.

        :raise: StateError if `Game` is not `Ready`.
        """
        if self.state is not Game.State.Ready:
            raise StateError("Cannot start game while in state: " + self.state)
        if self.options.sixes:
            deck = THDeckSixes()
        else:
            deck = THDeckOriginal()
        self.table = Table(self.game_id, self.players, deck)
        self.table.on_change('*', (
            lambda model, key, instruction:
                self._call_listener('table', instruction, {'property': key})))
        self.state = Game.State.Running

    def remove_player(self, p):
        """Removes player from game.

        :param p: Player -- The `Player` to remove.
        """
        index = self.players.index(p)
        self.players.remove(p)
        self._update_model_collection('players', {'action': 'remove',
                                                  'index': index})
        if self.state is Game.State.Running:
            self.table.pause()
            self.state = Game.State.Paused
        elif self.state is Game.State.Ready:
            self.state = Game.State.Created

    def remove_player_by_user_id(self, user_id):
        """Remove player from game by `User.user_id`.

        :param user_id: int -- The ID of the user to remove.
        :raise: ValueError if user is not a player.
        """
        for p in self.players:
            if p.user.user_id == user_id:
                return self.remove_player(p)
        raise ValueError("User is not a player in this game.")

    def add_player(self, user, team):
        """Add a player to the game.

        :param user: User -- The player's `User` object.
        :param team: str -- The team to join ('A' or 'B').
        :raise: ValueError if `Game` is not in a state to add players, or the
            table is already full.
        """
        if self.state not in [Game.State.Created, Game.State.Paused]:
            raise StateError("Cannot add new player in state: " + self.state)
        if len(self.players) >= 4:
            raise ValueError("Game already has 4 players. Cannot add another.")
        if len([1 for p in self.players if p.team == team]) >= 2:
            raise ValueError("Team `" + team + "` is full. Cannot add player.")
        self.players.append(Player(user, team))
        self._update_model_collection('players', {'action': 'append'})
        if len(self.players) == 4:
            if self.state is Game.State.Paused:
                self.state = Game.State.Running
                self.table.resume()
            else:
                self.state = Game.State.Ready

    def add_spectator(self, user):
        """Add a spectator to the game.

        :param user: User -- The spectator's `User` object.
        :raise: ValueError if `Game` does not allow spectators, or spectator
            slots have been filled.
        """
        if self.options.spec_mode is Game.SpecMode.NoSpectators:
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

    def remove_spectator_by_user_id(self, user_id):
        """Remove spectator from game by `User.user_id`.

        :param user_id: int -- The ID of the user to remove.
        :raise: ValueError if the user is not a spectator in the game.
        """
        for spec in self.spectators:
            if spec.user.user_id == user_id:
                return self.remove_spectator(spec)
        raise ValueError("User is not a spectator in this game.")

# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
