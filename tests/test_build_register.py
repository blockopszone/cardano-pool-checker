"""test module for build_register."""  # noqa: INP001
# see https://docs.pytest.org/en/latest/explanation/goodpractices.html#tests-outside-application-code
import json
import os
from typing import Any

import pytest

from cardano_pool_checker.cardano_pool_checker_class import CardanoPoolChecker


@pytest.fixture()
def updates_data() -> list[Any]:
    """Fixture that loads the testing pool updates.

    Returns:
        list[Any]: Return a list of updates.
    """
    with open(os.path.join(os.path.dirname(__file__), "pools_updates_expected.json")) as file:
        return json.load(file)


@pytest.fixture()
def register_expected() -> list[dict[str, Any]]:
    """Fixture that loads the expected register after processing the updates.

    Returns:
        list[dict[str, Any]]: Return a list with the pools register.
    """
    with open(os.path.join(os.path.dirname(__file__), "pools_register_expected.json")) as file:
        return json.load(file)


def test_build_register(updates_data: list[Any], register_expected: list[dict[str, Any]]):
    """Tests that function build_register returns the expected result.

    Args:
        updates_data (list[Any]): list of updates to process.
        register_expected (list[dict[str, Any]]): list with expected register.
    """
    result = CardanoPoolChecker.build_register(updates_data)
    # Save the output JSON to a file
    with open(os.path.join(os.path.dirname(__file__), "pools_register_result.json"), "w") as output_file:
        json.dump(result, output_file, indent=4)
    assert result == register_expected  # noqa: S101
