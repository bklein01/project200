"""Player package.

.. packageauthor:: Dave Zimmelman <zimmed@zimmed.io>

Exports:


"""

from core.datamodel import DataModelController, DataModel
from game.deck import CardHolder


class Player(DataModelController):

    MODEL_RULES = {
        'hand': ('hand', DataModel, lambda x: x.model),
        'name': ('name', str, None),
        'team': ('team', str, None),
        'player_id': ('player_id', int, None),
        'user_data': ('user_data', dict, None)
    }

    def __init__(self, user, team):
        self.team = team
        self.user_data = {}
        self.name = user.profie_name
        self.hand = CardHolder(None, 'suit')
        self.player_id = id(self)  # TODO: Player ID generator

# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
