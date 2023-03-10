"""Module to get zenodo URLs from NRSur Catlog zenodo page"""

import os
from ..logger import logger
from ..utils import get_event_name

HERE = os.path.dirname(os.path.abspath(__file__))
URL_FILE = os.path.join(
    HERE, "zenodo_urls.txt"
)  # This file's contents are autogenerated

TITLE = "NRSurrogate Catalog Posteriors"


def _commit_url_file():
    try:
        import git

        repo_root = os.path.join(HERE, "../../..")
        repo = git.Repo(repo_root)
        repo.git.add(URL_FILE)
        repo.git.commit(m=f"update urls [automated]")
        repo.git.push()
    except Exception as e:
        pass


def cache_zenodo_urls_file(sandbox=True) -> None:
    """Update the file URLs to the data on zenodo"""
    from zenodo_get import zenodo_get
    from zenodo_python import Deposition

    zeno = Deposition.from_title(title=TITLE, test=sandbox)
    logger.info(f"Zenodo {zeno} has {len(zeno.files)} files. Caching download URLs.")
    zeno.save_wget_file(URL_FILE)
    file_contents = open(URL_FILE, "r").read()
    logger.info(f"Finished caching Zenodo URLs to {URL_FILE}:\n{file_contents}")
    _commit_url_file()


def get_zenodo_urls() -> dict:
    """Returns a dictionary of the analysed events and their urls"""
    # read in the zenodo_urls.txt file (each line is a url)
    with open(URL_FILE, "r") as f:
        urls = f.readlines()
        urls = [url.strip() for url in urls]

    if len(urls) == 0:
        raise RuntimeError(f"No URLs found in {URL_FILE}")

    # extract the event name from the url
    event_names = [get_event_name(url) for url in urls]
    return dict(zip(event_names, urls))


def check_if_event_in_zenodo(event_name: str) -> bool:
    """Check if the event is in Zenodo"""
    return event_name in get_zenodo_urls()
