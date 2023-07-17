# cardano-pool-checker
JSON-based collection of historical Cardano stake pool registration data, lists of multi pool operators by different criteria and associated maintenance tools.  

  
## Usage

Multi pools listings by reason can be found under the pools/ directory in JSON format, ready to download or to be consumed by an external application.   

See below an example of how to use the tool to generate the lists:
```
❯ python cardano_pool_checker.py

Cardano Pool Checker v.0.1.0

[2023-07-17 23:03:42] Simple list with 3185 pools downloaded.
[2023-07-17 23:03:43] Pools updates: 0 new downloaded.
[2023-07-17 23:03:52] Pools register: rebuilt for 5322 stake pools.
[2023-07-17 23:06:40] Pools DNS translations: updated for 1936 currently tracked hostnames.
[2023-07-17 23:06:40] Found 178 entries for registered_currently_sharing_relay_hostname.
[2023-07-17 23:06:40] Found 137 entries for registered_currently_sharing_relay_ipv4.
[2023-07-17 23:06:40] Found 0 entries for registered_currently_sharing_relay_ipv6.
[2023-07-17 23:06:41] Found 79 entries for registered_currently_sharing_meta_json_homepage.
[2023-07-17 23:06:41] Found 0 entries for registered_currently_sharing_meta_url.
[2023-07-17 23:06:41] Found 0 entries for registered_currently_sharing_meta_url.
[2023-07-17 23:06:41] Found 17 entries for registered_currently_sharing_reward_addr.
[2023-07-17 23:06:41] Found 254 entries for registered_sharing_relay_hostname.
[2023-07-17 23:06:41] Found 271 entries for registered_sharing_relay_ipv4.
[2023-07-17 23:06:41] Found 0 entries for registered_sharing_relay_ipv6.
[2023-07-17 23:06:41] Found 96 entries for registered_sharing_meta_json_homepage.
[2023-07-17 23:06:41] Found 0 entries for registered_sharing_meta_url.
[2023-07-17 23:06:42] Found 32 entries for registered_sharing_owners.
[2023-07-17 23:06:42] Found 30 entries for registered_sharing_reward_addr.
```
  
The functions can also be run from external scripts: 
```
import cardano_pool_checker

my_checker = CardanoPoolChecker()
my_checker.update()
```  

## TO-DO
- Method to summarise the list multi pools according to a given selction of rules. 
- Improve documentation, stub file and docstrings.
- Github action that updates the lists on a daily basis.
- Improve the unit tests.
