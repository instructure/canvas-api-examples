from pathlib import Path

from recipes import discover

TESTS = Path(__file__).parent
MOCKED_TESTS = TESTS / "test_recipes.py"
LIVE_TESTS = TESTS / "test_live.py"


def untested_recipes(test_file, reference):
    """Recipes missing from tests."""
    source = test_file.read_text()
    return [r["id"] for r in discover() if reference.format(id=r["id"]) not in source]


def test_every_recipe_has_a_mocked_test():
    """We need mocked tests for each recipe because we build the current list of APIs from them."""
    untested = untested_recipes(MOCKED_TESTS, "recipes.{id}")
    assert not untested, (
        f"Recipe(s) without a mocked test in tests/test_recipes.py: {', '.join(untested)}. "
        "Add a test that runs the recipe against mocked Canvas responses, then run "
        "`python scripts/list_apis.py` to update used-apis.txt."
    )


def test_every_recipe_has_a_live_test():
    """Live tests catch API changes the mocks can't. The PR author runs them: pytest -m live."""
    untested = untested_recipes(LIVE_TESTS, 'recipe("{id}")')
    assert not untested, (
        f"Recipe(s) without a live test in tests/test_live.py: {', '.join(untested)}. "
        "Add a test that runs the recipe against a real demo Canvas, and make sure "
        "`pytest -m live` passes before you open the PR."
    )
