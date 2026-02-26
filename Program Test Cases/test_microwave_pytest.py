import os
import time
import tempfile

import pytest

from microwave_system import MicrowaveEngine, RecipeManager, CookingStage


@pytest.fixture
def engine():
    return MicrowaveEngine()


def test_engine_quick_start_and_finish(engine):
    engine.start_cooking(2, 100, CookingStage.COOK)
    time.sleep(3)
    assert engine.is_running is False
    assert engine.remaining_time == 0


@pytest.fixture
def recipe_manager_tmp():
    old_cwd = os.getcwd()
    tmpdir = tempfile.TemporaryDirectory()
    os.chdir(tmpdir.name)
    try:
        manager = RecipeManager()
        yield manager
    finally:
        os.chdir(old_cwd)
        tmpdir.cleanup()


def test_recipe_search_and_favorites(recipe_manager_tmp):
    manager = recipe_manager_tmp

    results = manager.search_recipes("cake")
    assert results  # at least one recipe with "cake" in name or ingredients

    idx = 0
    manager.add_to_favorites(idx)
    manager.add_to_favorites(idx)
    assert manager.favorites.count(idx) == 1

    favs = manager.get_favorites()
    assert favs[0] == manager.recipes[idx]