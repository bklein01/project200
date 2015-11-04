"""Player package.

.. packageauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class Spectator -- User controller for game spectator.
    :class Player -- User controller for game player.

"""

from combomethod import combomethod
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

    # noinspection PyMethodOverriding
    @classmethod
    def new(cls, user, data_store=None, **kwargs):
        kwargs.update({
            'name': user.profile_name,
            'user': user
        })
        return super(Spectator, cls).new(data_store, **kwargs)

    @classmethod
    def restore(cls, data_store, data_model, **kwargs):
        kwargs.update({
            'name': data_model.name,
            'user': User.get(data_store, data_model.uid)
        })
        return super(Spectator, cls).restore(data_store, data_model,
                                             **kwargs)


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

    # noinspection PyMethodParameters
    @combomethod
    def delete_cache(rec, data_store, uid=None):
        if isinstance(rec, Player):
            rec.hand.delete_cache(data_store)
        super(Player, rec).delete_cache(data_store, uid)

    # noinspection PyMethodParameters
    @combomethod
    def delete(rec, data_store, uid=None):
        """Delete hand controller and instance before Player."""
        if isinstance(rec, Player):
            rec.hand.delete(data_store)
        super(Player, rec).delete(data_store, uid)

    @classmethod
    def restore(cls, data_store, data_model, **kwargs):
        kwargs.update({
            'team': data_model.team,
            'hand': CardHolder.restore(data_model.hand, data_store),
            'abandoned': data_model.abandoned
        })
        return super(Player, cls).restore(data_store, data_model, **kwargs)

    # noinspection PyMethodOverriding
    @classmethod
    def new(cls, user, team, data_store=None, **kwargs):
        kwargs.update({
            'team': team,
            'hand': CardHolder.new(None, data_store, sort_method='suit')
        })
        return super(Player, cls).new(user, data_store, **kwargs)

    def __init__(self, *args, **kwargs):
        super(Player, self).__init__(*args, **kwargs)
        self.hand.on_change('*', (
            lambda model, key, instruction:
                self._call_listener('hand', instruction, {'property': key})))

    def new_user(self, user):
        if not self.abandoned:
            raise ValueError('Cannot change user of unabandoned player.')
        self.user = user
        self.name = user.profile_name
        self.abandoned = False

# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
