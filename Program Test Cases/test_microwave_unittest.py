# run this either as:
# unittest: python -m unittest test_microwave_unittest.py
# pytest: pytest test_microwave_unittest.py 
# (pytest will auto-discover and run the unittest.TestCase classes).

import os
import time
import tempfile
import unittest

from microwave_system import (
    MicrowaveEngine,
    RecipeManager,
    CookingStage,
)


class TestMicrowaveEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MicrowaveEngine()

    def test_start_cooking_sets_state_and_history(self):
        success = self.engine.start_cooking(90, 100, CookingStage.COOK)
        self.assertTrue(success)
        self.assertTrue(self.engine.is_running)
        self.assertEqual(self.engine.remaining_time, 90)
        self.assertEqual(self.engine.current_power, 100)
        self.assertEqual(self.engine.current_stage, CookingStage.COOK)
        history = self.engine.get_cooking_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["duration"], 90)
        self.assertEqual(history[0]["power"], 100)
        self.assertEqual(history[0]["stage"], "cook")

    def test_start_cooking_when_running_returns_false(self):
        self.engine.start_cooking(60, 60, CookingStage.WARM)
        success = self.engine.start_cooking(30, 30, CookingStage.COOK)
        self.assertFalse(success)
        self.assertEqual(len(self.engine.cooking_history), 1)

    def test_timer_counts_down_and_stops(self):
        self.engine.start_cooking(3, 100, CookingStage.COOK)
        time.sleep(4)  # allow timer thread to finish
        self.assertFalse(self.engine.is_running)
        self.assertEqual(self.engine.remaining_time, 0)

    def test_stop_cooking_resets_state(self):
        self.engine.start_cooking(60, 100, CookingStage.COOK)
        time.sleep(1)
        self.engine.stop_cooking()
        self.assertFalse(self.engine.is_running)
        self.assertEqual(self.engine.remaining_time, 0)

    def test_pause_and_resume(self):
        self.engine.start_cooking(5, 100, CookingStage.COOK)
        time.sleep(2)
        self.engine.pause_cooking()
        remaining_after_pause = self.engine.remaining_time
        time.sleep(2)
        # should not have changed while paused
        self.assertEqual(self.engine.remaining_time, remaining_after_pause)

        self.engine.resume_cooking()
        time.sleep(remaining_after_pause + 1)
        self.assertFalse(self.engine.is_running)
        self.assertEqual(self.engine.remaining_time, 0)

    def test_resume_with_zero_time_has_no_effect(self):
        self.engine.remaining_time = 0
        self.engine.is_running = False
        self.engine.resume_cooking()
        self.assertFalse(self.engine.is_running)
        self.assertEqual(self.engine.remaining_time, 0)

    def test_calculate_defrost_time_known_entry(self):
        seconds = self.engine.calculate_defrost_time("chicken", "thin", 500)
        self.assertEqual(seconds, 3 * 60)

    def test_calculate_defrost_time_scales_with_weight(self):
        seconds = self.engine.calculate_defrost_time("beef", "thick", 1000)
        self.assertEqual(seconds, 8 * 2 * 60)

    def test_calculate_defrost_time_unknown_defaults(self):
        seconds = self.engine.calculate_defrost_time("pork", "medium", 500)
        self.assertEqual(seconds, 3 * 60)

    def test_get_status_running(self):
        self.engine.start_cooking(60, 60, CookingStage.COOK)
        status = self.engine.get_status()
        self.assertTrue(status["running"])
        self.assertEqual(status["current_power"], 60)
        self.assertEqual(status["current_stage"], "cook")
        self.assertIsInstance(status["sensor_reading"], float)

    def test_get_status_idle(self):
        self.engine.stop_cooking()
        status = self.engine.get_status()
        self.assertFalse(status["running"])
        self.assertEqual(status["remaining_time"], 0)
        self.assertIsNone(status["current_stage"])
        self.assertIsInstance(status["sensor_reading"], float)


class TestRecipeManager(unittest.TestCase):
    def setUp(self):
        # Isolate filesystem using a temp directory, so we don't touch real recipes.json
        self._old_cwd = os.getcwd()
        self._tmpdir = tempfile.TemporaryDirectory()
        os.chdir(self._tmpdir.name)
        self.manager = RecipeManager()

    def tearDown(self):
        os.chdir(self._old_cwd)
        self._tmpdir.cleanup()

    def test_sample_recipes_created_when_file_missing(self):
        self.assertGreaterEqual(len(self.manager.recipes), 3)
        self.assertEqual(self.manager.favorites, [])
        self.assertTrue(os.path.exists("recipes.json"))

    def test_add_recipe_persists(self):
        idx = self.manager.add_recipe(
            name="Test Dish",
            category="Dinner",
            ingredients=["x", "y"],
            steps=["step1"],
            cooking_stages=[{"time": 60, "power": 80, "action": "Cook"}],
        )
        self.assertEqual(idx, len(self.manager.recipes) - 1)
        self.assertEqual(self.manager.recipes[idx]["name"], "Test Dish")

        # new manager should load it from file
        new_manager = RecipeManager()
        self.assertEqual(new_manager.recipes[idx]["name"], "Test Dish")

    def test_get_recipes_by_category(self):
        desserts = self.manager.get_recipes_by_category("Dessert")
        self.assertTrue(all(r["category"] == "Dessert" for r in desserts))

    def test_search_by_name_and_ingredient(self):
        # name search
        results_name = self.manager.search_recipes("mug")
        self.assertTrue(any("mug" in r["name"].lower() for r in results_name))

        # ingredient search (assuming sample has "eggs")
        results_ing = self.manager.search_recipes("eggs")
        self.assertTrue(any("eggs" in " ".join(r["ingredients"]).lower() for r in results_ing))

    def test_search_no_matches(self):
        results = self.manager.search_recipes("nonexistentingredient")
        self.assertEqual(results, [])

    def test_add_to_favorites_no_duplicates(self):
        idx = 0
        self.manager.add_to_favorites(idx)
        self.manager.add_to_favorites(idx)
        self.assertEqual(self.manager.favorites.count(idx), 1)

    def test_remove_from_favorites(self):
        idx = 0
        self.manager.add_to_favorites(idx)
        self.manager.remove_from_favorites(idx)
        self.assertNotIn(idx, self.manager.favorites)

    def test_get_favorites_ignores_out_of_range(self):
        # Directly simulate a stale index
        self.manager.favorites = [0, 999]
        favs = self.manager.get_favorites()
        self.assertEqual(len(favs), 1)
        # index 0 should correspond to first recipe
        self.assertEqual(favs[0], self.manager.recipes[0])

    def test_persistence_across_instances(self):
        idx = self.manager.add_recipe(
            name="Persistent Dish",
            category="Lunch",
            ingredients=["a"],
            steps=["s"],
            cooking_stages=[{"time": 30, "power": 50, "action": "Cook"}],
        )
        self.manager.add_to_favorites(idx)

        new_manager = RecipeManager()
        self.assertEqual(new_manager.recipes[idx]["name"], "Persistent Dish")
        self.assertIn(idx, new_manager.favorites)


if __name__ == "__main__":
    unittest.main()