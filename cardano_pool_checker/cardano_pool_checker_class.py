"""Cardano Pool Checker module containing its class definition."""
import ipaddress
import json
import os
import re
import socket
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import urllib3
import validators
from urllib3.exceptions import HTTPError

import cardano_pool_checker.cardano_pool_checker_config as cpc_config

http = urllib3.PoolManager()
urllib3.disable_warnings()


class CardanoPoolChecker:
    """Cardano Pool Checker class definition.

    This class provides methods to maintain a JSON-based collection of
    historical Cardano stake pool registration data and create lists of
    multi-pool operators according to different criteria.

    Attributes:
        lala

    Example:
        my_checker = CardanoPoolChecker()
        my_checker.update()

    The code above downloads and updates the stake pool information using the
    Koios API and stores it in the "pools" directory under the project's root.
    It creates a register containing a list of stake pools and tracks relevant
    changes over time. Additionally, it translates each hostname found during
    the process into IP addresses and saves them in a translations register for
    later analysis. Finally, JSON files are created in the "pools" directory
    for each shared resources detection policy defined. These lists can be used
    later to identify multi-stake pool operators using various criteria.
    """

    def __init__(
        self,
        updates: list[dict[str, Any]] | None = None,
        register: list[Any] | None = None,
        translations: dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None = None,
    ) -> None:
        """Initialize variables when instantiating the CardanoPoolChecker  class.

        Args:
            updates (list[dict[str, Any]] | None, optional):
                List of updates to init the class with, when None, updates are
                loaded from the corresponding file in the "pools" directory.
                Defaults to None.
            register (list[Any] | None, optional):
                List containing a pool register to init the class with, when None,
                register is loaded from the corresponding file in the "pools"
                directory. Defaults to None.
            translations (dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None, optional):
                Dictionary containing pool hostnames translations to init the
                class with, when None, the Dictionary is loaded from the
                corresponding file in the "pools" directory. Defaults to None.
        """
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
    def pools(self) -> list[dict[str, str | None]]:
        """Getter decorator for _pools attribute.

        Returns:
            list[dict[str, str | None]]: Return _pools value.
        """
        return self._pools

    @pools.setter
    def pools(self, value: list[dict[str, str | None]]) -> None:
        self._pools = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json(self.CPC_POOLS_LIST_FILENAME, value)

    @property
    def updates(self) -> list[dict[str, Any]]:
        """Getter decorator for _updates attribute.

        Returns:
            list[dict[str, Any]]: Return _updates value.
        """
        return self._updates

    @updates.setter
    def updates(self, value: list[dict[str, Any]]) -> None:
        if self._check_updates(value):
            self._updates = value
        else:
            msg = "Wrong updates data format."
            raise ValueError(msg)
        if self.CPC_SAVE_TO_DISK:
            self._save_json(self.CPC_POOLS_UPDATES_FILENAME, value)

    @property
    def register(self) -> list[Any]:
        """Getter decorator for _register attribute.

        Returns:
            list[Any]: Return _register value.
        """
        return self._register

    @register.setter
    def register(self, value: list[Any]) -> None:
        self._register = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json(self.CPC_POOLS_REGISTER_FILENAME, value)

    @property
    def translations(self) -> dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]]:
        """Getter decorator for _translations attribute.

        Returns:
            dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]]: Return _translations value.
        """
        return self._translations

    @translations.setter
    def translations(self, value: dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]]) -> None:
        self._translations = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json(self.CPC_POOLS_DNS_TRANSLATIONS_FILENAME, value)

    @property
    def last_block_time(self) -> int:
        """Getter decorator for the block time of the last update in updates.

        Returns:
            int: Return a timestamp with the block time of the last update in updates.
        """
        last_block_time = 0
        if isinstance(self._updates, list):
            last_update = self._updates[-1] if self._updates else None
            if isinstance(last_update, dict) and last_update.get("block_time") is not None:
                last_block_time = last_update["block_time"]
        return int(last_block_time)

    @property
    def registered_currently_sharing_relay_hostname(self) -> dict[str, list[str]]:
        """Getter decorator for _registered_currently_sharing_relay_hostname attribute.

        Returns:
            dict[str, list[str]]: returns a dictionary with registered stake pools that
                are currently sharing a relay hostname.
        """
        return self._registered_currently_sharing_relay_hostname

    @registered_currently_sharing_relay_hostname.setter
    def registered_currently_sharing_relay_hostname(self, value: dict[str, list[str]]) -> None:
        self._registered_currently_sharing_relay_hostname = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_currently_sharing_relay_hostname.json", value)

    @property
    def registered_currently_sharing_relay_ipv4(self) -> dict[str, list[str]]:
        """Getter decorator for _registered_currently_sharing_relay_ipv4 attribute.

        Returns:
            dict[str, list[str]]: returns a dictionary with registered stake pools that
                are currently sharing a relay ipv4 value.
        """
        return self._registered_currently_sharing_relay_ipv4

    @registered_currently_sharing_relay_ipv4.setter
    def registered_currently_sharing_relay_ipv4(self, value: dict[str, list[str]]) -> None:
        self._registered_currently_sharing_relay_ipv4 = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_currently_sharing_relay_ipv4.json", value)

    @property
    def registered_currently_sharing_relay_ipv6(self) -> dict[str, list[str]]:
        """Getter decorator for _registered_currently_sharing_relay_ipv6 attribute.

        Returns:
            dict[str, list[str]]: returns a dictionary with registered stake pools that
                are currently sharing a relay ipv6 value.
        """
        return self._registered_currently_sharing_relay_ipv6

    @registered_currently_sharing_relay_ipv6.setter
    def registered_currently_sharing_relay_ipv6(self, value: dict[str, list[str]]) -> None:
        self._registered_currently_sharing_relay_ipv6 = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_currently_sharing_relay_ipv6.json", value)

    @property
    def registered_currently_sharing_meta_json_homepage(self) -> dict[str, list[str]]:
        """Getter decorator for _registered_currently_sharing_meta_json_homepage attribute.

        Returns:
            dict[str, list[str]]: returns a dictionary with registered stake pools that
                are currently sharing the homepage value.
        """
        return self._registered_currently_sharing_meta_json_homepage

    @registered_currently_sharing_meta_json_homepage.setter
    def registered_currently_sharing_meta_json_homepage(self, value: dict[str, list[str]]) -> None:
        self._registered_currently_sharing_meta_json_homepage = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_currently_sharing_meta_json_homepage.json", value)

    @property
    def registered_currently_sharing_meta_url(self) -> dict[str, list[str]]:
        """Getter decorator for _registered_currently_sharing_meta_url attribute.

        Returns:
            dict[str, list[str]]: returns a dictionary with registered stake pools that
                are currently sharing the metadata url value.
        """
        return self._registered_currently_sharing_meta_url

    @registered_currently_sharing_meta_url.setter
    def registered_currently_sharing_meta_url(self, value: dict[str, list[str]]) -> None:
        self._registered_currently_sharing_meta_url = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_currently_sharing_meta_url.json", value)

    @property
    def registered_currently_sharing_owners(self) -> dict[str, list[str]]:
        """Getter decorator for _registered_currently_sharing_owners attribute.

        Returns:
            dict[str, list[str]]: returns a dictionary with registered stake pools that
                are currently sharing an owner address.
        """
        return self._registered_currently_sharing_owners

    @registered_currently_sharing_owners.setter
    def registered_currently_sharing_owners(self, value: dict[str, list[str]]) -> None:
        self._registered_currently_sharing_owners = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_currently_sharing_owners.json", value)

    @property
    def registered_currently_sharing_reward_addr(self) -> dict[str, list[str]]:
        """Getter decorator for _registered_currently_sharing_reward_addr attribute.

        Returns:
            dict[str, list[str]]: returns a dictionary with registered stake pools that
                are currently sharing a reward address value.
        """
        return self._registered_currently_sharing_reward_addr

    @registered_currently_sharing_reward_addr.setter
    def registered_currently_sharing_reward_addr(self, value: dict[str, list[str]]) -> None:
        self._registered_currently_sharing_reward_addr = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_currently_sharing_reward_addr.json", value)

    @property
    def registered_sharing_relay_hostname(self) -> dict[str, list[str]]:
        """Getter decorator for _registered_sharing_relay_hostname attribute.

        Returns:
            dict[str, list[str]]: returns a dictionary with registered stake pools that
                shared at any time a relay hostname.
        """
        return self._registered_sharing_relay_hostname

    @registered_sharing_relay_hostname.setter
    def registered_sharing_relay_hostname(self, value: dict[str, list[str]]) -> None:
        self._registered_sharing_relay_hostname = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_sharing_relay_hostname.json", value)

    @property
    def registered_sharing_relay_ipv4(self) -> dict[str, list[str]]:
        """Getter decorator for _registered_sharing_relay_ipv4 attribute.

        Returns:
            dict[str, list[str]]: returns a dictionary with registered stake pools that
                shared at any time a relay ipv4 value.
        """
        return self._registered_sharing_relay_ipv4

    @registered_sharing_relay_ipv4.setter
    def registered_sharing_relay_ipv4(self, value: dict[str, list[str]]) -> None:
        self._registered_sharing_relay_ipv4 = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_sharing_relay_ipv4.json", value)

    @property
    def registered_sharing_relay_ipv6(self) -> dict[str, list[str]]:
        """Getter decorator for _registered_sharing_relay_ipv6 attribute.

        Returns:
            dict[str, list[str]]: returns a dictionary with registered stake pools that
                shared at any time a relay ipv6 value.
        """
        return self._registered_sharing_relay_ipv6

    @registered_sharing_relay_ipv6.setter
    def registered_sharing_relay_ipv6(self, value: dict[str, list[str]]) -> None:
        self._registered_sharing_relay_ipv6 = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_sharing_relay_ipv6.json", value)

    @property
    def registered_sharing_meta_json_homepage(self) -> dict[str, list[str]]:
        """Getter decorator for _registered_sharing_meta_json_homepage attribute.

        Returns:
            dict[str, list[str]]: returns a dictionary with registered stake pools that
                shared at any time the homepage value.
        """
        return self._registered_sharing_meta_json_homepage

    @registered_sharing_meta_json_homepage.setter
    def registered_sharing_meta_json_homepage(self, value: dict[str, list[str]]) -> None:
        self._registered_sharing_meta_json_homepage = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_sharing_meta_json_homepage.json", value)

    @property
    def registered_sharing_meta_url(self) -> dict[str, list[str]]:
        """Getter decorator for _registered_sharing_meta_url attribute.

        Returns:
            dict[str, list[str]]: returns a dictionary with registered stake pools that
                shared at any time the metadata url value.
        """
        return self._registered_sharing_meta_url

    @registered_sharing_meta_url.setter
    def registered_sharing_meta_url(self, value: dict[str, list[str]]) -> None:
        self._registered_sharing_meta_url = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_sharing_meta_url.json", value)

    @property
    def registered_sharing_owners(self) -> dict[str, list[str]]:
        """Getter decorator for _registered_sharing_owners attribute.

        Returns:
            dict[str, list[str]]: returns a dictionary with registered stake pools that
                shared at any time an owner address.
        """
        return self._registered_sharing_owners

    @registered_sharing_owners.setter
    def registered_sharing_owners(self, value: dict[str, list[str]]) -> None:
        self._registered_sharing_owners = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_sharing_owners.json", value)

    @property
    def registered_sharing_reward_addr(self) -> dict[str, list[str]]:
        """Getter decorator for _registered_sharing_reward_addr attribute.

        Returns:
            dict[str, list[str]]: returns a dictionary with registered stake pools that
                shared a any time a reward address value.
        """
        return self._registered_sharing_reward_addr

    @registered_sharing_reward_addr.setter
    def registered_sharing_reward_addr(self, value: dict[str, list[str]]) -> None:
        self._registered_sharing_reward_addr = value
        if self.CPC_SAVE_TO_DISK:
            self._save_json("registered_sharing_reward_addr.json", value)

    @property
    def classified_pools(self) -> dict[str, list[dict[str, str | list[str]]]]:
        """Getter decorator for _classified_pools attribute.

        Returns:
            list[dict[str, str | list[str]]]: Return classified pools.
        """
        return self._classified_pools

    @classified_pools.setter
    def classified_pools(self, value: dict[str, list[dict[str, str | list[str]]]]) -> None:
        self._classified_pools = value
        if self.CPC_SAVE_TO_DISK:
            for rule in value:
                self._save_json(str(rule), value[rule])

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        return bool(validators.url(url))

    @staticmethod
    def _is_reachable_url(url: str) -> bool:
        http = urllib3.PoolManager()
        success: int = 200
        try:
            response = http.request("GET", url)
        except HTTPError:
            return False
        else:
            return int(response.status) == success

    @staticmethod
    def _unshorten_ipv6(address: str) -> str:
        try:
            ipv6 = ipaddress.IPv6Address(address)
        except ipaddress.AddressValueError:
            return "Invalid_IPv6"
        else:
            return str(ipv6.exploded)

    @staticmethod
    def _resolve_a_records(hostname: str) -> list[str | Any]:
        try:
            ip_addresses = set()
            for result in socket.getaddrinfo(hostname, None):
                ip_addresses.add(result[4][0])
            return list(ip_addresses)
        except socket.gaierror:
            return []

    def _load_settings(self) -> None:  # noqa: PLR0912
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
        try:
            self.CPC_POOLS_URL = cpc_config.CPC_POOLS_URL
        except (NameError, AttributeError):
            self.CPC_POOLS_URL = (
                "https://raw.githubusercontent.com/blockopszone/cardano-pool-checker/main/cardano_pool_checker/pools/"
            )
        try:
            self.CPC_MSPO_RULES = cpc_config.CPC_MSPO_RULES
        except (NameError, AttributeError):
            self.CPC_MSPO_RULES = []
        try:
            self.CPC_MSPO_RULES_ALLOWED_KEYWORDS = cpc_config.CPC_MSPO_RULES_ALLOWED_KEYWORDS
        except (NameError, AttributeError):
            self.CPC_MSPO_RULES_ALLOWED_KEYWORDS = [
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

    def _load_updates(self) -> None:
        try:
            with open(
                os.path.join(os.path.dirname(__file__), self.CPC_DATA_DIR, self.CPC_POOLS_UPDATES_FILENAME)
            ) as file:
                updates = json.load(file)
                if self._check_updates(updates):
                    self._updates = updates
                else:
                    msg = "Wrong updates data format."
                    raise ValueError(msg)
        except FileNotFoundError:
            print("Updates File not found, creating a new one.")  # noqa: T201
            self.updates = []
        except OSError as exc:
            msg = "Error reading the updates file."
            raise OSError(msg) from exc

    def _load_register(self) -> None:
        try:
            with open(
                os.path.join(os.path.dirname(__file__), self.CPC_DATA_DIR, self.CPC_POOLS_REGISTER_FILENAME)
            ) as file:
                self._register = json.load(file)
        except FileNotFoundError:
            print("Register File not found, creating a new one.")  # noqa: T201
            self.register = []
        except OSError as exc:
            msg = "Error reading the register file."
            raise OSError(msg) from exc

    def _load_translations(self) -> None:
        try:
            with open(
                os.path.join(os.path.dirname(__file__), self.CPC_DATA_DIR, self.CPC_POOLS_DNS_TRANSLATIONS_FILENAME),
            ) as file:
                self._translations = json.load(file)
        except FileNotFoundError:
            print("Translations File not found, creating a new one.")  # noqa: T201
            self.translations = {}
        except OSError as exc:
            msg = "Error reading the translations file."
            raise OSError(msg) from exc

    @staticmethod
    def _download_json(url: str) -> Any:
        resp = http.request("GET", url)
        if str(resp.status) == "200":
            return json.loads(resp.data)
        print("An error occurred while downloading data")  # noqa: T201
        sys.exit(1)

    def _save_json(self, filename: str, data: Any) -> None:
        directory = os.path.join(os.path.dirname(__file__), self.CPC_DATA_DIR)
        os.makedirs(directory, exist_ok=True)  # Create the directory if it doesn't exist
        file_path = os.path.join(directory, filename)
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

    def info(self) -> None:
        """Print program information."""
        print("\nCardano Pool Checker v.0.5.0\n")  # noqa: T201

    def update(self) -> None:
        """Update all the stake pools information in the "pools" directory.

        Update all the stake pools information, including the list of pools,
        the pool updates register, the hostnames translations, and the shared
        resources lists used for multi pool operators detection. The data is
        then saved in the "pools" directory under the project's root.
        """
        self.info()
        # Download a simple list of pools
        self.set_pools()
        # Update the updates incrementally.
        since = self.last_block_time
        new_updates = self.build_updates(since)
        if new_updates:
            if self._updates:
                # setter decorator is not triggered by .extend
                self.updates = self.updates + new_updates
            else:
                self.updates = new_updates
        current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Pools updates: {len(new_updates)} new downloaded.")  # noqa: T201
        # Icremental registry updates needs more testing, just passing
        # the current register and the new updates depends on the good
        # state of the register file. It may be required to look in the
        # register for the last block_time to be able to enforce a correct
        # sync, and this, among others, reduces the cost benefits of
        # incremental mode. Some benchmarking is needed.
        # For now, rebuild the register entirely with each update.
        self.set_register()
        self.set_translations()
        self.set_all_sharing()
        self.set_classified_pools()

    @classmethod
    def build_pools(cls) -> list[dict[str, str | None]]:
        """Build a complete list of stake pools using Koios API.

        Returns:
            list[dict[str, str | None]]: Returns a list of stake pools
                containing the pool_id_bech32 and ticker.
        """
        pagesize = 1000
        # get pool list
        koios_pool_list = []
        pool_range = range(0, 100000, pagesize)
        for offset in pool_range:
            url = "https://api.koios.rest/api/v0/pool_list?offset=" + str(offset) + "&limit=" + str(pagesize)
            fetched = cls._download_json(url)
            koios_pool_list.extend(fetched)
            if len(fetched) < pagesize:
                break
        return koios_pool_list

    def set_pools(self) -> None:
        """Update the pools attribute with new data coming from build_pools call."""
        self.pools = self.build_pools()
        current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Simple list with {len(self._pools)} pools downloaded.")  # noqa: T201

    @staticmethod
    def _check_updates(updates: list[dict[str, Any]] | None = None) -> bool:
        if updates is None:
            updates = []
        old_time = 0
        result = True
        if isinstance(updates, list):
            for update in updates:
                if isinstance(update, dict) and update.get("block_time") is not None:
                    if update["block_time"] >= old_time:
                        old_time = update["block_time"]
                    else:
                        result = False
                        break
        else:
            result = False
        return result

    @classmethod
    def build_updates(cls, since: int = 0) -> list[Any]:
        """Download the pool updates from Koios API.

        Args:
            since (int | None, optional): Timestamp indicating the starting point for
                obtaining register updates. If None, the current updates attribute
                is used to get the last entry block time to start from there.
                Defaults to None.

        Returns:
            list[Any]: Rerun a list with the updates.
        """
        # Get pool updates data using koios
        # curl -s "https://api.koios.rest/api/v0/pool_updates?block_time=gt.1&order=block_time.asc&limit=500"
        # -H "Range: 0-499"
        updates_list = []
        if isinstance(since, int):
            batchsize = 1000
            iteration = 0
            while True:
                fetched = cls._download_json(
                    "https://api.koios.rest/api/v0/pool_updates?block_time=gt."
                    + str(since)
                    + "&order=block_time.asc&offset="
                    + str(batchsize * iteration)
                    + "&limit="
                    + str(batchsize)
                )
                updates_list.extend(fetched)
                iteration += 1
                if len(fetched) < batchsize:
                    break
        return list(updates_list)

    def set_updates(self, since: int | None = None) -> None:
        """Update the updates attribute with new data coming from build_updates call.

        Args:
            since (int | None, optional): Timestamp indicating the starting point for
                obtaining register updates. If None, the current updates attribute
                is used to get the last entry block time to start from there.
                Defaults to None.
        """
        if since is None:
            since = self.last_block_time
        new_updates = self.build_updates(since)
        self.updates.extend(new_updates)
        current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Pools updates: {len(new_updates)} new downloaded.")  # noqa: T201

    @staticmethod
    def build_register(  # noqa: C901, PLR0912
        updates: list[dict[str, Any]] | None = None, register: list[Any] | None = None
    ) -> list[dict[str, Any]]:
        """Build a register with stake pools registratiosn and updates over time.

        Args:
            updates (list[dict[str, Any]] | None, optional): List of cronological
                pool updates used to create the register, when None the list is
                empty. Defaults to None.
            register (list[Any] | None, optional): List with an existing register
                that can be passed as a parameter to load alreasy existent values,
                so if incremental updates are also passed instead of the entire list,
                the register file can be extended, so built incrementally.
                This option is experimental, it requires better input param checks,
                and some benchmarking tests because possibly it's not worth to use,
                because with the actual code the current register needs to be fully
                processed anyway to match the expected dict format.
                Defaults to None.

        Returns:
            list[dict[str, Any]]: Return the built register.
        """
        # Start processing the register parameter
        if register is None:
            register = []
        if updates is None:
            updates = []
        register_dict = {}
        if register is not None and isinstance(register, list):
            for register_pool in register:
                if isinstance(register_pool, dict) and register_pool.get("pool_id_bech32") is not None:
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

    def set_register(self, updates: list[dict[str, Any]] | None = None) -> None:
        """Update the register attribute with new data coming from build_register call.

        Args:
            updates (list[dict[str, Any]] | None = None, optional): List of updates
                to use for building the register. When None, the update attribute
                is used. Defaults to None.
        """
        if updates is None:
            updates = self._updates
        self.register = self.build_register(updates)
        current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Pools register: rebuilt for {len(self._register)} stake pools.")  # noqa: T201

    @classmethod
    def build_translations(  # noqa: PLR0912, C901
        cls,
        register: list[dict[str, Any]] | None = None,
        translations: dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None = None,
    ) -> dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]]:
        """Build a hostname translations dictionary from the hosts in a pools registry.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools to analyse.
                Defaults to None.
            translations (dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None, optional):
                Dictionary with existent translations to extend with new ones. Defaults to None.

        Returns:
            dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]]:
                Dictionary with the updated translations.
        """
        # Iterate the registered pools to create a list of IPs from hostnames
        if translations is None:
            translations = {}
        if register is None:
            register = []
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
                        if resolved_ip_obj.version == 4:  # noqa: PLR2004
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
                        elif resolved_ip_obj.version == 6:  # noqa: PLR2004
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

    def set_translations(
        self,
        register: list[dict[str, Any]] | None = None,
        translations: dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None = None,
    ) -> None:
        """Update the translations attribute with the new data coming from a build_translations call.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools. Defaults to None.
            translations (dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None, optional):
                Existing translations dictionary to extend if passed as parameter.
                Defaults to None.
        """
        if register is None:
            register = self._register
        if translations is None:
            translations = self._translations
        self.translations = self.build_translations(register, translations)
        current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(  # noqa: T201
            f"[{current_time}] Pools DNS translations: updated for {len(self._translations)} currently tracked hostnames."
        )

    def set_all_sharing(
        self,
        register: list[dict[str, Any]] | None = None,
        translations: dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None = None,
    ) -> None:
        """Update attributes for all the available lists of shared resources between pools.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools. Defaults to None.
            translations (dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None, optional):
                Existing hostname translations dictionary to check for shared IP addresses
                also between the resolved ones. Defaults to None.
        """
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

    def set_registered_currently_sharing(
        self,
        register: list[dict[str, Any]] | None = None,
        translations: dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None = None,
    ) -> None:
        """Update attributes for all the available lists of currently shared resources between pools.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools. Defaults to None.
            translations (dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None, optional):
                Existing hostname translations dictionary to check for shared IP addresses
                also between the resolved ones. Defaults to None.
        """
        self.set_registered_currently_sharing_relay_hostname(register)
        self.set_registered_currently_sharing_relay_ipv4(register, translations)
        self.set_registered_currently_sharing_relay_ipv6(register, translations)
        self.set_registered_currently_sharing_meta_json_homepage(register)
        self.set_registered_currently_sharing_meta_url(register)
        self.set_registered_currently_sharing_owners(register)
        self.set_registered_currently_sharing_reward_addr(register)

    def set_registered_sharing(
        self,
        register: list[dict[str, Any]] | None = None,
        translations: dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None = None,
    ) -> None:
        """Update attributes for all the available lists of ever shared resources between pools.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools. Defaults to None.
            translations (dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None, optional):
                Existing hostname translations dictionary to check for shared IP addresses
                also between the resolved ones. Defaults to None.
        """
        self.set_registered_sharing_relay_hostname(register)
        self.set_registered_sharing_relay_ipv4(register, translations)
        self.set_registered_sharing_relay_ipv6(register, translations)
        self.set_registered_sharing_meta_json_homepage(register)
        self.set_registered_sharing_meta_url(register)
        self.set_registered_sharing_owners(register)
        self.set_registered_sharing_reward_addr(register)

    @staticmethod
    def find_registered_currently_sharing_relay_hostname(
        register: list[dict[str, Any]] | None = None
    ) -> dict[str, list[str]]:
        """Find registered stake pools that are currently sharing a relay hostname.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools.
                Defaults to None.

        Returns:
            dict[str, list[str]]: Dictionary containing the shared resources between pools.
        """
        # init result dict
        if register is None:
            register = []
        hostnames: dict[str, list[str]] = {}
        if isinstance(register, list):
            # iterate the registered pools to create a dict with values and a list with the ids containing them
            registered_pools = [
                pool for pool in register if isinstance(pool, dict) and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if isinstance(pool, dict) and pool.get("relays") is not None and isinstance(pool["relays"], list):
                    for relay in pool["relays"]:
                        if isinstance(relay, dict) and relay.get("dns") is not None:
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
        return {value: value_pools for value, value_pools in hostnames.items() if len(value_pools) > 1}

    def set_registered_currently_sharing_relay_hostname(self, register: list[dict[str, Any]] | None = None) -> None:
        """Update the registered_currently_sharing_relay_hostname attribute.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools,
                when None it is loaded from the attribute. Defaults to None.
        """
        if register is None:
            register = self._register
        self.registered_currently_sharing_relay_hostname = self.find_registered_currently_sharing_relay_hostname(
            register
        )
        current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(  # noqa: T201
            f"[{current_time}] Found {len(self._registered_currently_sharing_relay_hostname)} entries for registered_currently_sharing_relay_hostname."
        )

    @staticmethod
    def find_registered_currently_sharing_relay_ipv4(  # noqa: PLR0912, C901
        register: list[dict[str, Any]] | None = None,
        translations: dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None = None,
    ) -> dict[str, list[str]]:
        """Find registered stake pools that are currently sharing a relay IPv4 address.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools. Defaults to None.
            translations (dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None, optional):
                Existing hostname translations dictionary to check for shared IP addresses
                also between the resolved ones. Defaults to None.

        Returns:
            dict[str, list[str]]: Dictionary containing the shared resources between pools.
        """
        # init result dict
        if translations is None:
            translations = {}
        if register is None:
            register = []
        ipv4_addresses: dict[str, list[str]] = {}
        # iterate the registered pools to create a list of values and the ids containing them
        if isinstance(register, list):
            registered_pools = [
                pool for pool in register if isinstance(pool, dict) and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if isinstance(pool, dict) and pool.get("relays") is not None and isinstance(pool["relays"], list):
                    for relay in pool["relays"]:
                        if isinstance(relay, dict) and relay.get("ipv4") is not None:
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
        if isinstance(translations, dict) and translations.get("4") is not None:
            for hostname_data in translations.values():
                if isinstance(hostname_data, dict) and hostname_data.get("4") is not None:
                    for resolved_ip, resolved_ip_data in hostname_data["4"].items():
                        if isinstance(resolved_ip_data, dict):
                            for mypool, pool_data in resolved_ip_data.items():
                                if isinstance(pool_data, dict) and pool_data.get("last") is not None:
                                    last_datetime = datetime.fromtimestamp(pool_data["last"], tz=timezone.utc)
                                    if last_datetime > datetime.now(tz=timezone.utc) - timedelta(hours=4):
                                        if resolved_ip in ipv4_addresses:
                                            if mypool is not None and mypool not in ipv4_addresses[resolved_ip]:
                                                ipv4_addresses[resolved_ip].append(mypool)
                                        else:
                                            ipv4_addresses[resolved_ip] = [mypool]
        # Filter the dictionary to include only the IPv4 addresses present in multiple pools
        return {value: value_pools for value, value_pools in ipv4_addresses.items() if len(value_pools) > 1}

    def set_registered_currently_sharing_relay_ipv4(
        self,
        register: list[dict[str, Any]] | None = None,
        translations: dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None = None,
    ) -> None:
        """Update the registered_currently_sharing_relay_ipv4 attribute.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools,
                when None it is loaded from the attribute. Defaults to None.
            translations (dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None, optional):
                Existing hostname translations dictionary to check for shared IP addresses
                also between the resolved ones. Defaults to None.
        """
        if register is None:
            register = self._register
        if translations is None:
            translations = self._translations
        self.registered_currently_sharing_relay_ipv4 = self.find_registered_currently_sharing_relay_ipv4(
            register, translations
        )
        current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(  # noqa: T201
            f"[{current_time}] Found {len(self._registered_currently_sharing_relay_ipv4)} entries for registered_currently_sharing_relay_ipv4."
        )

    @classmethod
    def find_registered_currently_sharing_relay_ipv6(  # noqa: PLR0912, C901
        cls,
        register: list[dict[str, Any]] | None = None,
        translations: dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None = None,
    ) -> dict[Any, Any]:
        """Find registered stake pools that are currently sharing a relay IPv6 address.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools. Defaults to None.
            translations (dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None, optional):
                Existing hostname translations dictionary to check for shared IP addresses
                also between the resolved ones. Defaults to None.

        Returns:
            dict[Any, Any]: Dictionary containing the shared resources between pools.
        """
        # init result dict
        if translations is None:
            translations = {}
        if register is None:
            register = []
        ipv6_addresses: dict[str, list[str]] = {}
        if isinstance(register, list):
            # iterate the registered pools to create a list of values and the ids containing them
            registered_pools = [
                pool for pool in register if isinstance(pool, dict) and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if isinstance(pool, dict) and pool.get("relays") is not None and isinstance(pool["relays"], list):
                    for relay in pool["relays"]:
                        if isinstance(relay, dict) and relay.get("ipv6") is not None:
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
        if isinstance(translations, dict) and translations.get("6") is not None:
            for hostname_data in translations.values():
                if isinstance(hostname_data, dict) and hostname_data.get("6") is not None:
                    for resolved_ip, resolved_ip_data in hostname_data["6"].items():
                        full_ipv6 = cls._unshorten_ipv6(resolved_ip)
                        if isinstance(resolved_ip_data, dict):
                            for mypool, pool_data in resolved_ip_data.items():
                                if isinstance(pool_data, dict) and pool_data.get("last") is not None:
                                    last_datetime = datetime.fromtimestamp(pool_data["last"], tz=timezone.utc)
                                    if last_datetime > datetime.now(tz=timezone.utc) - timedelta(hours=4):
                                        if full_ipv6 in ipv6_addresses:
                                            if mypool is not None and mypool not in ipv6_addresses[full_ipv6]:
                                                ipv6_addresses[full_ipv6].append(mypool)
                                        else:
                                            ipv6_addresses[full_ipv6] = [mypool]
        # Filter the dictionary to include only the IPv6 addresses present in multiple pools
        return {value: value_pools for value, value_pools in ipv6_addresses.items() if len(value_pools) > 1}

    def set_registered_currently_sharing_relay_ipv6(
        self,
        register: list[dict[str, Any]] | None = None,
        translations: dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None = None,
    ) -> None:
        """Update the registered_currently_sharing_relay_ipv6 attribute.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools,
                when None it is loaded from the attribute. Defaults to None.
            translations (dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None, optional):
                Existing hostname translations dictionary to check for shared IP addresses
                also between the resolved ones. Defaults to None.
        """
        if register is None:
            register = self._register
        if translations is None:
            translations = self._translations
        self.registered_currently_sharing_relay_ipv6 = self.find_registered_currently_sharing_relay_ipv6(
            register, translations
        )
        current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(  # noqa: T201
            f"[{current_time}] Found {len(self._registered_currently_sharing_relay_ipv6)} entries for registered_currently_sharing_relay_ipv6."
        )

    @classmethod
    def find_registered_currently_sharing_meta_json_homepage(
        cls, register: list[dict[str, Any]] | None = None
    ) -> dict[str, list[str]]:
        """Find registered stake pools that are currently sharing the homepage.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools. Defaults to None.

        Returns:
            dict[str, list[str]]: Dictionary containing the shared resources between pools.
        """
        # init result dict
        if register is None:
            register = []
        homepages: dict[str, list[str]] = {}
        if isinstance(register, list):
            # iterate the registered pools to create a list of values and the ids containing them
            registered_pools = [
                pool for pool in register if isinstance(pool, dict) and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if (
                    isinstance(pool, dict)
                    and pool.get("meta_json") is not None
                    and (
                        isinstance(pool["meta_json"], dict)
                        and pool["meta_json"].get("homepage") is not None
                        and cls._is_valid_url(pool["meta_json"]["homepage"])
                    )
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
        return {value: value_pools for value, value_pools in homepages.items() if len(value_pools) > 1}

    def set_registered_currently_sharing_meta_json_homepage(self, register: list[dict[str, Any]] | None = None) -> None:
        """Update the registered_currently_sharing_meta_json_homepage attribute.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools,
                when None it is loaded from the attribute. Defaults to None.
        """
        if register is None:
            register = self._register
        self.registered_currently_sharing_meta_json_homepage = (
            self.find_registered_currently_sharing_meta_json_homepage(register)
        )
        current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(  # noqa: T201
            f"[{current_time}] Found {len(self._registered_currently_sharing_meta_json_homepage)} entries for registered_currently_sharing_meta_json_homepage."
        )

    @classmethod
    def find_registered_currently_sharing_meta_url(cls, register: list[dict[str, Any]] | None = None) -> dict[Any, Any]:
        """Find registered stake pools that are currently sharing the metadata url.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools. Defaults to None.

        Returns:
            dict[Any, Any]: Dictionary containing the shared resources between pools.
        """
        # init result dict
        if register is None:
            register = []
        meta_urls: dict[str, list[str]] = {}
        if isinstance(register, list):
            # iterate the registered pools to create a list of values and the ids containing them
            registered_pools = [
                pool for pool in register if isinstance(pool, dict) and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if isinstance(pool, dict) and pool.get("meta_url") is not None and cls._is_valid_url(pool["meta_url"]):
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
        return {value: value_pools for value, value_pools in meta_urls.items() if len(value_pools) > 1}

    def set_registered_currently_sharing_meta_url(self, register: list[dict[str, Any]] | None = None) -> None:
        """Update the registered_currently_sharing_meta_url attribute.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools,
                when None it is loaded from the attribute. Defaults to None.
        """
        if register is None:
            register = self._register
        self.registered_currently_sharing_meta_url = self.find_registered_currently_sharing_meta_url(register)
        current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(  # noqa: T201
            f"[{current_time}] Found {len(self._registered_currently_sharing_meta_url)} entries for registered_currently_sharing_meta_url."
        )

    @staticmethod
    def find_registered_currently_sharing_owners(register: list[dict[str, Any]] | None = None) -> dict[str, list[str]]:
        """Find registered stake pools that are currently sharing an owner address.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools. Defaults to None.

        Returns:
            dict[str, list[str]]: Dictionary containing the shared resources between pools.
        """
        # init result dict
        if register is None:
            register = []
        owners: dict[str, list[str]] = {}
        if isinstance(register, list):
            # iterate the registered pools to create a list of values and the ids containing them
            registered_pools = [
                pool for pool in register if isinstance(pool, dict) and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if isinstance(pool, dict) and pool.get("owners") is not None and isinstance(pool["owners"], list):
                    for owner in pool["owners"]:
                        if owner in owners:
                            # should be always true for currently functions but just in case...
                            if pool.get("pool_id_bech32") is not None and pool["pool_id_bech32"] not in owners[owner]:
                                owners[owner].append(pool["pool_id_bech32"])
                        else:
                            owners[owner] = [pool["pool_id_bech32"]]
        # Filter the dictionary to include only the owners present in multiple pools
        return {value: value_pools for value, value_pools in owners.items() if len(value_pools) > 1}

    def set_registered_currently_sharing_owners(self, register: list[dict[str, Any]] | None = None) -> None:
        """Update the registered_currently_sharing_owners attribute.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools,
                when None it is loaded from the attribute. Defaults to None.
        """
        if register is None:
            register = self._register
        self.registered_currently_sharing_owners = self.find_registered_currently_sharing_owners(register)
        current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(  # noqa: T201
            f"[{current_time}] Found {len(self._registered_currently_sharing_meta_url)} entries for registered_currently_sharing_meta_url."
        )

    @staticmethod
    def find_registered_currently_sharing_reward_addr(
        register: list[dict[str, Any]] | None = None
    ) -> dict[str, list[str]]:
        """Find registered stake pools that are currently sharing a reward address.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools. Defaults to None.

        Returns:
            dict[str, list[str]]: Dictionary containing the shared resources between pools.
        """
        # init result dict
        if register is None:
            register = []
        addresses: dict[str, list[str]] = {}
        if isinstance(register, list):
            # iterate the registered pools to create a list of values and the ids containing them
            registered_pools = [
                pool for pool in register if isinstance(pool, dict) and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if isinstance(pool, dict) and pool.get("reward_addr") is not None:
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
        return {value: value_pools for value, value_pools in addresses.items() if len(value_pools) > 1}

    def set_registered_currently_sharing_reward_addr(self, register: list[dict[str, Any]] | None = None) -> None:
        """Update the registered_currently_sharing_reward_addr attribute.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools,
                when None it is loaded from the attribute. Defaults to None.
        """
        if register is None:
            register = self._register
        self.registered_currently_sharing_reward_addr = self.find_registered_currently_sharing_reward_addr(register)
        current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(  # noqa: T201
            f"[{current_time}] Found {len(self._registered_currently_sharing_reward_addr)} entries for registered_currently_sharing_reward_addr."
        )

    @staticmethod
    def find_registered_sharing_relay_hostname(  # noqa: C901
        register: list[dict[str, Any]] | None = None
    ) -> dict[str, list[str]]:
        """Find registered stake pools that shared at any time a relay hostname.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools. Defaults to None.

        Returns:
            dict[str, list[str]]: Dictionary containing the shared resources between pools.
        """
        # init result dict
        if register is None:
            register = []
        hostnames: dict[str, list[str]] = {}
        if isinstance(register, list):
            # iterate the registered pools to create a dict with values and a list with the ids containing them
            registered_pools = [
                pool for pool in register if isinstance(pool, dict) and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if (
                    isinstance(pool, dict)
                    and pool.get("relays_log") is not None
                    and isinstance(pool["relays_log"], list)
                ):
                    for log in pool["relays_log"]:
                        if isinstance(log, dict) and log.get("relays") is not None and isinstance(log["relays"], list):
                            for relay in log["relays"]:
                                if isinstance(relay, dict) and relay.get("dns") is not None:
                                    if relay["dns"] in hostnames:
                                        if (
                                            pool.get("pool_id_bech32") is not None
                                            and pool["pool_id_bech32"] not in hostnames[relay["dns"]]
                                        ):
                                            hostnames[relay["dns"]].append(pool["pool_id_bech32"])
                                    else:
                                        hostnames[relay["dns"]] = [pool["pool_id_bech32"]]
        # Filter the dictionary to include only the hostnames present in multiple pools
        return {value: value_pools for value, value_pools in hostnames.items() if len(value_pools) > 1}

    def set_registered_sharing_relay_hostname(self, register: list[dict[str, Any]] | None = None) -> None:
        """Update the registered_sharing_relay_hostname attribute.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools,
                when None it is loaded from the attribute. Defaults to None.
        """
        if register is None:
            register = self._register
        self.registered_sharing_relay_hostname = self.find_registered_sharing_relay_hostname(register)
        current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(  # noqa: T201
            f"[{current_time}] Found {len(self._registered_sharing_relay_hostname)} entries for registered_sharing_relay_hostname."
        )

    @staticmethod
    def find_registered_sharing_relay_ipv4(  # noqa: C901, PLR0912
        register: list[dict[str, Any]] | None = None,
        translations: dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None = None,
    ) -> dict[str, list[str]]:
        """Find registered stake pools that shared at any time a relay IPv4.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools. Defaults to None.
            translations (dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None, optional):
                Existing hostname translations dictionary to check for shared IP addresses
                also between the resolved ones. Defaults to None.

        Returns:
            dict[str, list[str]]: Dictionary containing the shared resources between pools.
        """
        # init result dict
        if translations is None:
            translations = {}
        if register is None:
            register = []
        ipv4_addresses: dict[str, list[str]] = {}
        if isinstance(register, list):
            # iterate the registered pools to create a dict with values and a list with the ids containing them
            registered_pools = [
                pool for pool in register if isinstance(pool, dict) and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if (
                    isinstance(pool, dict)
                    and pool.get("relays_log") is not None
                    and isinstance(pool["relays_log"], list)
                ):
                    for log in pool["relays_log"]:
                        if isinstance(log, dict) and log.get("relays") is not None and isinstance(log["relays"], list):
                            for relay in log["relays"]:
                                if isinstance(relay, dict) and relay.get("ipv4") is not None:
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
        if isinstance(translations, dict) and translations.get("4") is not None:
            for hostname_data in translations.values():
                if isinstance(hostname_data, dict) and hostname_data.get("4") is not None:
                    for resolved_ip, resolved_ip_data in hostname_data["4"].items():
                        if isinstance(resolved_ip_data, dict) == dict:
                            for mypool in resolved_ip_data:
                                if resolved_ip in ipv4_addresses:
                                    if mypool is not None and mypool not in ipv4_addresses[resolved_ip]:
                                        ipv4_addresses[resolved_ip].append(mypool)
                                else:
                                    ipv4_addresses[resolved_ip] = [mypool]
        # Filter the dictionary to include only the IPv4 addresses present in multiple pools
        return {value: value_pools for value, value_pools in ipv4_addresses.items() if len(value_pools) > 1}

    def set_registered_sharing_relay_ipv4(
        self,
        register: list[dict[str, Any]] | None = None,
        translations: dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None = None,
    ) -> None:
        """Update the registered_sharing_relay_ipv4 attribute.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools,
                when None it is loaded from the attribute. Defaults to None.
            translations (dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None, optional):
                Existing hostname translations dictionary to check for shared IP addresses
                also between the resolved ones. Defaults to None.
        """
        if register is None:
            register = self._register
        if translations is None:
            translations = self._translations
        self.registered_sharing_relay_ipv4 = self.find_registered_sharing_relay_ipv4(register, translations)
        current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(  # noqa: T201
            f"[{current_time}] Found {len(self._registered_sharing_relay_ipv4)} entries for registered_sharing_relay_ipv4."
        )

    @classmethod
    def find_registered_sharing_relay_ipv6(  # noqa: C901, PLR0912
        cls,
        register: list[dict[str, Any]] | None = None,
        translations: dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None = None,
    ) -> dict[Any, Any]:
        """Find registered stake pools that shared at any time a relay IPv6.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools. Defaults to None.
            translations (dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None, optional):
                Existing hostname translations dictionary to check for shared IP addresses
                also between the resolved ones. Defaults to None.

        Returns:
            dict[Any, Any]: Dictionary containing the shared resources between pools.
        """
        # init result dict
        if translations is None:
            translations = {}
        if register is None:
            register = []
        ipv6_addresses: dict[str, list[str]] = {}
        if isinstance(register, list):
            # iterate the registered pools to create a dict with values and a list with the ids containing them
            registered_pools = [
                pool for pool in register if isinstance(pool, dict) and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if (
                    isinstance(pool, dict)
                    and pool.get("relays_log") is not None
                    and isinstance(pool["relays_log"], list)
                ):
                    for log in pool["relays_log"]:
                        if isinstance(log, dict) and log.get("relays") is not None and isinstance(log["relays"], list):
                            for relay in log["relays"]:
                                if isinstance(relay, dict) and relay.get("ipv6") is not None:
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
        if isinstance(translations, dict) and translations.get("6") is not None:
            for hostname_data in translations.values():
                if isinstance(hostname_data, dict) and hostname_data.get("6") is not None:
                    for resolved_ip, resolved_ip_data in hostname_data["6"].items():
                        full_ipv6 = cls._unshorten_ipv6(resolved_ip)
                        if isinstance(resolved_ip_data, dict):
                            for mypool in resolved_ip_data:
                                if full_ipv6 in ipv6_addresses:
                                    if mypool is not None and mypool not in ipv6_addresses[full_ipv6]:
                                        ipv6_addresses[full_ipv6].append(mypool)
                                else:
                                    ipv6_addresses[full_ipv6] = [mypool]
        # Filter the dictionary to include only the IPv6 addresses present in multiple pools
        return {value: value_pools for value, value_pools in ipv6_addresses.items() if len(value_pools) > 1}

    def set_registered_sharing_relay_ipv6(
        self,
        register: list[dict[str, Any]] | None = None,
        translations: dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None = None,
    ) -> None:
        """Update the registered_sharing_relay_ipv6 attribute.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools,
                when None it is loaded from the attribute. Defaults to None.
            translations (dict[str, dict[str, dict[str, dict[str, dict[str, float]]]]] | None, optional):
                Existing hostname translations dictionary to check for shared IP addresses
                also between the resolved ones. Defaults to None.
        """
        if register is None:
            register = self._register
        if translations is None:
            translations = self._translations
        self.registered_sharing_relay_ipv6 = self.find_registered_sharing_relay_ipv6(register, translations)
        current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(  # noqa: T201
            f"[{current_time}] Found {len(self._registered_sharing_relay_ipv6)} entries for registered_sharing_relay_ipv6."
        )

    @classmethod
    def find_registered_sharing_meta_json_homepage(
        cls, register: list[dict[str, Any]] | None = None
    ) -> dict[str, list[str]]:
        """Find registered stake pools that shared at any time the homepage.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools. Defaults to None.

        Returns:
            dict[str, list[str]]: Dictionary containing the shared resources between pools.
        """
        # init result dict
        if register is None:
            register = []
        homepages: dict[str, list[str]] = {}
        if isinstance(register, list):
            # iterate the registered pools to create a dict with values and a list with the ids containing them
            registered_pools = [
                pool for pool in register if isinstance(pool, dict) and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if (
                    isinstance(pool, dict)
                    and pool.get("meta_json_log") is not None
                    and isinstance(pool["meta_json_log"], list)
                ):
                    for log in pool["meta_json_log"]:
                        if (
                            isinstance(log, dict)
                            and log.get("meta_json") is not None
                            and (
                                isinstance(log["meta_json"], dict)
                                and log["meta_json"].get("homepage") is not None
                                and cls._is_valid_url(log["meta_json"]["homepage"])
                            )
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
        return {value: value_pools for value, value_pools in homepages.items() if len(value_pools) > 1}

    def set_registered_sharing_meta_json_homepage(self, register: list[dict[str, Any]] | None = None) -> None:
        """Update the registered_sharing_meta_json_homepage attribute.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools,
                when None it is loaded from the attribute. Defaults to None.
        """
        if register is None:
            register = self._register
        self.registered_sharing_meta_json_homepage = self.find_registered_sharing_meta_json_homepage(register)
        current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(  # noqa: T201
            f"[{current_time}] Found {len(self._registered_sharing_meta_json_homepage)} entries for registered_sharing_meta_json_homepage."
        )

    @classmethod
    def find_registered_sharing_meta_url(cls, register: list[dict[str, Any]] | None = None) -> dict[Any, Any]:
        """Find registered stake pools that shared at any time the metadata url.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools. Defaults to None.

        Returns:
            dict[Any, Any]: Dictionary containing the shared resources between pools.
        """
        # init result dict
        if register is None:
            register = []
        urls: dict[str, list[str]] = {}
        if isinstance(register, list):
            # iterate the registered pools to create a dict with values and a list with the ids containing them
            registered_pools = [
                pool for pool in register if isinstance(pool, dict) and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if (
                    isinstance(pool, dict)
                    and pool.get("meta_url_log") is not None
                    and isinstance(pool["meta_url_log"], list)
                ):
                    for log in pool["meta_url_log"]:
                        if (
                            isinstance(log, dict)
                            and log.get("meta_url") is not None
                            and cls._is_valid_url(log["meta_url"])
                        ):
                            if log["meta_url"] in urls:
                                if (
                                    pool.get("pool_id_bech32") is not None
                                    and pool["pool_id_bech32"] not in urls[log["meta_url"]]
                                ):
                                    urls[log["meta_url"]].append(pool["pool_id_bech32"])
                            else:
                                urls[log["meta_url"]] = [pool["pool_id_bech32"]]
        # Filter the dictionary to include only the urls present in multiple pools
        return {value: value_pools for value, value_pools in urls.items() if len(value_pools) > 1}

    def set_registered_sharing_meta_url(self, register: list[dict[str, Any]] | None = None) -> None:
        """Update the registered_sharing_meta_url attribute.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools,
                when None it is loaded from the attribute. Defaults to None.
        """
        if register is None:
            register = self._register
        self.registered_sharing_meta_url = self.find_registered_sharing_meta_url(register)
        current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(  # noqa: T201
            f"[{current_time}] Found {len(self._registered_sharing_meta_url)} entries for registered_sharing_meta_url."
        )

    @staticmethod
    def find_registered_sharing_owners(  # noqa: C901
        register: list[dict[str, Any]] | None = None
    ) -> dict[str, list[str]]:
        """Find registered stake pools that shared at any time an owner address.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools. Defaults to None.

        Returns:
            dict[str, list[str]]: Dictionary containing the shared resources between pools.
        """
        # init result dict
        if register is None:
            register = []
        owners: dict[str, list[str]] = {}
        if isinstance(register, list):
            # iterate the registered pools to create a dict with values and a list with the ids containing them
            registered_pools = [
                pool for pool in register if isinstance(pool, dict) and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if (
                    isinstance(pool, dict)
                    and pool.get("owners_log") is not None
                    and isinstance(pool["owners_log"], list)
                ):
                    for log in pool["owners_log"]:
                        if isinstance(log, dict) and log.get("owners") is not None and isinstance(log["owners"], list):
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
        return {value: value_pools for value, value_pools in owners.items() if len(value_pools) > 1}

    def set_registered_sharing_owners(self, register: list[dict[str, Any]] | None = None) -> None:
        """Update the registered_sharing_owners attribute.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools,
                when None it is loaded from the attribute. Defaults to None.
        """
        if register is None:
            register = self._register
        self.registered_sharing_owners = self.find_registered_sharing_owners(register)
        current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(  # noqa: T201
            f"[{current_time}] Found {len(self._registered_sharing_owners)} entries for registered_sharing_owners."
        )

    @staticmethod
    def find_registered_sharing_reward_addr(register: list[dict[str, Any]] | None = None) -> dict[str, list[str]]:
        """Find registered stake pools that shared at any time a reward address.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools. Defaults to None.

        Returns:
            dict[str, list[str]]: Dictionary containing the shared resources between pools.
        """
        # init result dict
        if register is None:
            register = []
        addresses: dict[str, list[str]] = {}
        if isinstance(register, list):
            # iterate the registered pools to create a dict with values and a list with the ids containing them
            registered_pools = [
                pool for pool in register if isinstance(pool, dict) and pool.get("pool_status") == "registered"
            ]
            for pool in registered_pools:
                if (
                    isinstance(pool, dict)
                    and pool.get("reward_addr_log") is not None
                    and isinstance(pool["reward_addr_log"], list)
                ):
                    for log in pool["reward_addr_log"]:
                        if isinstance(log, dict) and log.get("reward_addr") is not None:
                            if log["reward_addr"] in addresses:
                                if (
                                    pool.get("pool_id_bech32") is not None
                                    and pool["pool_id_bech32"] not in addresses[log["reward_addr"]]
                                ):
                                    addresses[log["reward_addr"]].append(pool["pool_id_bech32"])
                            else:
                                addresses[log["reward_addr"]] = [pool["pool_id_bech32"]]
        # Filter the dictionary to include only the addresses present in multiple pools
        return {value: value_pools for value, value_pools in addresses.items() if len(value_pools) > 1}

    def set_registered_sharing_reward_addr(self, register: list[dict[str, Any]] | None = None) -> None:
        """Update the registered_sharing_reward_addr attribute.

        Args:
            register (list[dict[str, Any]] | None, optional): Register of pools,
                when None it is loaded from the attribute. Defaults to None.
        """
        if register is None:
            register = self._register
        self.registered_sharing_reward_addr = self.find_registered_sharing_reward_addr(register)
        current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print(  # noqa: T201
            f"[{current_time}] Found {len(self._registered_sharing_reward_addr)} entries for registered_sharing_reward_addr."
        )

    def _is_rule_safe(self, rule: str) -> bool:
        # The rule is invalid if contains something else than lowercase letters, uppercase letters, spaces, and parentheses
        pattern = r"^[a-zA-Z0-9 ()]*$"
        if bool(re.match(pattern, rule)) is False:
            return False
        # Filter the parentheses from the rule and check if all the words are allowed
        filtered_rule = re.sub(r"[^a-zA-Z0-9\s]", "", rule)
        allowed = self.CPC_MSPO_RULES_ALLOWED_KEYWORDS
        words = filtered_rule.split()
        # Return True if all words are allowed, otherwise return False
        return all(word in allowed for word in words)

    def _are_rule_vars_safe(self, my_vars: dict[str, bool]) -> bool:
        allowed = self.CPC_MSPO_RULES_ALLOWED_KEYWORDS
        # Return False if any key is a non allowed word or if values are not bool, otherwise return True
        return all(not (not isinstance(my_vars[my_var], bool) or str(my_var) not in allowed) for my_var in my_vars)

    def build_classified_pools(  # noqa: C901
        self,
        pools_path: str,
        pools_list: list[dict[str, str | list[str]]],
        config_rules: list[dict[str, str | dict[str, str]]],
    ) -> dict[str, list[dict[str, str | list[str]]]]:
        """Builds lists of stake pools by classifying them using the provided rules.

        Args:
            pools_path (str): The path where the pool resources listings are stored.
            pools_list (list[dict[str, str | list[str]]]): The list of pools to classify.
            config_rules (list[dict[str, str  |  dict[str, str]]]): The rules to use for classifying.

        Returns:
            dict[str, list[dict[str, str|list[str]]]]: The classified lists of pools.
        """
        # Use a dictionary to store results for each rule
        result_files = {}
        # Get the allowed keywords in the rules definition
        allowed = self.CPC_MSPO_RULES_ALLOWED_KEYWORDS
        # Process each defined rule
        for rule in config_rules:
            matching_ids = []
            non_matching_ids = []
            for pool in pools_list:
                if isinstance(pool["pool_id_bech32"], str):
                    id_value = pool["pool_id_bech32"]
                reason = []
                variables = {}
                if isinstance(rule["files"], dict):
                    for var, filename in rule["files"].items():
                        with open(os.path.join(pools_path, filename)) as file:
                            file_content = json.load(file)
                        variables[var] = id_value in str(file_content)
                if (
                    isinstance(rule["rule"], str)
                    and self._is_rule_safe(rule["rule"])
                    and self._are_rule_vars_safe(variables)
                ):
                    if eval(rule["rule"], variables):  # noqa: S307, PGH001
                        for var in variables:
                            if variables[var] and (var in allowed) and isinstance(rule["files"], dict):
                                reason.append(self.CPC_POOLS_URL + str(rule["files"].get(var)))  # noqa: PERF401
                        my_pool = pool.copy()
                        my_pool["reason"] = reason
                        matching_ids.append(my_pool)
                    else:
                        non_matching_ids.append(pool)
            if isinstance(rule["matching_file"], str) and isinstance(rule["non_matching_file"], str):
                result_files[rule["matching_file"]] = matching_ids
                result_files[rule["non_matching_file"]] = non_matching_ids
        return result_files

    def set_classified_pools(self) -> None:
        """Update the classified_pools attribute."""
        # Get the list of pools
        try:
            with open(os.path.join(os.path.dirname(__file__), self.CPC_DATA_DIR, self.CPC_POOLS_LIST_FILENAME)) as file:
                pools_list = json.load(file)
        except FileNotFoundError:
            print("Pools list File not found.")  # noqa: T201
        except OSError as exc:
            msg = "Error reading the pools list file."
            raise OSError(msg) from exc
        # Get the classify rules
        config_rules = self.CPC_MSPO_RULES
        # Execute classify rules and set the attribute (optionally save to disk)
        self.classified_pools = self.build_classified_pools(
            os.path.join(os.path.dirname(__file__), self.CPC_DATA_DIR), pools_list, config_rules
        )
        # Show statistics
        for rule in self.classified_pools:
            current_time = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] Found {len(self.classified_pools[rule])} entries for {rule!s} rule.")  # noqa: T201
