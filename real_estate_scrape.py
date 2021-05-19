import json
import os
import re
from datetime import datetime, timezone

import matplotlib.pyplot as plt
import pandas as pd
import requests
from lxml import html

csvfile = "data.csv"
plotfile = "data.png"

with open("sites.json") as f:
    sites = json.load(f)


def get_value(url, xpath):
    session = requests.Session()
    # User-Agent required otherwise you get blocked
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    try:
        scraperapi_key = os.environ["SCRAPERAPI_KEY"]
        session.params = {
            "api_key": scraperapi_key,
            "url": url,
        }
        url = "http://api.scraperapi.com"
    except KeyError:
        pass
    response = session.get(url, timeout=60)
    tree = html.fromstring(response.content)
    value = tree.xpath(xpath)[0]
    return re.sub(r"[\$,\,]", "", value)


def try_get_value(*args, **kwargs):
    try:
        return get_value(*args, **kwargs)
    except requests.exceptions.Timeout:
        print(f"{args=}, {kwargs=}: Request timed out")
    except requests.exceptions.RequestException:
        print(f"{args=}, {kwargs=}: Request failed")
    except KeyError:
        print(f"{args=}, {kwargs=}: Could not parse response")
    except Exception as e:
        print(f"{args=}, {kwargs=}: Failed for unknown reason")
        print(f"{e=}")
    return "NaN"


def retry_get_value(n=3, *args, **kwargs):
    i = 0
    while i < n:
        value = try_get_value(*args, **kwargs)
        if value != "NaN":
            return value
        i += 1
    return value


def ensure_csv():
    """Make sure a CSV with the appropriate header exists."""
    expected_header = "date," + ",".join(site["name"] for site in sites) + "\n"
    try:
        with open(csvfile) as f:
            header = next(f)
            assert header == expected_header
    except (FileNotFoundError, AssertionError):
        with open(csvfile, mode="w") as f:
            f.write(expected_header)


def append_csv(values):
    # https://stackoverflow.com/a/28164131/409879
    ensure_csv()
    datetime_string = datetime.now(timezone.utc).astimezone().isoformat()
    line = f"{datetime_string},{','.join(str(v[1]) for v in values)}\n"
    with open(csvfile, mode="a") as f:
        f.write(line)


def plot_file():
    df = pd.read_csv(csvfile, index_col="date", parse_dates=True)
    ax = df.plot()
    ax.ticklabel_format(style="plain", axis="y")  # no exponential notation on y-axis
    ax.set_ylabel("Estimated value ($)")
    ax.set_xlabel(f"Date (last updated {df.index[-1].date().isoformat()})")
    ax.grid()
    plt.rcParams["savefig.dpi"] = 144
    ax.get_figure().savefig(plotfile, bbox_inches="tight")


if __name__ == "__main__":
    values = []
    for site in sites:
        try:
            url = site["url"]
        except KeyError:
            url = os.environ[site["name"].upper() + "_URL"]
        value = retry_get_value(url=url, xpath=site["xpath"])
        print(f"{site['name']} {value=}")
        values.append((site["name"], value))
    append_csv(values)
    plot_file()
