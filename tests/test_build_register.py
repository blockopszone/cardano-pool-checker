import os
import json
import pytest

from cardano_pool_checker.cardano_pool_checker import CardanoPoolChecker


@pytest.fixture
def updates_data():
    with open(os.path.join(os.path.dirname(__file__), "pools_updates_expected.json"), "r") as file:
        data = json.load(file)
    return data


@pytest.fixture
def register_expected():
    with open(os.path.join(os.path.dirname(__file__), "pools_register_expected.json"), "r") as file:
        data = json.load(file)
    return data


def test_build_register(updates_data, register_expected):
    result = CardanoPoolChecker.build_register(updates_data)
    # Save the output JSON to a file
    with open(os.path.join(os.path.dirname(__file__), "pools_register_result.json"), "w") as output_file:
        json.dump(result, output_file, indent=4)
    assert result == register_expected
