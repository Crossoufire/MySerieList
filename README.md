# MyLists

MyLists is a website with a beautiful and clear interface which allows you to track all your TV shows without remembering what was your last watched episode. It integrates all kind of statistics so you can see how much time you spent. Moreover, you can see you friends' list and compare it to yours. You can see a live version here : [https://mylists.info](https://mylists.info).

![MyLists](https://raw.githubusercontent.com/Crossoufire/MyLists/master/MyLists/static/img/home_img1.jpg)

MyLists uses [Flask](http://flask.pocoo.org/) and [Material Design for Bootstrap 4](https://mdbootstrap.com/)

## Features

* Create a list of all your TV shows
* Compare your list with your friends
* Get statistics about your list (time spent, number of episodes watched, etc)
* More to come !

## Prerequisites

* Python 3.6 (developed and tested with this version)
* pip3

## Installation

```
git clone https://www.github.com/Crossoufire/MyLists.git
cd MyLists
pip3 install -r requirements.txt
```

Before starting the program, you MUST create a `config.ini` file respecting the following syntax :

```
[Flask]
secret = <random_value>

[Mail]
email = <mail used for sending registration / reset password / email update email>
password = <password of the email>

[Captcha]
public_key = <public key of Google reCAPTCHA>
private_key = <private key of Google reCAPTCHA>

[TheMovieDB]
api_key = <API key of TheMovieDB. You need to register on their website to get one>
```

The default configuration used for the mails uses Gmail. Feel free to adapt it as you want (file `Mylists/__init__.py`, parameters `app.config['MAIL_X]`).

If you want to first test the project locally, you should change the values of `app.config['TESTING']` to `True` and `app.config["SESSION_COOKIE_SECURE"]` to `False` in the `Mylists/__init__.py` file.

Then run the command `python3 Run.py` and open the link [http://localhost:5000](http://localhost:5000).

## Administration

When you run the program for the first time, it will create a user `admin` with the password `password` with the ID `1`. Do NOT forget to change the password. This can be done at the beginning of the file `Mylists/routes.py` or using the UI. All the administration tasks are filtered on the user ID (ID == 1), so feel free to also change the username if you want (again in the file `Mylists/routes.py` or using the UI). The admin has access to the pages `/admin`.
 
## Misc

We started this project to fulfill our needs. The live version [https://mylists.info](https://mylists.info) runs on a potato server, thus not meant to be used by thousand people at the same time. If you still can see the register button at the top of the homepage, feel free to do it. Otherwise, run your own version of MyLists :)

## Contact

<contact@mylists.info>