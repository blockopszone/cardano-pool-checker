import os
import json
import pytest

from cardano_pool_checker.cardano_pool_checker import CardanoPoolChecker


@pytest.fixture
def register_data():
    with open(os.path.join(os.path.dirname(__file__), "pools_register_expected.json"), "r") as file:
        data = json.load(file)
    return data


def load_expected(prefix):
    dir = os.path.dirname(__file__)
    with open(os.path.join(dir, prefix + "_expected.json"), "r") as file:
        data = json.load(file)
    return data


def save_result(prefix, data):
    dir = os.path.dirname(__file__)
    with open(os.path.join(dir, prefix + "_result.json"), "w") as file:
        json.dump(data, file, indent=4)


def test_find_registered_sharing_relay_hostname(register_data):
    # Define the prefix of the field to test and load expected results
    prefix = "registered_sharing_relay_hostname"
    expected = load_expected(prefix)
    # Run the function to test
    result = CardanoPoolChecker.find_registered_sharing_relay_hostname(register_data)
    # Save the output JSON to a file for further analysis
    save_result(prefix, result)
    # test result
    assert result == expected


def test_find_registered_sharing_relay_ipv4(register_data):
    # Define the prefix of the field to test and load expected results
    prefix = "registered_sharing_relay_ipv4"
    expected = load_expected(prefix)
    # Run the function to test
    result = CardanoPoolChecker.find_registered_sharing_relay_ipv4(register_data)
    # Save the output JSON to a file for further analysis
    save_result(prefix, result)
    # test result
    assert result == expected


def test_find_registered_sharing_relay_ipv6(register_data):
    # Define the prefix of the field to test and load expected results
    prefix = "registered_sharing_relay_ipv6"
    expected = load_expected(prefix)
    # Run the function to test
    result = CardanoPoolChecker.find_registered_sharing_relay_ipv6(register_data)
    # Save the output JSON to a file for further analysis
    save_result(prefix, result)
    # test result
    assert result == expected


def test_find_registered_sharing_meta_json_homepage(register_data):
    # Define the prefix of the field to test and load expected results
    prefix = "registered_sharing_meta_json_homepage"
    expected = load_expected(prefix)
    # Run the function to test
    result = CardanoPoolChecker.find_registered_sharing_meta_json_homepage(register_data)
    # Save the output JSON to a file for further analysis
    save_result(prefix, result)
    # test result
    assert result == expected


def test_find_registered_sharing_meta_url(register_data):
    # Define the prefix of the field to test and load expected results
    prefix = "registered_sharing_meta_url"
    expected = load_expected(prefix)
    # Run the function to test
    result = CardanoPoolChecker.find_registered_sharing_meta_url(register_data)
    # Save the output JSON to a file for further analysis
    save_result(prefix, result)
    # test result
    assert result == expected


def test_find_registered_sharing_owners(register_data):
    # Define the prefix of the field to test and load expected results
    prefix = "registered_sharing_owners"
    expected = load_expected(prefix)
    # Run the function to test
    result = CardanoPoolChecker.find_registered_sharing_owners(register_data)
    # Save the output JSON to a file for further analysis
    save_result(prefix, result)
    # test result
    assert result == expected


def test_find_registered_sharing_reward_addr(register_data):
    # Define the prefix of the field to test and load expected results
    prefix = "registered_sharing_reward_addr"
    expected = load_expected(prefix)
    # Run the function to test
    result = CardanoPoolChecker.find_registered_sharing_reward_addr(register_data)
    # Save the output JSON to a file for further analysis
    save_result(prefix, result)
    # test result
    assert result == expected
