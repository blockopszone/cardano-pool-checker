"""Cardano Pool Checker configuration file."""
CPC_DATA_DIR: str = "pools/"
CPC_POOLS_UPDATES_FILENAME: str = "pools_updates.json"
CPC_POOLS_REGISTER_FILENAME: str = "pools_register.json"
CPC_POOLS_DNS_TRANSLATIONS_FILENAME: str = "pools_dns_translations.json"
CPC_POOLS_LIST_FILENAME: str = "pools_list.json"
CPC_SAVE_TO_DISK: bool = True
# Pool files URL prefix
CPC_POOLS_URL: str = (
    "https://raw.githubusercontent.com/blockopszone/cardano-pool-checker/main/cardano_pool_checker/pools/"
)
# Multi Stake Pool Operators definitions
CPC_MSPO_RULES = [
    {
        # cardano-pool-checker default definition
        "rule": "wwwc or mtac or ownc or hstc or ip4c or ip6c or rwdc",
        "files": {
            "wwwc": "registered_currently_sharing_meta_json_homepage.json",
            "mtac": "registered_currently_sharing_meta_url.json",
            "ownc": "registered_currently_sharing_owners.json",
            "hstc": "registered_currently_sharing_relay_hostname.json",
            "ip4c": "registered_currently_sharing_relay_ipv4.json",
            "ip6c": "registered_currently_sharing_relay_ipv6.json",
            "rwdc": "registered_currently_sharing_reward_addr.json",
        },
        "matching_file": "registered_multi_stake_pool_operators.json",
        "non_matching_file": "registered_single_stake_pool_operators.json",
    },
    # Feel free to add your own definitions below, adding a suffix to the result files.
    # {
    #    "rule": "ownc or hstc or ip4c or ip6c or rwdc or (own and hst)",
    #    "files": {"ownc": "registered_currently_sharing_owners.json",
    #              "own": "registered_sharing_owners.json",
    #              "hstc": "registered_currently_sharing_relay_hostname.json",
    #              "hst": "registered_sharing_relay_hostname.json",
    #              "ip4c": "registered_currently_sharing_relay_ipv4.json",
    #              "ip6c": "registered_currently_sharing_relay_ipv6.json",
    #              "rwdc": "registered_currently_sharing_reward_addr.json"
    #            },
    #    "matching_file": "registered_multi_stake_pool_operators_yourid.json",
    #    "non_matching_file": "registered_single_stake_pool_operators_yourid.json"
    # },
]

# Keywords allowed inside the rules definition.
CPC_MSPO_RULES_ALLOWED_KEYWORDS = [
    "and",
    "or",
    "www",
    "mta",
    "own",
    "hst",
    "ip4",
    "ip6",
    "rwd",
    "wwwc",
    "mtac",
    "ownc",
    "hstc",
    "ip4c",
    "ip6c",
    "rwdc",
]
