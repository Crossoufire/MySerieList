# MyLists

MyLists is a website with a nice and clear interface which allows you to track all your TV shows / Anime and Movies. 
It integrates statistics so you can see how much time you spent. Moreover, you can see follow people, see their list  
and compare it to yours. You can see a live version here : [https://mylists.info](https://mylists.info).

![MyLists](https://raw.githubusercontent.com/Crossoufire/MyLists/master/MyLists/static/img/home222.jpg)

MyLists uses [Flask](http://flask.pocoo.org/) and [Material Design for Bootstrap 4](https://mdbootstrap.com/)

## Features

* Create a list of all your TV shows / Anime and Movies
* Compare your list with your follows
* Get statistics about your list (time spent, number of episodes watched, prefered genres, etc)
* More to come !

## Prerequisites

* Python 3.6+ (developed and tested with this version)
* pip3

## Installation

```
git clone https://www.github.com/Crossoufire/MyLists.git
cd MyLists
pip3 install -r requirements.txt
```

Before starting the program, you *MUST* create a `config.ini` file respecting the following syntax :

```
[Flask]
secret = <random_value>

[Mail]
email = <mail used for sending registration / reset password / email update email>
password = <password of the email>
server = <server to connect to>
port = <port to connect to>

[TheMovieDB]
api_key = <API key of TheMovieDB. You need to register on their website to get one>

[OAuth]
twitter_id = <twitter_id>
twitter_secret = <twitter_secret>
```

For example if you want to use Gmail, set `server = smtp.gmail.com` and `port = 465` . If you need more settings, feel 
free to adapt it as you want (file `Mylists/__init__.py`, parameters `app.config['MAIL_X]`).

If you want to first test the project locally, you should change the values of `app.config['TESTING']` to `True` and 
`app.config["SESSION_COOKIE_SECURE"]` to `False` in the `Mylists/__init__.py` file.

Then run the command `python3 Run.py` and open the link [http://localhost:5000](http://localhost:5000).

## Administration

When you run the program for the first time, it will create 3 users : one `user`, one `manager` and one `admin` with all the same the password `password`:

* `user`: standard user
* `manager`: standard user with the right to manage media:
    * Can lock any media so it won't be updated anymore by the APScheduler (to be used for old media with no more update needed)
    * When a media is locked, can edit its metadata
* `admin`: Used for administration tasks (access to all `/admin` pages). Should not be used as a standard user account. Does not appear in Hall of fame and its statistics are not taken into account.

## Misc

We started this project to fulfill our needs. The live version [https://mylists.info](https://mylists.info) runs on a 
raspberry pi 3B+, thus not meant to be used by a lot of people at the same time. If you can see the register button 
at the top right of the homepage, feel free to do it. Otherwise, you can run your own version of MyLists ;)

## Contact

<contact@mylists.info>