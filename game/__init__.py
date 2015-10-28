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
from game.player import Player
# from core.decorators import classproperty


class Game(DataModelController):

    State = Enum('Created', 'Ready', 'Running', 'Paused')

    DEFAULT_OPTIONS = DotDict({
        'sixes': False
    })

    # noinspection PyCallByClass,PyTypeChecker
    MODEL_RULES = {
        'game_id': ('game_id', int, None),
        'players': ('players', Collection.List(DataModel), lambda x: x.model),
        'owner_id': ('creator', int, lambda x: x.id),
        'state': ('state', str, None),
        'table': ('table', DataModel, lambda x: x.model),
        'points': ('points', Collection.Dict(int), None)
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
        super(Game, self).__init__(self.__class__.MODEL_RULES)

    def new_game(self):
        if self.state is not Game.State.Ready:
            raise StateError("Cannot start game while in state: " + self.state)
        if self.options.sixes:
            deck = THDeckSixes()
        else:
            deck = THDeckOriginal()
        self.table = Table(self.game_id, self.players, deck)
        self.state = Game.State.Running

    def remove_player(self, p):
        self.players.remove(p)
        if self.state is Game.State.Running:
            self.table.pause()
            self.state = Game.State.Paused
        elif self.state is Game.State.Ready:
            self.state = Game.State.Created

    def remove_player_by_user(self, user):
        for p in self.players:
            if p.user_data.user_id == user.user_id:
                return self.remove_player(p)
        raise ValueError("User has no player in this game.")

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


# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
