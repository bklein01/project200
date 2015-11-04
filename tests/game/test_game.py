#!/usr/bin/env python
"""Unit tests for `game.Game` class.

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>

"""

from . import (GameNoInitTestCase, GameInitTestCase, GameCreatedTestCase,
               GameReadyTestCase, GameRunningTestCase)
from core.exceptions import StateError
from game import Game


class GameNewTest(GameNoInitTestCase):
    """Game construction tests."""

    def test_new(self):
        """Tests Game.new with default args."""
        obj = Game.new(self._creator, self._ds)
        self.assertIsInstance(obj, Game, "Game instance not initialized.")
        self.assertHasAttribute(obj, 'uid', "Game has no unique ID.")
        self.assertHasAttributes(obj, [
            'players', 'spectators', 'state', 'points', 'options', 'table'])
        self.assertIsCREATED(obj)

    def test_new_options(self):
        """Tests Game.new with options arg."""
        obj = Game.new(self._creator, self._ds, {
            'sixes': True,
            'spec_allow_chat': False,
            'win_amount': 400
        })
        self.assertTrue(obj.options.sixes,
                        "game.options.sixes didn't set.")
        self.assertFalse(obj.options.spec_allow_chat,
                         "game.options.spec_allow_chat didn't set.")
        self.assertEqual(obj.options.win_amount, 400,
                         "game.options.win_amount didn't set.")


class GameLoadTest(GameInitTestCase):
    """Game loading/restoring tests."""

    def test_load_existing(self):
        """Tests Game.get/load with existing controller in cache."""
        game_a = Game.get(self._ds, self._game.uid)
        self.assertIsInstance(game_a, Game,
                              "Didn't retrieve Game controller.")
        self.assertIs(self._game, game_a,
                      "Instances are not the same.")
        game_b = Game.load(self._ds, self._game.uid)
        self.assertIs(game_a, game_b,
                      "Game get and load instances do not match.")
        self.assertEqual(id(game_a), id(game_b),
                         "Game get and load instances do not match.")

    def test_delete_cache(self):
        """Tests that controller cache is deleted."""
        uid = self._game.uid
        self._game.delete_cache(self._ds)
        self._game = None
        self.assertIsNone(self._ds.get_strict_controller(Game, uid),
                          "Game controller did not clear from cache.")

    def test_save(self):
        """Tests permanent model save."""
        uid = self._game.uid
        self._game.save(self._ds)
        self._game.delete_cache(self._ds)
        self._game = None
        model = self._ds.get_strict_model(Game, uid)
        self.assertIsNotNone(model, "Model did not save.")
        self.assertEqual(model.uid, uid, "Model did not save correctly.")

    def test_delete(self):
        """Tests that controller and model is deleted."""
        uid = self._game.uid
        self._game.save(self._ds)
        self._game.delete(self._ds)
        self._game = None
        self.assertIsNone(self._ds.get_strict_controller(Game, uid))
        with self.assertRaises(ValueError):
            self._ds.get_controller(Game, uid)

    def test_load_stored(self):
        """Tests Game.get/load with non-existing controller."""
        uid = self._game.uid
        gid = id(self._game)
        # Save model then delete controller from memory
        self._game.save(self._ds)
        self._game.delete_cache(self._ds)
        self._game = None
        # Retrieve new controller from existing model
        _game = Game.get(uid, self._ds)
        self.assertIsInstance(_game, Game,
                              "`get` Didn't retrieve Game controller.")
        self.assertEqual(_game.uid, uid,
                         "Game controller `get` does not match uid.")
        self.assertNotEqual(gid, id(_game),
                            "Game controller didn't delete properly.")
        gid = id(_game)
        Game.delete_cache(self._ds, uid)
        self._game = Game.load(uid, self._ds)
        self.assertIsInstance(self._game, Game,
                              "`load` Didn't retrieve Game controller.")
        self.assertEqual(self._game.uid, uid,
                         "Game controller `load` does not match uid.")
        self.assertNotEqual(gid, id(self._game),
                            "Game controller didn't delete properly.")

    def test_restore_existing(self):
        """Tests Game.restore with existing controller."""
        model = self._game.model
        gid = id(self._game)
        self._game = None
        self._game = Game.restore(self._ds, model)
        self.assertIsInstance(self._game, Game,
                              "`restore` didn't retrieve Game controller.")
        self.assertEqual(self._game.uid, model.uid,
                         "Controller and model do not match.")
        self.assertEqual(id(self._game), gid,
                         "Game instances do not match.")
        self.assertIs(model, self._game.model,
                      "Model instances do not match")

    def test_restore_stored(self):
        """Tests Game.restore with non-existing controller."""
        model = self._game.model
        gid = id(self._game)
        self._game.save(self._ds)
        self._game.delete_cache(self._ds)
        self._game = None
        _game = Game.restore(self._ds, model)
        self.assertIsInstance(_game, Game,
                              "`restore` didn't retrieve Game controller.")
        self.assertEqual(_game.uid, model.uid,
                         "Controller and model do not match.")
        self.assertNotEqual(gid, id(_game),
                            "Game controller didn't delete properly.")


class GameSetupTest(GameCreatedTestCase):
    """Game CREATED to READY tests."""

    def test_valid_game_setup(self):
        """Tests valid behavior for adding players to READY state."""
        self.assertEqual(self._game.active_players(), 1)
        for x in xrange(1, 4):
            self._game.add_player(self._users[x], x)
        self.assertEqual(self._game.active_players(), 4)
        self.assertIsREADY(self._game)

    def test_invalid_game_setup(self):
        """Tests invalid behavior for adding players to READY state."""
        with self.assertRaises(ValueError):
            self._game.add_player(self._creator, 1)
        with self.assertRaises(ValueError):
            self._game.add_player(self._users[1], 0)
        for x in xrange(1, 4):
            self._game.add_player(self._users[x], x)
        with self.assertRaises(ValueError):
            self._game.add_player(self._users[4], 1)


class GameStartTest(GameReadyTestCase):
    """Game table setup tests."""

    def test_valid_new_game(self):
        """Tests valid Game.new_game behavior."""
        self._game.new_game()
        self.assertIsRUNNING(self._game)
        self.assertIsNotNone(self._game.table)
        self.assertEqual(self._game.table.player_turn, 1,
                         "Game.table unsuccessful init.")

    def test_invalid_new_game(self):
        """Tests invalid Game.new_game behavior."""
        self._game.remove_player_by_user_id(self._users[1].uid)
        with self.assertRaises(StateError):
            self._game.new_game()
        self._game.add_player(self._users[1], 1)
        self._game.new_game()
        with self.assertRaises(StateError):
            self._game.new_game()


class GamePauseResumeTestPregame(GameReadyTestCase):
    """Game READY to CREATED behavior."""

    def test_valid_pause_resume_pregame(self):
        """Tests valid behavior for removing players when READY."""
        self._game.remove_player_by_user_id(self._users[1].uid)
        self.assertIsCREATED(self._game)
        self.assertEqual(self._game.active_players(), 3)
        self._game.remove_player_by_user_id(self._users[2].uid)
        self._game.add_player(self._users[4], 2)
        self._game.add_player(self._users[2], 1)
        self.assertIsREADY(self._game)
        self.assertEqual(self._game.active_players(), 4)

    def test_invalid_pause_resume_pregame(self):
        """Tests invalid behavior for removing players when READY."""
        with self.assertRaises(ValueError):
            self._game.remove_player_by_user_id(self._users[4].uid)
        self._game.remove_player_by_user_id(self._users[2].uid)
        with self.assertRaises(ValueError):
            self._game.add_player(self._users[4], 1)
        with self.assertRaises(ValueError):
            self._game.add_player(self._users[1], 2)


class GamePauseResumeTest(GameRunningTestCase):
    """Game RUNNING to PAUSED tests."""

    def test_valid_pause_resume(self):
        """Tests valid behavior for removing players when RUNNING."""
        p_1_model = self._game.players[1].model
        p_2_model = self._game.players[2].model
        self._game.remove_player_by_user_id(self._users[1].uid)
        self.assertIsPAUSED(self._game)
        self.assertEqual(self._game.active_players(), 3)
        self._game.remove_player_by_user_id(self._users[2].uid)
        self._game.add_player(self._users[4], 2)
        self._game.add_player(self._users[2], 1)
        self.assertIsRUNNING(self._game)
        self.assertEqual(self._game.active_players(), 4)
        self.assertIs(self._game.players[1].model, p_1_model,
                      "Player 1 model did not preserve.")
        self.assertIs(self._game.players[2].model, p_2_model,
                      "Player 2 model did not preserve.")

    def test_invalid_pause_resume(self):
        """Tests invalid behavior for removing players when RUNNING."""
        with self.assertRaises(ValueError):
            self._game.remove_player_by_user_id(self._users[4].uid)
        self._game.remove_player_by_user_id(self._users[2].uid)
        self._game.remove_player_by_user_id(self._users[3].uid)
        with self.assertRaises(ValueError):
            self._game.remove_player_by_user_id(self._users[2].uid)
        with self.assertRaises(ValueError):
            self._game.add_player(self._users[4], 1)
        with self.assertRaises(ValueError):
            self._game.add_player(self._users[1], 2)
        self._game.add_player(self._users[4], 2)
        self.assertIsPAUSED(self._game)
        with self.assertRaises(StateError):
            self._game.new_game()
