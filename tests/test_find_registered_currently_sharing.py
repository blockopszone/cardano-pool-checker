"""test module for find_registered_currently_sharing_* functions."""  # noqa: INP001
# see https://docs.pytest.org/en/latest/explanation/goodpractices.html#tests-outside-application-code
import json
import os
from typing import Any

import pytest

from cardano_pool_checker.cardano_pool_checker_class import CardanoPoolChecker


@pytest.fixture()
def register_data() -> list[dict[str, Any]]:
    """Fixture that loads the register data.

    Returns:
        list[dict[str, Any]]: list with the register data.
    """
    with open(os.path.join(os.path.dirname(__file__), "pools_register_expected.json")) as file:
        return json.load(file)


def load_expected(prefix: str) -> dict[Any]:
    """Loads a expected test result from a file for a given prefix.

    Args:
        prefix (str): The prefix that uniquely identifies the file.

    Returns:
        dict[Any]: Returns a dictionary with the expected test result.
    """
    mydir = os.path.dirname(__file__)
    with open(os.path.join(mydir, prefix + "_expected.json")) as file:
        return json.load(file)


def save_result(prefix: str, data: dict[Any]):
    """Saves the data from a test result to a file with a given prefix.

    Args:
        prefix (str): The prefix to uniquely identify the file.
        data (dict[Any]): The data to save to the file.
    """
    mydir = os.path.dirname(__file__)
    with open(os.path.join(mydir, prefix + "_result.json"), "w") as file:
        json.dump(data, file, indent=4)


def test_find_registered_currently_sharing_relay_hostname(register_data: list[dict[str, Any]]):
    """Tests that function find_registered_currently_sharing_relay_hostname returns the expected result.

    Args:
        register_data (list[dict[str, Any]]): The test register data.
    """
    # Define the prefix of the field to test and load expected results
    prefix = "registered_currently_sharing_relay_hostname"
    expected = load_expected(prefix)
    # Run the function to test
    result = CardanoPoolChecker.find_registered_currently_sharing_relay_hostname(register_data)
    # Save the output JSON to a file for further analysis
    save_result(prefix, result)
    # test result
    assert result == expected  # noqa: S101


def test_find_registered_currently_sharing_relay_ipv4(register_data: list[dict[str, Any]]):
    """Tests that function find_registered_currently_sharing_relay_ipv4 returns the expected result.

    Args:
        register_data (list[dict[str, Any]]): The test register data.
    """
    # Define the prefix of the field to test and load expected results
    prefix = "registered_currently_sharing_relay_ipv4"
    expected = load_expected(prefix)
    # Run the function to test
    result = CardanoPoolChecker.find_registered_currently_sharing_relay_ipv4(register_data)
    # Save the output JSON to a file for further analysis
    save_result(prefix, result)
    # test result
    assert result == expected  # noqa: S101


def test_find_registered_currently_sharing_relay_ipv6(register_data: list[dict[str, Any]]):
    """Tests that function find_registered_currently_sharing_relay_ipv6 returns the expected result.

    Args:
        register_data (list[dict[str, Any]]): The test register data.
    """
    # Define the prefix of the field to test and load expected results
    prefix = "registered_currently_sharing_relay_ipv6"
    expected = load_expected(prefix)
    # Run the function to test
    result = CardanoPoolChecker.find_registered_currently_sharing_relay_ipv6(register_data)
    # Save the output JSON to a file for further analysis
    save_result(prefix, result)
    # test result
    assert result == expected  # noqa: S101


def test_find_registered_currently_sharing_meta_json_homepage(register_data: list[dict[str, Any]]):
    """Tests that function find_registered_currently_sharing_meta_json_homepage returns the expected result.

    Args:
        register_data (list[dict[str, Any]]): The test register data.
    """
    # Define the prefix of the field to test and load expected results
    prefix = "registered_currently_sharing_meta_json_homepage"
    expected = load_expected(prefix)
    # Run the function to test
    result = CardanoPoolChecker.find_registered_currently_sharing_meta_json_homepage(register_data)
    # Save the output JSON to a file for further analysis
    save_result(prefix, result)
    # test result
    assert result == expected  # noqa: S101


def test_find_registered_currently_sharing_meta_url(register_data: list[dict[str, Any]]):
    """Tests that function find_registered_currently_sharing_meta_url returns the expected result.

    Args:
        register_data (list[dict[str, Any]]): The test register data.
    """
    # Define the prefix of the field to test and load expected results
    prefix = "registered_currently_sharing_meta_url"
    expected = load_expected(prefix)
    # Run the function to test
    result = CardanoPoolChecker.find_registered_currently_sharing_meta_url(register_data)
    # Save the output JSON to a file for further analysis
    save_result(prefix, result)
    # test result
    assert result == expected  # noqa: S101


def test_find_registered_currently_sharing_owners(register_data: list[dict[str, Any]]):
    """Tests that function find_registered_currently_sharing_owners returns the expected result.

    Args:
        register_data (list[dict[str, Any]]): The test register data.
    """
    # Define the prefix of the field to test and load expected results
    prefix = "registered_currently_sharing_owners"
    expected = load_expected(prefix)
    # Run the function to test
    result = CardanoPoolChecker.find_registered_currently_sharing_owners(register_data)
    # Save the output JSON to a file for further analysis
    save_result(prefix, result)
    # test result
    assert result == expected  # noqa: S101


def test_find_registered_currently_sharing_reward_addr(register_data: list[dict[str, Any]]):
    """Tests that function find_registered_currently_sharing_reward_addr returns the expected result.

    Args:
        register_data (list[dict[str, Any]]): The test register data.
    """
    # Define the prefix of the field to test and load expected results
    prefix = "registered_currently_sharing_reward_addr"
    expected = load_expected(prefix)
    # Run the function to test
    result = CardanoPoolChecker.find_registered_currently_sharing_reward_addr(register_data)
    # Save the output JSON to a file for further analysis
    save_result(prefix, result)
    # test result
    assert result == expected  # noqa: S101
