"""test module for build_register."""  # noqa: INP001
# see https://docs.pytest.org/en/latest/explanation/goodpractices.html#tests-outside-application-code
import json
import os

# from typing import Any  # noqa: ERA001
import pytest

from cardano_pool_checker.cardano_pool_checker_class import CardanoPoolChecker


@pytest.fixture()
def pools_path() -> str:
    """Fixture that loads the path for testing files.

    Returns:
        str: Returns a path.
    """
    return os.path.join(os.path.dirname(__file__))


@pytest.fixture()
def pools_list() -> list[dict[str, str]]:
    """Fixture that loads the testing pools list.

    Returns:
        list[dict[str, str]]: Return a list of pools.
    """
    with open(os.path.join(os.path.dirname(__file__), "pools_list_expected.json")) as file:
        return json.load(file)


@pytest.fixture()
def config_rules() -> dict[str, str | dict[str, str]]:
    """Fixture that loads a test set of MSPO config rules.

    Returns:
        dict[str, str|dict[str, str]]: Return a list with the pools register.
    """
    return [
        {
            # cardano-pool-checker default definition
            "rule": "wwwc or mtac or ownc or hstc or ip4c or ip6c or rwdc",
            "files": {
                "wwwc": "registered_currently_sharing_meta_json_homepage_expected.json",
                "mtac": "registered_currently_sharing_meta_url_expected.json",
                "ownc": "registered_currently_sharing_owners_expected.json",
                "hstc": "registered_currently_sharing_relay_hostname_expected.json",
                "ip4c": "registered_currently_sharing_relay_ipv4_expected.json",
                "ip6c": "registered_currently_sharing_relay_ipv6_expected.json",
                "rwdc": "registered_currently_sharing_reward_addr_expected.json",
            },
            "matching_file": "registered_multi_stake_pool_operators_r1_result.json",
            "non_matching_file": "registered_single_stake_pool_operators_r1_result.json",
        },
        {
            "rule": "ownc or hstc or ip4c or ip6c or rwdc or (own and hst)",
            "files": {
                "ownc": "registered_currently_sharing_owners_expected.json",
                "own": "registered_sharing_owners_expected.json",
                "hstc": "registered_currently_sharing_relay_hostname_expected.json",
                "hst": "registered_sharing_relay_hostname_expected.json",
                "ip4c": "registered_currently_sharing_relay_ipv4_expected.json",
                "ip6c": "registered_currently_sharing_relay_ipv6_expected.json",
                "rwdc": "registered_currently_sharing_reward_addr_expected.json",
            },
            "matching_file": "registered_multi_stake_pool_operators_r2_result.json",
            "non_matching_file": "registered_single_stake_pool_operators_r2_result.json",
        },
    ]


@pytest.fixture()
def classified_pools_expected() -> dict[str, list[dict[str, str | list[str]]]]:
    """Fixture that loads the expected classified pools after processing the list.

    Returns:
        dict[str, list[dict[str, str|list[str]]]]: Returns a dict with the classified pools.
    """
    with open(os.path.join(os.path.dirname(__file__), "pools_classified_expected.json")) as file:
        return json.load(file)


def test_build_classified_pools(
    pools_path: str,
    pools_list: list[dict[str, str]],
    config_rules: dict[str, str | dict[str, str]],
    classified_pools_expected: dict[str, list[dict[str, str | list[str]]]],
):
    """Tests that function build_classified_pools returns the expected result.

    Args:
        pools_path (str): Path for the pools files.
        pools_list (list[dict[str, str]]): List of stake pools.
        config_rules (dict[str, str | dict[str, str]]): Dictionary with rules to classify the pools.
        classified_pools_expected (dict[str, list[dict[str, str|list[str]]]]): The expected results.
    """
    cpc = CardanoPoolChecker()
    result = cpc.build_classified_pools(pools_path, pools_list, config_rules)
    # Save the output JSON to a file
    with open(os.path.join(os.path.dirname(__file__), "pools_classified_result.json"), "w") as output_file:
        json.dump(result, output_file, indent=4)
    # Compare the result with the expected value
    assert result == classified_pools_expected  # noqa: S101
