# cardano-pool-checker
JSON-based collection of historical Cardano stake pool registration data, lists of multi pool operators by different criteria and associated maintenance tools.  

## Install and usage
Please note that installing the software is optional since all the result JSON files are automatically updated in the repository on a daily basis and are ready for download. For instance, you can access a list of multi-stake pool operators, based on the site's criteria, at this [location](https://github.com/blockopszone/cardano-pool-checker/blob/main/cardano_pool_checker/pools/registered_multi_stake_pool_operators.json), or you can integrate it into an external application or directly download it from the command line using the following command:
```
curl https://raw.githubusercontent.com/blockopszone/cardano-pool-checker/main/cardano_pool_checker/pools/registered_multi_stake_pool_operators.json
```
You can also view the files that are live and available at this [location](https://github.com/blockopszone/cardano-pool-checker/tree/main/cardano_pool_checker/pools)

If the site's criteria for defining a multi-stake pool operator do not meet your requirements, you have the option to submit a Pull Request (PR) in the repository and add your own criteria to the [config file](https://github.com/blockopszone/cardano-pool-checker/blob/main/cardano_pool_checker/cardano_pool_checker_config.py) . The resultant files will be published then in the repository on a daily basis.

If, for any reason, your criteria are not accepted or if you prefer not to share them, or even if you need the lists updated more frequently than once a day, you can choose to install the package and run it locally. Below is an example of how to use the tool to generate the lists:
```
❯ pipx install cardano-pool-checker
❯ cardano-pool-checker

Cardano Pool Checker v1.0.0

[2023-10-24 19:52:03] Simple list with 3133 pools downloaded.
[2023-10-24 19:52:07] Pools updates: 13 new downloaded.
[2023-10-24 19:52:13] Pools register: rebuilt for 5733 stake pools.
[2023-10-24 20:01:08] Pools DNS translations: updated for 2119 currently tracked hostnames.
[2023-10-24 20:01:08] Found 189 entries for registered_currently_sharing_relay_hostname.
[2023-10-24 20:01:08] Found 133 entries for registered_currently_sharing_relay_ipv4.
[2023-10-24 20:01:08] Found 0 entries for registered_currently_sharing_relay_ipv6.
[2023-10-24 20:01:08] Found 123 entries for registered_currently_sharing_meta_json_homepage.
[2023-10-24 20:01:08] Found 14 entries for registered_currently_sharing_meta_url.
[2023-10-24 20:01:08] Found 14 entries for registered_currently_sharing_meta_url.
[2023-10-24 20:01:08] Found 28 entries for registered_currently_sharing_reward_addr.
[2023-10-24 20:01:08] Found 268 entries for registered_sharing_relay_hostname.
[2023-10-24 20:01:08] Found 302 entries for registered_sharing_relay_ipv4.
[2023-10-24 20:01:08] Found 0 entries for registered_sharing_relay_ipv6.
[2023-10-24 20:01:09] Found 154 entries for registered_sharing_meta_json_homepage.
[2023-10-24 20:01:09] Found 43 entries for registered_sharing_meta_url.
[2023-10-24 20:01:09] Found 42 entries for registered_sharing_owners.
[2023-10-24 20:01:09] Found 40 entries for registered_sharing_reward_addr.
[2023-10-24 20:01:19] Found 858 entries for registered_multi_stake_pool_operators.json rule.
[2023-10-24 20:01:19] Found 2275 entries for registered_single_stake_pool_operators.json rule.
```
  
Finally, the functions can also be run using your own scripts, for example: 
```
import cardano_pool_checker

my_checker = CardanoPoolChecker()
my_checker.update()
```  

## FAQ

### What is the criteria of this repo to differentiate the multi stake pool operators?
The criteria are defined as code in the [config file](https://github.com/blockopszone/cardano-pool-checker/blob/main/cardano_pool_checker/cardano_pool_checker_config.py), making them intentionally publicly available to apply a full disclosure policy in contrast to some websites listing pools using opaque rules. Basically, we consider a multi-stake pool operator to be one that is ***currently*** registered and ***currently*** sharing any of the following: the relay hostname, relay IPv4, relay IPv6, the metadata URL, the website, some owner, or the reward address.

### Are pools sharing the same relay by using an IP address in one pool and a hostname that resolves to the same IP address in another pool detected?
They should be, as the script maintains a translation table that stores not only the current hostname translations but also the previous ones. This information is used to compare with the IPv4 and IPv6 addresses and populate the files that track pools that are currently sharing or have ever shared.

### What to do if you disagree with the contents of some of the files
This code aims to compile the list in an objective and factual manner, with the only potentially subjective aspect being the definition of the rules. If you disagree with our rules, you are free to create your own and even host them here. That being said, the code may contain bugs, so please don't hesitate to open an issue if you believe there is an error.

## TO-DO
- Testing, testing and testing.
