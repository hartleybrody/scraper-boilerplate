# Web Scraping Boilerplate

In the spirit of my [flask boilerplate](https://github.com/hartleybrody/flask-boilerplate) project, I figured it would be helpful to create a web scraping boilerplate repo. This will contain all of the common, generic helpers that I use on most scraping efforts to help get new projects off the ground faster.

Specifically, it helps with:

 - getting python packages installed (requests, beautiful soup)
 - setting up redis to manage a work queue
 - helpers for making and retrying requests
 - logic for rotating proxies and detecting ones that aren't working
 - using a database to store scraped data

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
