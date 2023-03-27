import os
from glob import glob
from typing import List, Union
import re

from .logger import logger
from .utils import get_event_name
from .api.zenodo_interface import get_zenodo_urls

CACHE_ENV_VAR = "NRSUR_CATALOG_CACHE_DIR"
DEFAULT_CACHE_DIR = "./.nrsur_catalog_cache"
NR_FILE_EXTENSION = "_NRSur7dq4_merged_result.hdf5"
LVK_FILE_EXTENSION = "_mixed_cosmo.h5"


class CatalogCache:

    def __init__(self, cache_dir: str):
        """Class to handle the cache directory"""
        assert cache_dir is not None, "Cache directory must be specified"
        self._cache = cache_dir
        os.makedirs(self._cache, exist_ok=True)

    @property
    def dir(self)-> str:
        return os.path.abspath(self._cache)

    @property
    def list(self):
        return self._list()

    @property
    def list_lvk(self):
        return self._list(lvk_posteriors=True)

    def _list(self, lvk_posteriors=False) -> List[str]:
        """List the contents of the cache directory (sorted by number in filename)"""
        file_extension = LVK_FILE_EXTENSION if lvk_posteriors else NR_FILE_EXTENSION
        file_regex = os.path.join(self._cache, f"*{file_extension}")
        files = glob(file_regex)
        files = sorted(
            files, key=lambda x: int(re.findall(r"\d+", os.path.basename(x))[0])
        )
        return files

    @property
    def event_names(self) -> List[str]:
        """List the event names in the cache directory"""
        return [get_event_name(f) for f in self.list]

    @property
    def event_names_lvk(self) -> List[str]:
        """List the event names in the cache directory"""
        return [get_event_name(f) for f in self.list_lvk]

    def find(self, name: str, hard_fail=False, lvk_posteriors=False) -> str:
        """Find a file in the cache directory"""
        file_extension = LVK_FILE_EXTENSION if lvk_posteriors else NR_FILE_EXTENSION
        filepath = f"{self._cache}/{name}{file_extension}"
        if os.path.exists(filepath):
            return filepath
        if hard_fail:
            logger.debug(f"Current cache: {self.list} (doesnt have {filepath})")
            raise FileNotFoundError(
                f"Could not find {name} in cache dir {self.cache_dir}"
            )
        return ""

    def check_if_events_cached_in_zenodo(self, lvk_posteriors=False):
        """Return a list of events that are in the cache and in Zenodo"""
        zenodo_events = set(get_zenodo_urls(lvk_posteriors).keys())
        local_events = set(self.event_names)
        if zenodo_events != local_events:
            logger.warning(
                f"Events in cache do not match events in Zenodo.\n"
                f"local: {local_events},\n"
                f"zenodo: {zenodo_events},\n"
                f"missing: {zenodo_events - local_events},\n"
                "Uploading the events to zenodo after building the website."
            )

    @property
    def is_empty(self):
        return len(self.list) == 0

