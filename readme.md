# Web Scraping Boilerplate

[👉 Read more about this repository here.](https://blog.hartleybrody.com/web-scraping-boilerplate/)

In the spirit of my [flask boilerplate](https://github.com/hartleybrody/flask-boilerplate) project, I figured it would be helpful to create a web scraping boilerplate repo. This will contain all of the common, generic helpers that I use on most scraping efforts to help get new projects off the ground faster.

Specifically, it helps with:

 - using a database to store scraped data
 - helpers for making requests and handling network errors
 - getting python packages installed (requests, beautiful soup)
 - setting up redis to manage a queue of work
 - rotating proxies and detecting ones that aren't working
 - keeping track of which data was collected when
 - managing changes to the database model over time

There's nothing specific to scraping one particular site in here, all of this functionality is agnostic to the target site. This makes it useful as a base for any new scraping project, where it's collecting data from retailers, government sites or social networks.


----

Here are the steps for getting your system initially setup.

### Install python dependencies
This project assumes you already have [virtualenv, virtualenvwrapper](http://docs.python-guide.org/en/latest/dev/virtualenvs/) and [autoenv](https://github.com/kennethreitz/autoenv) installed globally on your system.

First, create a new virtual environment:

    mkvirtualenv {{PROJECT_SLUG}}

Then, install the required python dependencies

    pip install -r requirements.txt

### Setup local postgres database
Create the database locally

    psql -h localhost -d postgres

    psql (10.1)
    Type "help" for help.

    postgres=# CREATE DATABASE {{PROJECT_SLUG}};
    CREATE DATABASE


### Setup local redis server
You can install redis using [the project's Quickstart instructions](https://redis.io/topics/quickstart).

Or, if you're on macOS with homebrew, you can simply run

    brew install redis

Once you've got redis installed on your system, start the local server in the background with

    redis-server  --daemonize yes


### Run database migrations
Detect changes to `models.py` and generate a timestamped migration file

    alembic revision --autogenerate

Once you've looked over the generated migrations file, apply the migration to the database

    alembic upgrade head

Note that you will need to run both of these commands once at initial setup to get your database setup.

You can roll back a migration using

    alembic downgrade -1

### Proxies
A list of proxy IPs and ports should be stored in `input/proxies.txt`.

They should be listed one per line, in the following format:

    {ip_address}:{port}

If proxies are required to run the scrape -- meaning the scrape should stop if no proxies are available -- then you should set the following environment variable:

    export PROXIES_REQUIRED="true"

Note that once the target site identifies a proxy and blocks it, that proxy will be removed from the in-memory proxy list for that scrape (it is not removed from the proxies file). This means that a scrape may start out with a full list of proxies but end up grinding to a halt if requests are made too frequently and proxies started to get detected by the target site and removed from the proxy list until none are left.

From experience running this scrape, with 50 proxies you should not use more than 4 workers running requests at the same time.

If proxies are not required to scrape (ie due to low-volume local testing) you can disable that check by setting

    export PROXIES_REQUIRED="false"

