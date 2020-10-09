# real-estate-scrape

Get the estimated value of an address from Redfin and Zillow every night and
store the result.

Redfin and Zillow both give you an estimate of the current market value of your
home. That estimate is given to the nearest dollar, and comes with a chart that
claims to be the history of that estimate. That historical chart is a lie. The
estimate for today bounces around a lot, but they retcon the history to pretend
it doesn't. The precision of today's estimate and the smoothness of the chart
make the estimate look ridiculously trustworth. This scraper captures the
bouncing, which gives you a good idea how much to trust the current value
(probably good to 10-20% at most).

See [`data.csv`](data.csv) and [`data.pdf`](data.pdf) for example output for
[594 S Mapleton Dr, Los
Angeles](https://www.redfin.com/CA/Los-Angeles/594-S-Mapleton-Dr-90024/home/6824711)
(not my house, maybe I should stop giving away my elite scraping code for free).

This repository uses [the git scraping
pattern](https://simonwillison.net/2020/Oct/9/git-scraping/), i.e. GitHub
actions run a cron job, and git stores the version controlled output of that
cron job.

## Usage: recurring job

1. Sign up for [Proxybot](https://proxybot.io/) and make a note of your API key.
   A free account is enough to use this scraper for a few weeks, at which point
   a couple of dollars will buy you enough Proxybot credits to last for the
   remainder of your mortgage.

2. Fork this repository on GitHub

3. Under Settings > Secrets, configure environment variables containing the URLs
   of the address on Redfin and Zillow and your Proxybot key:
    - `REDFIN_URL`, e.g.
      `https://www.redfin.com/CA/Los-Angeles/594-S-Mapleton-Dr-90024/home/6824711`
    - `ZILLOW_URL`, e.g.
      `https://www.zillow.com/homedetails/594-S-Mapleton-Dr-Los-Angeles-CA-90024/20524417_zpid/`
    - `PROXYBOT_KEY`, e.g.`abcdefqwert12345`

The scraping job runs every day at 5am UTC. Come back in 24 hours and you should
find `data.csv` in your forked repository. Come back a few days later and you
should see the beginnings of a chart in `data.pdf`.

Alternatively, you can run the scraping job manually as often as you like by
clicking "Run workflow" under Actions > scrape on GitHub.

## Usage: manually from your own machine

Clone the repository, export `REDFIN_URL` and `ZILLOW_URL` and run `python
real_estate_scrape.py`. You probably won't need Proxybot if you're running this
from a home internet connection.

## Adding a new site

To add a new site:

 - add an entry in `sites.json`
 - set `xpath` to the xpath containing the piece of data you want to collect
 - export the `<NAME>_URL` environment variable, where `<NAME>` should be
   replaced with the upper case version of the `"name"` field in sites.json.
 - if you want to keep the history in `data.csv` manually edit its header to add
   the new site (otherwise `data.csv` will be overwritten with an empty table).

## Caveats

 - The Zillow scraper doesn't work if the house is on the market. The page
   layout changes and I can't figure out the xpath. PRs welcome.
