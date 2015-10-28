"""Player package.

.. packageauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:
    :class Spectator -- User controller for game spectator.
    :class Player -- User controller for game player.

"""

from core.datamodel import DataModelController, DataModel
from core.decorators import classproperty
from game.deck import CardHolder


class Spectator(DataModelController):

    @classproperty
    def MODEL_RULES(cls):
        return {
            'name': ('name', str, None),
            'user': ('user', DataModel, lambda x: x.model)
        }

    def __init__(self, user):
        self.name, self.user = user.profile_name, user
        super(Spectator, self).__init__(self.__class__.MODEL_RULES)


class Player(Spectator):

    @classproperty
    def MODEL_RULES(cls):
        old_rules = super(Player, cls).MODEL_RULES
        old_rules['hand'] = ('hand', DataModel, lambda x: x.model)
        old_rules['team'] = ('team', str, None)
        old_rules['player_id'] = ('player_id', int, None)
        return old_rules

    def __init__(self, user, team):
        self.team = team
        self.hand = CardHolder(None, 'suit')
        self.player_id = id(self)  # TODO: Player ID generator
        super(Player, self).__init__(user)

# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
