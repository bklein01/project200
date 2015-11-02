#!/usr/bin/env python
"""Game tests package.

.. packageauthor: zimmed <zimmed@zimmed.io>

Exposes:
    :class GameTestCase -- The class that all game tests must inherit from.
"""

from .. import TestCase, main
from game import Game
from store.user import User
from store import ModelStore


class GameNoInitTestCase(TestCase):

    def setUp(self):
        super(GameNoInitTestCase, self).setUp()
        self._ds = ModelStore
        self._user_generator = (
            User.new(None, 'user' + str(x), 'user@user.us', 'pw', self._ds)
            for x in xrange(1, 999))
        self._creator = self._user_generator.next()

    def tearDown(self):
        super(GameNoInitTestCase, self).tearDown()
        if self._creator:
            User.delete(self._creator.uid, self._ds)
            self._creator = None

    def assertIsGameState(self, obj, state, msg=None):
        if not msg:
            msg = ("Game is in state `" + obj.state + "`, not"
                   " `" + state + "`.")
        self.assertEqual(obj.state, state, msg)

    def assertIsCREATED(self, obj, msg=None):
        self.assertIsGameState(obj, Game.State.CREATED, msg)

    def assertIsREADY(self, obj, msg=None):
        self.assertIsGameState(obj, Game.State.READY, msg)

    def assertIsRUNNING(self, obj, msg=None):
        self.assertIsGameState(obj, Game.State.RUNNING, msg)

    def assertIsPAUSED(self, obj, msg=None):
        self.assertIsGameState(obj, Game.State.PAUSED, msg)

    def assertIsEND(self, obj, msg=None):
        self.assertIsGameState(obj, Game.State.END, msg)


class GameInitTestCase(GameNoInitTestCase):

    def setUp(self):
        super(GameInitTestCase, self).setUp()
        self._game = Game.new(self._creator, self._ds)

    def tearDown(self):
        super(GameInitTestCase, self).tearDown()
        if hasattr(self, '_game') and self._game:
            Game.delete(self._game.uid, self._ds)
        self._game = None


class GameCreatedTestCase(GameInitTestCase):

    def setUp(self):
        super(GameCreatedTestCase, self).setUp()
        self._users = [self._user_generator.next() for _ in xrange(6)]
        if self._game.state is not Game.State.CREATED:
            raise RuntimeError("GameCreatedTestCase setUp failed.")

    def tearDown(self):
        super(GameCreatedTestCase, self).tearDown()
        for u in self._users:
            if u:
                User.delete(u.uid, self._ds)
        self._users = None


class GameReadyTestCase(GameCreatedTestCase):

    def setUp(self):
        super(GameReadyTestCase, self).setUp()
        for x in xrange(1, 4):
            self._game.add_player(self._users[x], x)
        if self._game.state is not Game.State.READY:
            raise RuntimeError("GameReadyTestCase setUp failed.")


class GameRunningTestCase(GameReadyTestCase):

    def setUp(self):
        super(GameRunningTestCase, self).setUp()
        self._game.new_game()
        if self._game.state is not Game.State.RUNNING:
            raise RuntimeError("GameRunningTestCase setUp failed.")


if __name__ == '__main__':
    main()

# ----------------------------------------------------------------------------
__version__ = 0.1
__license__ = "MIT"
__credits__ = ["zimmed"]
# ----------------------------------------------------------------------------
