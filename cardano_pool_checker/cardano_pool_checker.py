import os
import json
import urllib3
from urllib3.exceptions import HTTPError
import re
import ipaddress
import socket
import time
from datetime import datetime, timedelta

# import cardano_pool_checker.cardano_pool_checker_config as cpc_config
import cardano_pool_checker_config as cpc_config

http = urllib3.PoolManager()
urllib3.disable_warnings()


# OOP
class CardanoPoolChecker:
    def __init__(self, updates=None, register=None, translations=None):
        self._load_settings()
        if updates is None:
            self._load_updates()
        else:
            self._updates = updates
        if register is None:
            self._load_register()
        else:
            self._register = register
        if translations is None:
            self._load_translations()
        else:
            self._translations = translations

    @property
    def pools(self):
        return self._pools

    @pools.setter
    def pools(self, value):
        self._pools = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json(self.CPC_POOLS_LIST_FILENAME, value)

    @property
    def updates(self):
        return self._updates

    @updates.setter
    def updates(self, value):
        if self._check_updates(value):
            self._updates = value
        else:
            raise ValueError("Wrong updates data format.")
        if self.CPC_SAVE_TO_DISK:
            self._save_json(self.CPC_POOLS_UPDATES_FILENAME, value)

    @property
    def register(self):
        return self._register

    @register.setter
    def register(self, value):
        self._register = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json(self.CPC_POOLS_REGISTER_FILENAME, value)

    @property
    def translations(self):
        return self._translations

    @translations.setter
    def translations(self, value):
        self._translations = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json(self.CPC_POOLS_DNS_TRANSLATIONS_FILENAME, value)

    @property
    def last_block_time(self):
        last_block_time = 0
        if type(self._updates) == list:
            if self._updates:
                last_update = self._updates[-1]
            else:
                last_update = None
            if type(last_update) == dict and last_update.get("block_time") is not None:
                last_block_time = last_update["block_time"]
        return int(last_block_time)

    @property
    def registered_currently_sharing_relay_hostname(self):
        return self._registered_currently_sharing_relay_hostname

    @registered_currently_sharing_relay_hostname.setter
    def registered_currently_sharing_relay_hostname(self, value):
        self._registered_currently_sharing_relay_hostname = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_currently_sharing_relay_hostname.json", value)

    @property
    def registered_currently_sharing_relay_ipv4(self):
        return self._registered_currently_sharing_relay_ipv4

    @registered_currently_sharing_relay_ipv4.setter
    def registered_currently_sharing_relay_ipv4(self, value):
        self._registered_currently_sharing_relay_ipv4 = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_currently_sharing_relay_ipv4.json", value)

    @property
    def registered_currently_sharing_relay_ipv6(self):
        return self._registered_currently_sharing_relay_ipv6

    @registered_currently_sharing_relay_ipv6.setter
    def registered_currently_sharing_relay_ipv6(self, value):
        self._registered_currently_sharing_relay_ipv6 = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_currently_sharing_relay_ipv6.json", value)

    @property
    def registered_currently_sharing_meta_json_homepage(self):
        return self._registered_currently_sharing_meta_json_homepage

    @registered_currently_sharing_meta_json_homepage.setter
    def registered_currently_sharing_meta_json_homepage(self, value):
        self._registered_currently_sharing_meta_json_homepage = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_currently_sharing_meta_json_homepage.json", value)

    @property
    def registered_currently_sharing_meta_url(self):
        return self._registered_currently_sharing_meta_url

    @registered_currently_sharing_meta_url.setter
    def registered_currently_sharing_meta_url(self, value):
        self._registered_currently_sharing_meta_url = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_currently_sharing_meta_url.json", value)

    @property
    def registered_currently_sharing_owners(self):
        return self._registered_currently_sharing_owners

    @registered_currently_sharing_owners.setter
    def registered_currently_sharing_owners(self, value):
        self._registered_currently_sharing_owners = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_currently_sharing_owners.json", value)

    @property
    def registered_currently_sharing_reward_addr(self):
        return self._registered_currently_sharing_reward_addr

    @registered_currently_sharing_reward_addr.setter
    def registered_currently_sharing_reward_addr(self, value):
        self._registered_currently_sharing_reward_addr = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_currently_sharing_reward_addr.json", value)

    @property
    def registered_sharing_relay_hostname(self):
        return self._registered_sharing_relay_hostname

    @registered_sharing_relay_hostname.setter
    def registered_sharing_relay_hostname(self, value):
        self._registered_sharing_relay_hostname = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_sharing_relay_hostname.json", value)

    @property
    def registered_sharing_relay_ipv4(self):
        return self._registered_sharing_relay_ipv4

    @registered_sharing_relay_ipv4.setter
    def registered_sharing_relay_ipv4(self, value):
        self._registered_sharing_relay_ipv4 = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_sharing_relay_ipv4.json", value)

    @property
    def registered_sharing_relay_ipv6(self):
        return self._registered_sharing_relay_ipv6

    @registered_sharing_relay_ipv6.setter
    def registered_sharing_relay_ipv6(self, value):
        self._registered_sharing_relay_ipv6 = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_sharing_relay_ipv6.json", value)

    @property
    def registered_sharing_meta_json_homepage(self):
        return self._registered_sharing_meta_json_homepage

    @registered_sharing_meta_json_homepage.setter
    def registered_sharing_meta_json_homepage(self, value):
        self._registered_sharing_meta_json_homepage = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_sharing_meta_json_homepage.json", value)

    @property
    def registered_sharing_meta_url(self):
        return self._registered_sharing_meta_url

    @registered_sharing_meta_url.setter
    def registered_sharing_meta_url(self, value):
        self._registered_sharing_meta_url = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_sharing_meta_url.json", value)

    @property
    def registered_sharing_owners(self):
        return self._registered_sharing_owners

    @registered_sharing_owners.setter
    def registered_sharing_owners(self, value):
        self._registered_sharing_owners = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_sharing_owners.json", value)

    @property
    def registered_sharing_reward_addr(self):
        return self._registered_sharing_reward_addr

    @registered_sharing_reward_addr.setter
    def registered_sharing_reward_addr(self, value):
        self._registered_sharing_reward_addr = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_sharing_reward_addr.json", value)

    @staticmethod
    def _is_valid_url(url):
        pattern = r"^(https?://)?[a-zA-Z0-9]+([-.][a-zA-Z0-9]+)*\.[a-zA-Z]{2,6}([-.][a-zA-Z0-9]+)*$"
        return re.match(pattern, url) is not None

    @staticmethod
    def _is_reachable_url(url):
        http = urllib3.PoolManager()
        try:
            response = http.request("GET", url)
            return response.status == 200
        except HTTPError:
            return False

    @staticmethod
    def _unshorten_ipv6(address):
        try:
            ipv6 = ipaddress.IPv6Address(address)
            unshortened_address = ipv6.exploded
            return unshortened_address
        except ipaddress.AddressValueError:
            return None

    @staticmethod
    def _resolve_a_records(hostname):
        try:
            ip_addresses = set()
            for result in socket.getaddrinfo(hostname, None):
                ip_addresses.add(result[4][0])
            return list(ip_addresses)
        except socket.gaierror:
            return []

    def _load_settings(self):
        try:
            self.CPC_DATA_DIR = cpc_config.CPC_DATA_DIR
        except (NameError, AttributeError):
            self.CPC_DATA_DIR = "pools/"
        try:
            self.CPC_POOLS_UPDATES_FILENAME = cpc_config.CPC_POOLS_UPDATES_FILENAME
        except (NameError, AttributeError):
            self.CPC_POOLS_UPDATES_FILENAME = "pools_updates.json"
        try:
            self.CPC_POOLS_REGISTER_FILENAME = cpc_config.CPC_POOLS_REGISTER_FILENAME
        except (NameError, AttributeError):
            self.CPC_POOLS_REGISTER_FILENAME = "pools_register.json"
        try:
            self.CPC_POOLS_DNS_TRANSLATIONS_FILENAME = cpc_config.CPC_POOLS_DNS_TRANSLATIONS_FILENAME
        except (NameError, AttributeError):
            self.CPC_POOLS_DNS_TRANSLATIONS_FILENAME = "pools_dns_translations.json"
        try:
            self.CPC_POOLS_LIST_FILENAME = cpc_config.CPC_POOLS_LIST_FILENAME
        except (NameError, AttributeError):
            self.CPC_POOLS_LIST_FILENAME = "pools_list.json"
        try:
            self.CPC_SAVE_TO_DISK = cpc_config.CPC_SAVE_TO_DISK
        except (NameError, AttributeError):
            self.CPC_SAVE_TO_DISK = True

    def _load_updates(self):
        try:
            with open(
                os.path.join(os.path.dirname(__file__), self.CPC_DATA_DIR, self.CPC_POOLS_UPDATES_FILENAME), "r"
            ) as file:
                updates = json.load(file)
                if self._check_updates(updates):
                    self._updates = updates
                else:
                    raise ValueError("Wrong updates data format.")
        except FileNotFoundError:
            print("Updates File not found, creating a new one.")
            self.updates = []
        except IOError:
            raise IOError("Error reading the updates file.")

    def _load_register(self):
        try:
            with open(
                os.path.join(os.path.dirname(__file__), self.CPC_DATA_DIR, self.CPC_POOLS_REGISTER_FILENAME), "r"
            ) as file:
                self._register = json.load(file)
        except FileNotFoundError:
            print("Register File not found, creating a new one.")
            self.register = []
        except IOError:
            raise IOError("Error reading the register file.")

    def _load_translations(self):
        try:
            with open(
                os.path.join(os.path.dirname(__file__), self.CPC_DATA_DIR, self.CPC_POOLS_DNS_TRANSLATIONS_FILENAME),
                "r",
            ) as file:
                self._translations = json.load(file)
        except FileNotFoundError:
            print("Translations File not found, creating a new one.")
            self.translations = {}
        except IOError:
            raise IOError("Error reading the translations file.")

    @staticmethod
    def _download_json(url):
        resp = http.request("GET", url, redirect=True)
        if str(resp.status) == "200":
            obj = json.loads(resp.data)
            return obj
        else:
            print("An error occurred while downloading data")
            exit

    def _save_json(self, filename, data):
        directory = os.path.join(os.path.dirname(__file__), self.CPC_DATA_DIR)
        os.makedirs(directory, exist_ok=True)  # Create the directory if it doesn't exist
        file_path = os.path.join(directory, filename)
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

    def info(self):
        print("\nCardano Pool Checker v.0.1.0\n")

    def update(self):
        self.info()
        # Download a simple list of pools
        self.set_pools()
        # Update the updates incrementally.
        since = self.last_block_time
        new_updates = self.build_updates(since)
        if new_updates:
            if self._updates:
                # setter decorator is not triggered by .extend
                # self.updates.extend(new_updates)
                self.updates = self.updates + new_updates
            else:
                self.updates = new_updates
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Pools updates: {len(new_updates)} new downloaded.")
        # Icremental registry updates needs more testing, just passing
        # the current register and the new updates depends on the good
        # state of the register file. It may be required to look in the
        # register for the last block_time to be able to enforce a correct
        # sync, and this, among others, reduces the cost benefits of
        # incremental mode. Some benchmarking is needed.
        # self.register = self.build_register(new_updates, self._register)
        # For now, rebuild the register entirely with each update.
        self.set_register()
        self.set_translations()
        self.set_all_sharing()

    @classmethod
    def build_pools(cls):
        # get pool list
        koios_pool_list = []
        pool_range = range(0, 100000, 1000)
        for offset in pool_range:
            # print ("offset is %s" % offset)
            url = "https://api.koios.rest/api/v0/pool_list?offset=" + str(offset) + "&limit=1000"
            fetched = cls._download_json(url)
            koios_pool_list.extend(fetched)
            # print ("fetched %s entries" % len(fetched))
            if len(fetched) < 1000:
                break
        return koios_pool_list

    def set_pools(self):
        self.pools = self.build_pools()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Simple list with {len(self._pools)} pools downloaded.")

    @staticmethod
    def _check_updates(updates=[]):
        old_time = 0
        result = True
        if type(updates) == list:
            for update in updates:
                if type(update) == dict and update.get("block_time") is not None:
                    if update["block_time"] >= old_time:
                        old_time = update["block_time"]
                    else:
                        result = False
                        break
        else:
            result = False
        return result

    @classmethod
    def build_updates(cls, since=0):
        # Get pool updates data using koios
        # curl -s "https://api.koios.rest/api/v0/pool_updates?block_time=gt.1&order=block_time.asc&limit=500"
        # -H "Range: 0-499"
        updates_list = []
        if type(since) == int:
            batchSize = 1000
            iteration = 0
            while True:
                iteration += 1
                fetched = cls._download_json(
                    "https://api.koios.rest/api/v0/pool_updates?block_time=gt."
                    + str(since)
                    + "&order=block_time.asc&offset="
                    + str(batchSize * iteration)
                    + "&limit="
                    + str(batchSize)
                )
                updates_list.extend(fetched)
                if len(fetched) < batchSize:
                    break
        return list(updates_list)

    def set_updates(self, since=None):
        if since is None:
            since = self.last_block_time
        new_updates = self.build_updates(since)
        self.updates.extend(new_updates)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Pools updates: {len(new_updates)} new downloaded.")

    @staticmethod
    def build_register(updates=[], register=[]):
        # register can be passed as a parameter to load the current values
        # so if incremental updates are also passed instead of the entire list,
        # the register file can be built incrementally.
        #
        # This option is experimental, it requires better input param checks,
        # and some benchmarking tests because possibly it's not worth to use,
        # because with the actual code the current register needs to be fully
        # processed anyway to match the expected dict format.
        #
        # Start processing the register parameter
        register_dict = {}
        if register is not None and type(register) == list:
            for register_pool in register:
                if type(register_pool) == dict and register_pool.get("pool_id_bech32") is not None:
                    register_dict[register_pool["pool_id_bech32"]] = register_pool
                else:  # abort if some unexpected element is found
                    register_dict = {}
                    break
        # Start processing the updates
        for update in updates:
            pool_id_bech32 = update["pool_id_bech32"]
            pool_id_hex = update["pool_id_hex"]
            if pool_id_bech32 not in register_dict:
                register_dict[pool_id_bech32] = {
                    "pool_id_bech32": pool_id_bech32,
                    "pool_id_hex": pool_id_hex,
                    "active_epoch_no": update["active_epoch_no"],
                    "vrf_key_hash": update["vrf_key_hash"],
                    "margin": update["margin"],
                    "margin_log": [
                        {"tx_hash": update["tx_hash"], "block_time": update["block_time"], "margin": update["margin"]}
                    ],
                    "fixed_cost": update["fixed_cost"],
                    "fixed_cost_log": [
                        {
                            "tx_hash": update["tx_hash"],
                            "block_time": update["block_time"],
                            "fixed_cost": update["fixed_cost"],
                        }
                    ],
                    "pledge": update["pledge"],
                    "pledge_log": [
                        {"tx_hash": update["tx_hash"], "block_time": update["block_time"], "pledge": update["pledge"]}
                    ],
                    "reward_addr": update["reward_addr"],
                    "reward_addr_log": [
                        {
                            "tx_hash": update["tx_hash"],
                            "block_time": update["block_time"],
                            "reward_addr": update["reward_addr"],
                        }
                    ],
                    "owners": update["owners"],
                    "owners_log": [
                        {"tx_hash": update["tx_hash"], "block_time": update["block_time"], "owners": update["owners"]}
                    ],
                    "relays": update["relays"],
                    "relays_log": [
                        {"tx_hash": update["tx_hash"], "block_time": update["block_time"], "relays": update["relays"]}
                    ],
                    "meta_url": update["meta_url"],
                    "meta_url_log": [
                        {
                            "tx_hash": update["tx_hash"],
                            "block_time": update["block_time"],
                            "meta_url": update["meta_url"],
                        }
                    ],
                    "meta_hash": update["meta_hash"],
                    "meta_hash_log": [
                        {
                            "tx_hash": update["tx_hash"],
                            "block_time": update["block_time"],
                            "meta_hash": update["meta_hash"],
                        }
                    ],
                    "meta_json": update["meta_json"],
                    "meta_json_log": [
                        {
                            "tx_hash": update["tx_hash"],
                            "block_time": update["block_time"],
                            "meta_json": update["meta_json"],
                        }
                    ],
                    "pool_status": update["pool_status"],
                    "retiring_epoch": update["retiring_epoch"],
                }
            else:
                pool = register_dict[pool_id_bech32]
                # Update margin
                if pool["margin"] != update["margin"]:
                    pool["margin"] = update["margin"]
                    pool["margin_log"].append(
                        {"tx_hash": update["tx_hash"], "block_time": update["block_time"], "margin": update["margin"]}
                    )
                # Update fixed_cost
                if pool["fixed_cost"] != update["fixed_cost"]:
                    pool["fixed_cost"] = update["fixed_cost"]
                    pool["fixed_cost_log"].append(
                        {
                            "tx_hash": update["tx_hash"],
                            "block_time": update["block_time"],
                            "fixed_cost": update["fixed_cost"],
                        }
                    )
                # Update pledge
                if pool["pledge"] != update["pledge"]:
                    pool["pledge"] = update["pledge"]
                    pool["pledge_log"].append(
                        {"tx_hash": update["tx_hash"], "block_time": update["block_time"], "pledge": update["pledge"]}
                    )
                # Update reward_addr
                if pool["reward_addr"] != update["reward_addr"]:
                    pool["reward_addr"] = update["reward_addr"]
                    pool["reward_addr_log"].append(
                        {
                            "tx_hash": update["tx_hash"],
                            "block_time": update["block_time"],
                            "reward_addr": update["reward_addr"],
                        }
                    )
                # Update owners
                if pool["owners"] != update["owners"]:
                    pool["owners"] = update["owners"]
                    pool["owners_log"].append(
                        {"tx_hash": update["tx_hash"], "block_time": update["block_time"], "owners": update["owners"]}
                    )
                # Update relays
                if pool["relays"] != update["relays"]:
                    pool["relays"] = update["relays"]
                    pool["relays_log"].append(
                        {"tx_hash": update["tx_hash"], "block_time": update["block_time"], "relays": update["relays"]}
                    )
                # Update meta_url
                if pool["meta_url"] != update["meta_url"]:
                    pool["meta_url"] = update["meta_url"]
                    pool["meta_url_log"].append(
                        {
                            "tx_hash": update["tx_hash"],
                            "block_time": update["block_time"],
                            "meta_url": update["meta_url"],
                        }
                    )
                # Update meta_hash
                if pool["meta_hash"] != update["meta_hash"]:
                    pool["meta_hash"] = update["meta_hash"]
                    pool["meta_hash_log"].append(
                        {
                            "tx_hash": update["tx_hash"],
                            "block_time": update["block_time"],
                            "meta_hash": update["meta_hash"],
                        }
                    )
                # Update meta_json
                if pool["meta_json"] != update["meta_json"]:
                    pool["meta_json"] = update["meta_json"]
                    pool["meta_json_log"].append(
                        {
                            "tx_hash": update["tx_hash"],
                            "block_time": update["block_time"],
                            "meta_json": update["meta_json"],
                        }
                    )
                # Update pool_status
                if pool["pool_status"] != update["pool_status"]:
                    pool["pool_status"] = update["pool_status"]
                # Update retiring_epoch
                if pool["retiring_epoch"] != update["retiring_epoch"]:
                    pool["retiring_epoch"] = update["retiring_epoch"]
        return list(register_dict.values())

    def set_register(self, updates=None):
        if updates is None:
            updates = self._updates
        self.register = self.build_register(updates)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Pools register: rebuilt for {len(self._register)} stake pools.")

    @classmethod
    def build_translations(cls, register=[], translations={}):
        # Iterate the registered pools to create a list of IPs from hostnames
        registered_pools = [pool for pool in register if pool.get("pool_status") == "registered"]
        for pool in registered_pools:
            for relay in pool["relays"]:
                if relay["dns"] is not None:
                    resolved_ips = cls._resolve_a_records(relay["dns"])  # Assuming resolve_a_records() is defined
                    my_time = time.time()
                    for resolved_ip in resolved_ips:
                        resolved_ip_obj = ipaddress.ip_address(resolved_ip)
                        if translations.get(relay["dns"]) is None:
                            translations[relay["dns"]] = {}
                        if resolved_ip_obj.version == 4:
                            if translations[relay["dns"]].get("4") is None:
                                translations[relay["dns"]]["4"] = {}
                            if resolved_ip not in translations[relay["dns"]]["4"]:
                                translations[relay["dns"]]["4"][resolved_ip] = {}
                            if pool["pool_id_bech32"] not in translations[relay["dns"]]["4"][resolved_ip]:
                                translations[relay["dns"]]["4"][resolved_ip][pool["pool_id_bech32"]] = {
                                    "first": my_time,
                                    "last": my_time,
                                }
                            else:
                                translations[relay["dns"]]["4"][resolved_ip][pool["pool_id_bech32"]]["last"] = my_time
                        elif resolved_ip_obj.version == 6:
                            resolved_ipv6 = cls._unshorten_ipv6(resolved_ip)
                            if translations[relay["dns"]].get("6") is None:
                                translations[relay["dns"]]["6"] = {}
                            if resolved_ipv6 not in translations[relay["dns"]]["6"]:
                                translations[relay["dns"]]["6"][resolved_ipv6] = {}
                            if pool["pool_id_bech32"] not in translations[relay["dns"]]["6"][resolved_ipv6]:
                                translations[relay["dns"]]["6"][resolved_ipv6][pool["pool_id_bech32"]] = {
                                    "first": my_time,
                                    "last": my_time,
                                }
                            else:
                                translations[relay["dns"]]["6"][resolved_ipv6][pool["pool_id_bech32"]]["last"] = my_time
        return translations

    def set_translations(self, register=None, translations=None):
        if register is None:
            register = self._register
        if translations is None:
            translations = self._translations
        self.translations = self.build_translations(register, translations)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[{current_time}] Pools DNS translations: updated for {len(self._translations)} currently tracked hostnames."
        )

    def set_all_sharing(self, register=None, translations=None):
        self.set_registered_currently_sharing_relay_hostname(register)
        self.set_registered_currently_sharing_relay_ipv4(register, translations)
        self.set_registered_currently_sharing_relay_ipv6(register, translations)
        self.set_registered_currently_sharing_meta_json_homepage(register)
        self.set_registered_currently_sharing_meta_url(register)
        self.set_registered_currently_sharing_owners(register)
        self.set_registered_currently_sharing_reward_addr(register)
        self.set_registered_sharing_relay_hostname(register)
        self.set_registered_sharing_relay_ipv4(register, translations)
        self.set_registered_sharing_relay_ipv6(register, translations)
        self.set_registered_sharing_meta_json_homepage(register)
        self.set_registered_sharing_meta_url(register)
        self.set_registered_sharing_owners(register)
        self.set_registered_sharing_reward_addr(register)

    def set_registered_currently_sharing(self, register=None, translations=None):
        self.set_registered_currently_sharing_relay_hostname(register)
        self.set_registered_currently_sharing_relay_ipv4(register, translations)
        self.set_registered_currently_sharing_relay_ipv6(register, translations)
        self.set_registered_currently_sharing_meta_json_homepage(register)
        self.set_registered_currently_sharing_meta_url(register)
        self.set_registered_currently_sharing_owners(register)
        self.set_registered_currently_sharing_reward_addr(register)

    def set_registered_sharing(self, register=None, translations=None):
        self.set_registered_sharing_relay_hostname(register)
        self.set_registered_sharing_relay_ipv4(register, translations)
        self.set_registered_sharing_relay_ipv6(register, translations)
        self.set_registered_sharing_meta_json_homepage(register)
        self.set_registered_sharing_meta_url(register)
        self.set_registered_sharing_owners(register)
        self.set_registered_sharing_reward_addr(register)

    @staticmethod
    def find_registered_currently_sharing_relay_hostname(register=[]):
        # init result dict
        hostnames = {}
        if type(register) == list:
            # iterate the registered pools to create a dict with values and a list with the ids containing them
            registered_pools = [
                pool for pool in register if type(pool) == dict and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if type(pool) == dict and pool.get("relays") is not None:
                    if type(pool["relays"]) == list:
                        for relay in pool["relays"]:
                            if type(relay) == dict and relay.get("dns") is not None:
                                if relay["dns"] in hostnames:
                                    # should be always true for currently functions but just in case...
                                    if (
                                        pool.get("pool_id_bech32") is not None
                                        and pool["pool_id_bech32"] not in hostnames[relay["dns"]]
                                    ):
                                        hostnames[relay["dns"]].append(pool["pool_id_bech32"])
                                else:
                                    hostnames[relay["dns"]] = [pool["pool_id_bech32"]]
        # Filter the dictionary to include only the hostnames present in multiple pools
        shared = {value: value_pools for value, value_pools in hostnames.items() if len(value_pools) > 1}
        return shared

    def set_registered_currently_sharing_relay_hostname(self, register=None):
        if register is None:
            register = self._register
        self.registered_currently_sharing_relay_hostname = self.find_registered_currently_sharing_relay_hostname(
            register
        )
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[{current_time}] Found {len(self._registered_currently_sharing_relay_hostname)} entries for registered_currently_sharing_relay_hostname."
        )

    @staticmethod
    def find_registered_currently_sharing_relay_ipv4(register=[], translations={}):
        # init result dict
        ipv4_addresses = {}
        # iterate the registered pools to create a list of values and the ids containing them
        if type(register) == list:
            registered_pools = [
                pool for pool in register if type(pool) == dict and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if type(pool) == dict and pool.get("relays") is not None:
                    if type(pool["relays"]) == list:
                        for relay in pool["relays"]:
                            if type(relay) == dict and relay.get("ipv4") is not None:
                                if relay["ipv4"] in ipv4_addresses:
                                    # should be always true for currently functions but just in case...
                                    if (
                                        pool.get("pool_id_bech32") is not None
                                        and pool["pool_id_bech32"] not in ipv4_addresses[relay["ipv4"]]
                                    ):
                                        ipv4_addresses[relay["ipv4"]].append(pool["pool_id_bech32"])
                                else:
                                    ipv4_addresses[relay["ipv4"]] = [pool["pool_id_bech32"]]
        # iterate the list of relay hostname translations to also look among the
        # recent (less than 4h) resolved IPs for sharing conditions
        if type(translations) == dict and translations.get("4") is not None:
            for hostname, hostname_data in translations:
                if type(hostname_data) == dict and hostname_data.get("4") is not None:
                    for resolved_ip, resolved_ip_data in hostname_data["4"]:
                        if type(resolved_ip_data) == dict:
                            for pool, pool_data in resolved_ip_data:
                                if type(pool_data) == dict and pool_data.get("last") is not None:
                                    if pool_data["last"] > datetime.now() - timedelta(hours=4):
                                        if resolved_ip in ipv4_addresses:
                                            if pool is not None and pool not in ipv4_addresses[resolved_ip]:
                                                ipv4_addresses[resolved_ip].append(pool)
                                        else:
                                            ipv4_addresses[resolved_ip] = [pool]
        # Filter the dictionary to include only the IPv4 addresses present in multiple pools
        shared = {value: value_pools for value, value_pools in ipv4_addresses.items() if len(value_pools) > 1}
        return shared

    def set_registered_currently_sharing_relay_ipv4(self, register=None, translations=None):
        if register is None:
            register = self._register
        if translations is None:
            translations = self._translations
        self.registered_currently_sharing_relay_ipv4 = self.find_registered_currently_sharing_relay_ipv4(
            register, translations
        )
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[{current_time}] Found {len(self._registered_currently_sharing_relay_ipv4)} entries for registered_currently_sharing_relay_ipv4."
        )

    @classmethod
    def find_registered_currently_sharing_relay_ipv6(cls, register=[], translations={}):
        # init result dict
        ipv6_addresses = {}
        if type(register) == list:
            # iterate the registered pools to create a list of values and the ids containing them
            registered_pools = [
                pool for pool in register if type(pool) == dict and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if type(pool) == dict and pool.get("relays") is not None:
                    if type(pool["relays"]) == list:
                        for relay in pool["relays"]:
                            if type(relay) == dict and relay.get("ipv6") is not None:
                                full_ipv6 = cls._unshorten_ipv6(relay["ipv6"])
                                if full_ipv6 is not None:
                                    if full_ipv6 in ipv6_addresses:
                                        # should be always true for currently functions but just in case...
                                        if (
                                            pool.get("pool_id_bech32") is not None
                                            and pool["pool_id_bech32"] not in ipv6_addresses[full_ipv6]
                                        ):
                                            ipv6_addresses[full_ipv6].append(pool["pool_id_bech32"])
                                    else:
                                        ipv6_addresses[full_ipv6] = [pool["pool_id_bech32"]]
        # iterate the list of relay hostname translations to also look among the
        # recent (less than 4h) resolved IPs for sharing conditions
        if type(translations) == dict and translations.get("6") is not None:
            for hostname, hostname_data in translations:
                if type(hostname_data) == dict and hostname_data.get("6") is not None:
                    for resolved_ip, resolved_ip_data in hostname_data["6"]:
                        full_ipv6 = cls._unshorten_ipv6(resolved_ip)
                        if type(resolved_ip_data) == dict:
                            for pool, pool_data in resolved_ip_data:
                                if type(pool_data) == dict and pool_data.get("last") is not None:
                                    if pool_data["last"] > datetime.now() - timedelta(hours=4):
                                        if full_ipv6 in ipv6_addresses:
                                            if pool is not None and pool not in ipv6_addresses[full_ipv6]:
                                                ipv6_addresses[full_ipv6].append(pool)
                                        else:
                                            ipv6_addresses[full_ipv6] = [pool]
        # Filter the dictionary to include only the IPv6 addresses present in multiple pools
        shared = {value: value_pools for value, value_pools in ipv6_addresses.items() if len(value_pools) > 1}
        return shared

    def set_registered_currently_sharing_relay_ipv6(self, register=None, translations=None):
        if register is None:
            register = self._register
        if translations is None:
            translations = self._translations
        self.registered_currently_sharing_relay_ipv6 = self.find_registered_currently_sharing_relay_ipv6(
            register, translations
        )
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[{current_time}] Found {len(self._registered_currently_sharing_relay_ipv6)} entries for registered_currently_sharing_relay_ipv6."
        )

    @classmethod
    def find_registered_currently_sharing_meta_json_homepage(cls, register=[]):
        # init result dict
        homepages = {}
        if type(register) == list:
            # iterate the registered pools to create a list of values and the ids containing them
            registered_pools = [
                pool for pool in register if type(pool) == dict and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if type(pool) == dict and pool.get("meta_json") is not None:
                    if (
                        type(pool["meta_json"]) == dict
                        and pool["meta_json"].get("homepage") is not None
                        and cls._is_valid_url(pool["meta_json"]["homepage"])
                    ):
                        if pool["meta_json"]["homepage"] in homepages:
                            # should be always true for currently functions but just in case...
                            if (
                                pool.get("pool_id_bech32") is not None
                                and pool["pool_id_bech32"] not in homepages[pool["meta_json"]["homepage"]]
                            ):
                                homepages[pool["meta_json"]["homepage"]].append(pool["pool_id_bech32"])
                        else:
                            homepages[pool["meta_json"]["homepage"]] = [pool["pool_id_bech32"]]
        # Filter the dictionary to include only the homepages present in multiple pools
        shared = {value: value_pools for value, value_pools in homepages.items() if len(value_pools) > 1}
        return shared

    def set_registered_currently_sharing_meta_json_homepage(self, register=None):
        if register is None:
            register = self._register
        self.registered_currently_sharing_meta_json_homepage = (
            self.find_registered_currently_sharing_meta_json_homepage(register)
        )
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[{current_time}] Found {len(self._registered_currently_sharing_meta_json_homepage)} entries for registered_currently_sharing_meta_json_homepage."
        )

    @classmethod
    def find_registered_currently_sharing_meta_url(cls, register=[]):
        # init result dict
        meta_urls = {}
        if type(register) == list:
            # iterate the registered pools to create a list of values and the ids containing them
            registered_pools = [
                pool for pool in register if type(pool) == dict and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if type(pool) == dict and pool.get("meta_url") is not None and cls._is_valid_url(pool["meta_url"]):
                    if pool["meta_url"] in meta_urls:
                        # should be always true for currently functions but just in case...
                        if (
                            pool.get("pool_id_bech32") is not None
                            and pool["pool_id_bech32"] not in meta_urls[pool["meta_url"]]
                        ):
                            meta_urls[pool["meta_url"]].append(pool["pool_id_bech32"])
                    else:
                        meta_urls[pool["meta_url"]] = [pool["pool_id_bech32"]]
        # Filter the dictionary to include only the meta_urls present in multiple pools
        shared = {value: value_pools for value, value_pools in meta_urls.items() if len(value_pools) > 1}
        return shared

    def set_registered_currently_sharing_meta_url(self, register=None):
        if register is None:
            register = self._register
        self.registered_currently_sharing_meta_url = self.find_registered_currently_sharing_meta_url(register)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[{current_time}] Found {len(self._registered_currently_sharing_meta_url)} entries for registered_currently_sharing_meta_url."
        )

    @staticmethod
    def find_registered_currently_sharing_owners(register=[]):
        # init result dict
        owners = {}
        if type(register) == list:
            # iterate the registered pools to create a list of values and the ids containing them
            registered_pools = [
                pool for pool in register if type(pool) == dict and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if type(pool) == dict and pool.get("owners") is not None and type(pool["owners"]) == list:
                    for owner in pool["owners"]:
                        if owner in owners:
                            # should be always true for currently functions but just in case...
                            if pool.get("pool_id_bech32") is not None and pool["pool_id_bech32"] not in owners[owner]:
                                owners[owner].append(pool["pool_id_bech32"])
                        else:
                            owners[owner] = [pool["pool_id_bech32"]]
        # Filter the dictionary to include only the owners present in multiple pools
        shared = {value: value_pools for value, value_pools in owners.items() if len(value_pools) > 1}
        return shared

    def set_registered_currently_sharing_owners(self, register=None):
        if register is None:
            register = self._register
        self.registered_currently_sharing_owners = self.find_registered_currently_sharing_owners(register)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[{current_time}] Found {len(self._registered_currently_sharing_meta_url)} entries for registered_currently_sharing_meta_url."
        )

    @staticmethod
    def find_registered_currently_sharing_reward_addr(register=[]):
        # init result dict
        addresses = {}
        if type(register) == list:
            # iterate the registered pools to create a list of values and the ids containing them
            registered_pools = [
                pool for pool in register if type(pool) == dict and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if type(pool) == dict and pool.get("reward_addr") is not None:
                    if pool["reward_addr"] in addresses:
                        # should be always true for currently functions but just in case...
                        if (
                            pool.get("pool_id_bech32") is not None
                            and pool["pool_id_bech32"] not in addresses[pool["reward_addr"]]
                        ):
                            addresses[pool["reward_addr"]].append(pool["pool_id_bech32"])
                    else:
                        addresses[pool["reward_addr"]] = [pool["pool_id_bech32"]]
        # Filter the dictionary to include only the hostnames present in multiple pools
        shared = {value: value_pools for value, value_pools in addresses.items() if len(value_pools) > 1}
        return shared

    def set_registered_currently_sharing_reward_addr(self, register=None):
        if register is None:
            register = self._register
        self.registered_currently_sharing_reward_addr = self.find_registered_currently_sharing_reward_addr(register)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[{current_time}] Found {len(self._registered_currently_sharing_reward_addr)} entries for registered_currently_sharing_reward_addr."
        )

    @staticmethod
    def find_registered_sharing_relay_hostname(register=[]):
        # init result dict
        hostnames = {}
        if type(register) == list:
            # iterate the registered pools to create a dict with values and a list with the ids containing them
            registered_pools = [
                pool for pool in register if type(pool) == dict and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if type(pool) == dict and pool.get("relays_log") is not None and type(pool["relays_log"]) == list:
                    for log in pool["relays_log"]:
                        if type(log) == dict and log.get("relays") is not None and type(log["relays"]) == list:
                            for relay in log["relays"]:
                                if type(relay) == dict and relay.get("dns") is not None:
                                    if relay["dns"] in hostnames:
                                        if (
                                            pool.get("pool_id_bech32") is not None
                                            and pool["pool_id_bech32"] not in hostnames[relay["dns"]]
                                        ):
                                            hostnames[relay["dns"]].append(pool["pool_id_bech32"])
                                    else:
                                        hostnames[relay["dns"]] = [pool["pool_id_bech32"]]
        # Filter the dictionary to include only the hostnames present in multiple pools
        shared = {value: value_pools for value, value_pools in hostnames.items() if len(value_pools) > 1}
        return shared

    def set_registered_sharing_relay_hostname(self, register=None):
        if register is None:
            register = self._register
        self.registered_sharing_relay_hostname = self.find_registered_sharing_relay_hostname(register)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[{current_time}] Found {len(self._registered_sharing_relay_hostname)} entries for registered_sharing_relay_hostname."
        )

    @staticmethod
    def find_registered_sharing_relay_ipv4(register=[], translations={}):
        # init result dict
        ipv4_addresses = {}
        if type(register) == list:
            # iterate the registered pools to create a dict with values and a list with the ids containing them
            registered_pools = [
                pool for pool in register if type(pool) == dict and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if type(pool) == dict and pool.get("relays_log") is not None and type(pool["relays_log"]) == list:
                    for log in pool["relays_log"]:
                        if type(log) == dict and log.get("relays") is not None and type(log["relays"]) == list:
                            for relay in log["relays"]:
                                if type(relay) == dict and relay.get("ipv4") is not None:
                                    if relay["ipv4"] in ipv4_addresses:
                                        if (
                                            pool.get("pool_id_bech32") is not None
                                            and pool["pool_id_bech32"] not in ipv4_addresses[relay["ipv4"]]
                                        ):
                                            ipv4_addresses[relay["ipv4"]].append(pool["pool_id_bech32"])
                                    else:
                                        ipv4_addresses[relay["ipv4"]] = [pool["pool_id_bech32"]]
        # iterate the list of relay hostname translations to also look among the
        # resolved IPs for sharing conditions
        if type(translations) == dict and translations.get("4") is not None:
            for hostname, hostname_data in translations:
                if type(hostname_data) == dict and hostname_data.get("4") is not None:
                    for resolved_ip, resolved_ip_data in hostname_data["4"]:
                        if type(resolved_ip_data) == dict:
                            for pool in resolved_ip_data:
                                if resolved_ip in ipv4_addresses:
                                    if pool is not None and pool not in ipv4_addresses[resolved_ip]:
                                        ipv4_addresses[resolved_ip].append(pool)
                                else:
                                    ipv4_addresses[resolved_ip] = [pool]
        # Filter the dictionary to include only the IPv4 addresses present in multiple pools
        shared = {value: value_pools for value, value_pools in ipv4_addresses.items() if len(value_pools) > 1}
        return shared

    def set_registered_sharing_relay_ipv4(self, register=None, translations=None):
        if register is None:
            register = self._register
        if translations is None:
            translations = self._translations
        self.registered_sharing_relay_ipv4 = self.find_registered_sharing_relay_ipv4(register, translations)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[{current_time}] Found {len(self._registered_sharing_relay_ipv4)} entries for registered_sharing_relay_ipv4."
        )

    @classmethod
    def find_registered_sharing_relay_ipv6(cls, register=[], translations={}):
        # init result dict
        ipv6_addresses = {}
        if type(register) == list:
            # iterate the registered pools to create a dict with values and a list with the ids containing them
            registered_pools = [
                pool for pool in register if type(pool) == dict and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if type(pool) == dict and pool.get("relays_log") is not None and type(pool["relays_log"]) == list:
                    for log in pool["relays_log"]:
                        if type(log) == dict and log.get("relays") is not None and type(log["relays"]) == list:
                            for relay in log["relays"]:
                                if type(relay) == dict and relay.get("ipv6") is not None:
                                    full_ipv6 = cls._unshorten_ipv6(relay["ipv6"])
                                    if full_ipv6 is not None:
                                        if full_ipv6 in ipv6_addresses:
                                            if (
                                                pool.get("pool_id_bech32") is not None
                                                and pool["pool_id_bech32"] not in ipv6_addresses[full_ipv6]
                                            ):
                                                ipv6_addresses[full_ipv6].append(pool["pool_id_bech32"])
                                        else:
                                            ipv6_addresses[full_ipv6] = [pool["pool_id_bech32"]]
        # iterate the list of relay hostname translations to also look among the
        # resolved IPs for sharing conditions
        if type(translations) == dict and translations.get("6") is not None:
            for hostname, hostname_data in translations:
                if type(hostname_data) == dict and hostname_data.get("6") is not None:
                    for resolved_ip, resolved_ip_data in hostname_data["6"]:
                        full_ipv6 = cls._unshorten_ipv6(resolved_ip)
                        if type(resolved_ip_data) == dict:
                            for pool in resolved_ip_data:
                                if full_ipv6 in ipv6_addresses:
                                    if pool is not None and pool not in ipv6_addresses[full_ipv6]:
                                        ipv6_addresses[full_ipv6].append(pool)
                                else:
                                    ipv6_addresses[full_ipv6] = [pool]
        # Filter the dictionary to include only the IPv6 addresses present in multiple pools
        shared = {value: value_pools for value, value_pools in ipv6_addresses.items() if len(value_pools) > 1}
        return shared

    def set_registered_sharing_relay_ipv6(self, register=None, translations=None):
        if register is None:
            register = self._register
        if translations is None:
            translations = self._translations
        self.registered_sharing_relay_ipv6 = self.find_registered_sharing_relay_ipv6(register, translations)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[{current_time}] Found {len(self._registered_sharing_relay_ipv6)} entries for registered_sharing_relay_ipv6."
        )

    @classmethod
    def find_registered_sharing_meta_json_homepage(cls, register=[]):
        # init result dict
        homepages = {}
        if type(register) == list:
            # iterate the registered pools to create a dict with values and a list with the ids containing them
            registered_pools = [
                pool for pool in register if type(pool) == dict and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if type(pool) == dict and pool.get("meta_json_log") is not None and type(pool["meta_json_log"]) == list:
                    for log in pool["meta_json_log"]:
                        if type(log) == dict and log.get("meta_json") is not None:
                            if (
                                type(log["meta_json"]) == dict
                                and log["meta_json"].get("homepage") is not None
                                and cls._is_valid_url(log["meta_json"]["homepage"])
                            ):
                                if log["meta_json"]["homepage"] in homepages:
                                    if (
                                        pool.get("pool_id_bech32") is not None
                                        and pool["pool_id_bech32"] not in homepages[log["meta_json"]["homepage"]]
                                    ):
                                        homepages[log["meta_json"]["homepage"]].append(pool["pool_id_bech32"])
                                else:
                                    homepages[log["meta_json"]["homepage"]] = [pool["pool_id_bech32"]]
        # Filter the dictionary to include only the homepages present in multiple pools
        shared = {value: value_pools for value, value_pools in homepages.items() if len(value_pools) > 1}
        return shared

    def set_registered_sharing_meta_json_homepage(self, register=None):
        if register is None:
            register = self._register
        self.registered_sharing_meta_json_homepage = self.find_registered_sharing_meta_json_homepage(register)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[{current_time}] Found {len(self._registered_sharing_meta_json_homepage)} entries for registered_sharing_meta_json_homepage."
        )

    @classmethod
    def find_registered_sharing_meta_url(cls, register=[]):
        # init result dict
        urls = {}
        if type(register) == list:
            # iterate the registered pools to create a dict with values and a list with the ids containing them
            registered_pools = [
                pool for pool in register if type(pool) == dict and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if type(pool) == dict and pool.get("meta_url_log") is not None and type(pool["meta_url_log"]) == list:
                    for log in pool["meta_url_log"]:
                        if type(log) == dict and log.get("meta_url") is not None and cls._is_valid_url(log["meta_url"]):
                            if log["meta_url"] in urls:
                                if (
                                    pool.get("pool_id_bech32") is not None
                                    and pool["pool_id_bech32"] not in urls[log["meta_url"]]
                                ):
                                    urls[log["meta_url"]].append(pool["pool_id_bech32"])
                            else:
                                urls[log["meta_url"]] = [pool["pool_id_bech32"]]
        # Filter the dictionary to include only the urls present in multiple pools
        shared = {value: value_pools for value, value_pools in urls.items() if len(value_pools) > 1}
        return shared

    def set_registered_sharing_meta_url(self, register=None):
        if register is None:
            register = self._register
        self.registered_sharing_meta_url = self.find_registered_sharing_meta_url(register)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[{current_time}] Found {len(self._registered_sharing_meta_url)} entries for registered_sharing_meta_url."
        )

    @staticmethod
    def find_registered_sharing_owners(register=[]):
        # init result dict
        owners = {}
        if type(register) == list:
            # iterate the registered pools to create a dict with values and a list with the ids containing them
            registered_pools = [
                pool for pool in register if type(pool) == dict and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if type(pool) == dict and pool.get("owners_log") is not None and type(pool["owners_log"]) == list:
                    for log in pool["owners_log"]:
                        if type(log) == dict and log.get("owners") is not None and type(log["owners"]) == list:
                            for owner in log["owners"]:
                                if owner is not None:
                                    if owner in owners:
                                        if (
                                            pool.get("pool_id_bech32") is not None
                                            and pool["pool_id_bech32"] not in owners[owner]
                                        ):
                                            owners[owner].append(pool["pool_id_bech32"])
                                    else:
                                        owners[owner] = [pool["pool_id_bech32"]]
        # Filter the dictionary to include only the owners present in multiple pools
        shared = {value: value_pools for value, value_pools in owners.items() if len(value_pools) > 1}
        return shared

    def set_registered_sharing_owners(self, register=None):
        if register is None:
            register = self._register
        self.registered_sharing_owners = self.find_registered_sharing_owners(register)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Found {len(self._registered_sharing_owners)} entries for registered_sharing_owners.")

    @staticmethod
    def find_registered_sharing_reward_addr(register=[]):
        # init result dict
        addresses = {}
        if type(register) == list:
            # iterate the registered pools to create a dict with values and a list with the ids containing them
            registered_pools = [
                pool for pool in register if type(pool) == dict and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if (
                    type(pool) == dict
                    and pool.get("reward_addr_log") is not None
                    and type(pool["reward_addr_log"]) == list
                ):
                    for log in pool["reward_addr_log"]:
                        if type(log) == dict and log.get("reward_addr") is not None:
                            if log["reward_addr"] in addresses:
                                if (
                                    pool.get("pool_id_bech32") is not None
                                    and pool["pool_id_bech32"] not in addresses[log["reward_addr"]]
                                ):
                                    addresses[log["reward_addr"]].append(pool["pool_id_bech32"])
                            else:
                                addresses[log["reward_addr"]] = [pool["pool_id_bech32"]]
        # Filter the dictionary to include only the addresses present in multiple pools
        shared = {value: value_pools for value, value_pools in addresses.items() if len(value_pools) > 1}
        return shared

    def set_registered_sharing_reward_addr(self, register=None):
        if register is None:
            register = self._register
        self.registered_sharing_reward_addr = self.find_registered_sharing_reward_addr(register)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[{current_time}] Found {len(self._registered_sharing_reward_addr)} entries for registered_sharing_reward_addr."
        )


def main():
    my_checker = CardanoPoolChecker()
    my_checker.update()


if __name__ == "__main__":
    main()
