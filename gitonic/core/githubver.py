from const import VERSION

import semver
from urllib3 import request

URL = "https://api.github.com/repos/kr-g/gitonic/tags"


def mkver(x):
    return x[1:]


def check_github_new_version():

    res = request("GET", URL)

    verslist_published = list(map(lambda x: mkver(x['name']), res.json()))

    verlist_published = list(
        map(lambda x: semver.Version.parse(x), verslist_published))

    latest_published = max(verlist_published)

    version_current = semver.Version.parse(mkver(VERSION))

    if version_current < latest_published:
        return latest_published


if __name__ == "__main__":
    if latest_published := check_github_new_version():
        print(f"you are using gitonic {
              VERSION}. there is a new version available {latest_published}")
