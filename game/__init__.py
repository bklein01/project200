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

    State = Enum('Created', 'Ready', 'Running', 'Paused')
    SpecMode = Enum('NoSpectators', 'Standard', 'ActivePlayer', 'AllInfo')

    DEFAULT_OPTIONS = DotDict({
        'sixes': False,
        'spec_mode': 'Standard',
        'spec_allow_chat': True,
        'spec_max': 4
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
        for p in self.players:
            if p.user.user_id == user_id:
                return self.remove_player(p)
        raise ValueError("User is not a player in this game.")

    def add_player(self, user, team):
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
        if self.options.spec_mode is Game.SpecMode.NoSpectators:
            raise StateError("This game does not allow spectators.")
        if len(self.spectators) >= self.options.spec_max:
            raise StateError("This game has reached the max allowed "
                             "spectators.")
        self.spectators.append(Spectator(user))
        self._update_model_collection('spectators', {'action': 'append'})

    def remove_spectator(self, spec):
        index = self.spectators.index(spec)
        self.spectators.remove(spec)
        self._update_model_collection('spectators', {'action': 'remove',
                                                     'index': index})

    def remove_spectator_by_user_id(self, user_id):
        for spec in self.spectators:
            if spec.user.user_id == user_id:
                return self.remove_spectator(spec)
        raise ValueError("User is not a spectator in this game.")



# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
