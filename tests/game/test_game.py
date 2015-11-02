#!/usr/bin/env python
"""Unit tests for `game.Game` class.

.. moduleauthor:: Dave Zimmelman <zimmed@zimmed.io>

"""

from . import (GameNoInitTestCase, GameInitTestCase, GameCreatedTestCase,
               GameReadyTestCase, GameRunningTestCase)
from core.exceptions import StateError
from game import Game


class GameNewTest(GameNoInitTestCase):

    def test_new(self):
        obj = Game.new(self._creator, self._ds)
        self.assertIsInstance(obj, Game, "Game instance not initialized.")
        self.assertHasAttribute(obj, 'uid', "Game has no unique ID.")
        self.assertHasAttributes(obj, [
            'players', 'spectators', 'state', 'points', 'options', 'table'])
        self.assertIsCREATED(obj)

    def test_new_options(self):
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

    def test_load_existing(self):
        game_a = Game.get(self._game.uid, self._ds)
        self.assertIsInstance(game_a, Game,
                              "Didn't retrieve Game controller.")
        self.assertIs(self._game, game_a,
                      "Instances are not the same.")
        game_b = Game.load(self._game.uid, self._ds)
        self.assertIs(game_a, game_b,
                      "Game get and load instances do not match.")
        self.assertEqual(id(game_a), id(game_b),
                         "Game get and load instances do not match.")

    def test_load_stored(self):
        uid = self._game.uid
        gid = id(self._game)
        # Delete controller from memory
        self._game = None
        self.assertTrue(self._ds.delete_controller(Game, uid),
                        "Game controller delete from store failed.")
        # Retrieve new controller from existing model
        self._game = Game.get(uid, self._ds)
        self.assertIsInstance(self._game, Game,
                              "`get` Didn't retrieve Game controller.")
        self.assertEqual(self._game.uid, uid,
                         "Game controller `get` does not match uid.")
        self.assertNotEqual(gid, id(self._game),
                            "Game controller didn't delete properly.")
        gid = id(self._game)
        self._game = None
        self._ds.delete_controller(Game, uid)
        self._game = Game.load(uid, self._ds)
        self.assertIsInstance(self._game, Game,
                              "`load` Didn't retrieve Game controller.")
        self.assertEqual(self._game.uid, uid,
                         "Game controller `load` does not match uid.")
        self.assertNotEqual(gid, id(self._game),
                            "Game controller didn't delete properly.")

    def test_restore_existing(self):
        model = self._game.model
        gid = id(self._game)
        self._game = None
        self._game = Game.restore(model, self._ds)
        self.assertIsInstance(self._game, Game,
                              "`restore` didn't retrieve Game controller.")
        self.assertEqual(self._game.uid, model.uid,
                         "Controller and model do not match.")
        self.assertEqual(id(self._game), gid,
                         "Game instances do not match.")

    def test_restore_stored(self):
        model = self._game.model
        gid = id(self._game)
        self._ds.delete_controller(Game, model.uid)
        self._game = None
        self._game = Game.restore(model, self._ds)
        self.assertIsInstance(self._game, Game,
                              "`restore` didn't retrieve Game controller.")
        self.assertEqual(self._game.uid, model.uid,
                         "Controller and model do not match.")
        self.assertNotEqual(gid, id(self._game),
                            "Game controller didn't delete properly.")


class GameSetupTest(GameCreatedTestCase):

    def test_valid_game_setup(self):
        self.assertEqual(self._game.active_players(), 1)
        for x in xrange(1, 4):
            self._game.add_player(self._users[x], x)
        self.assertEqual(self._game.active_players(), 4)
        self.assertIsREADY(self._game)

    def test_invalid_game_setup(self):
        with self.assertRaises(ValueError):
            self._game.add_player(self._users[0], 1)
        with self.assertRaises(ValueError):
            self._game.add_player(self._users[1], 0)
        for x in xrange(1, 4):
            self._game.add_player(self._users[x], x)
        with self.assertRaises(ValueError):
            self._game.add_player(self._users[4], 1)


class GameStartTest(GameReadyTestCase):

    def test_valid_new_game(self):
        self._game.new_game()
        self.assertIsRUNNING(self._game)
        self.assertIsNotNone(self._game.table)
        self.assertEqual(self._game.table.player_turn, 1,
                         "Game.table unsuccessful init.")

    def test_invalid_new_game(self):
        self._game.remove_player_by_user_id(self._users[1].uid)
        with self.assertRaises(StateError):
            self._game.new_game()
        self._game.add_player(self._users[1], 1)
        self._game.new_game()
        with self.assertRaises(StateError):
            self._game.new_game()


class GamePauseResumeTestPregame(GameReadyTestCase):

    def test_valid_pause_resume_pregame(self):
        self._game.remove_player_by_user_id(self._users[1].uid)
        self.assertIsCREATED(self._game)
        self.assertEqual(self._game.active_players(), 3)
        self._game.remove_player_by_user_id(self._users[2].uid)
        self._game.add_player(self._users[4], 2)
        self._game.add_player(self._users[2], 1)
        self.assertIsREADY(self._game)
        self.assertEqual(self._game.active_players(), 4)

    def test_invalid_pause_resume_pregame(self):
        with self.assertRaises(ValueError):
            self._game.remove_player_by_user_id(self._users[4].uid)
        self._game.remove_player_by_user_id(self._users[2].uid)
        with self.assertRaises(ValueError):
            self._game.add_player(self._users[4], 1)
        with self.assertRaises(ValueError):
            self._game.add_player(self._users[1], 2)


class GamePauseResumeTest(GameRunningTestCase):

    def test_valid_pause_resume(self):
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
        self.assertIs(self._game.players[1], p_1_model,
                      "Player 1 model did not preserve.")
        self.assertIs(self._game.players[2], p_2_model,
                      "Player 2 model did not preserve.")

    def test_invalid_pause_resume(self):
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





