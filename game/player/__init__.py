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
        rules = super(Spectator, cls).MODEL_RULES
        rules.update({
            'name': ('name', str, None),
            'user_id': ('user', str, lambda x: x.uid)
        })
        return rules

    @classmethod
    def new(cls, user, data_store, **kwargs):
        kwargs.update({
            'name': user.profile_name,
            'user': user
        })
        return super(Spectator, cls).new(data_store, **kwargs)

    @classmethod
    def restore(cls, data_model, data_store, **kwargs):
        ctrl = data_store.get_controller(cls, data_model.uid)
        if not ctrl:
            kwargs.update({
                'name': data_model.name,
                'user': User.get(data_model.user_id, data_store)
            })
            ctrl = super(Spectator, cls).restore(data_model, data_store,
                                                 **kwargs)
        return ctrl


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
        rules = super(Player, cls).MODEL_RULES
        rules.update({
            'hand': ('hand', DataModel, lambda x: x.model),
            'team': ('team', str, None),
            'abandoned': ('abandoned', bool, None)
        })
        return rules

    @classproperty
    def INIT_DEFAULTS(cls):
        defaults = super(Player, cls).INIT_DEFAULTS
        defaults.update({
            'abandoned': False
        })
        return defaults

    @classmethod
    def restore(cls, data_model, data_store, **kwargs):
        ctrl = data_store.get_controller(cls, data_model.uid)
        if ctrl:
            return ctrl
        kwargs.update({
            'team': data_model.team,
            'hand': CardHolder.restore(data_model.hand, data_store),
            'abandoned': data_model.abandoned
        })
        return super(Player, cls).restore(data_model, data_store, **kwargs)

    @classmethod
    def new(cls, user, team, data_store, **kwargs):
        kwargs.update({
            'team': team,
            'hand': CardHolder.new(None, 'suit', data_store)
        })
        return super(Player, cls).new(user, data_store, **kwargs)

    def new_user(self, user):
        if not self.abandoned:
            raise ValueError('Cannot change user of unabandoned player.')
        self.user = user
        self.abandoned = False

# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
