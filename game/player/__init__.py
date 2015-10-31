"""Player package.

.. packageauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class Spectator -- User controller for game spectator.
    :class Player -- User controller for game player.

"""

from core.datamodel import DataModelController, DataModel
from core.decorators import classproperty
from game.deck import CardHolder
from store.user import User


class Spectator(DataModelController):
    """Spectating user.

    Class Properties:
        :type MODEL_RULES: dict -- The rule set for the underlying `DataModel`.

    Class Methods:
        load -- Load new Game object from existing DataModel.
        get -- Load new Game object from existing game_id.

    Init Parameters:
        user -- The `User` object.

    Properties:
        :type name: str -- The profile name of the user.
        :type user: User -- The user.
    """

    @classproperty
    def MODEL_RULES(cls):
        """Rules for the DataModel.

        New Model Keys:
            :key name: str -- The profile name of the user.
            :key user: DataModel -- The user data.
        """
        return {
            'name': ('name', str, None),
            'user': ('user', DataModel, lambda x: x.model)
        }

    @classmethod
    def load(cls, model):
        user = User.load()

    @classmethod
    def get(cls, player_id):
        pass

    def __init__(self, user):
        """Spectator init.

        :param user: User -- The user.
        """
        self.name, self.user = user.profile_name, user
        super(Spectator, self).__init__(self.__class__.MODEL_RULES)


class Player(Spectator):
    """Game player.

    Init Parameters:
        user -- The user object.
        team -- The player's team.

    Properties:
        :type team: str -- The player's team identifier.
    """

    @classproperty
    def MODEL_RULES(cls):
        """Rules for the DataModel.

        New Model Keys:
            :key hand: DataModel -- Model representating the player's
                `CardContainer` or hand.
            :key team: str -- Player's team identifier.
            :key player_id: int -- The unique Player ID.
        """
        old_rules = super(Player, cls).MODEL_RULES
        old_rules['hand'] = ('hand', DataModel, lambda x: x.model)
        old_rules['team'] = ('team', str, None)
        old_rules['player_id'] = ('player_id', int, None)
        return old_rules

    def __init__(self, user, team):
        """Player init.

        :param user: User -- The user.
        :param team: str -- The team identifier.
        """
        self.team = team
        self.hand = CardHolder(None, 'suit')
        self.player_id = id(self)  # TODO: Player ID generator
        super(Player, self).__init__(user)

# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
