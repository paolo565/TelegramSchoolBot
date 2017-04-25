# TelegramSchoolBot [![MIT License](https://img.shields.io/github/license/paolobarbolini/TelegramSchoolBot.svg?maxAge=2592000)](LICENSE)
_Interact with your school website with telegram!_

This bot was created to simplify the interaction with my school's website by using telegram.

It allows you to check the school hours of a class, a teacher or a classroom and to optionally receive notifications when new announcements are posted on their website.

## Compatibility
This bot has only been tested on my school website which is using the [Yoomla CMS](https://www.joomla.org/) with the [JSN Epic](https://www.joomlashine.com/joomla-templates/jsn-epic-joomla-template-details.html) template.
The link to the article containing the link to the page created with [Orario Facile 8](https://www.orariofacile.com/) is on the left side of the screen.
The path to the page created with ``Orario Facile`` must start with ``/web_orario`` or ``/weborario``.

It is licensed under the [MIT License](LICENSE), which basically allows you to do whatever you want with it as long as you preserve the copyright and license notices.
You can easily make it work with your school website by adapting the code to it, you only need to know a little bit of Python and HTML.

## Required dependencies
This bot requires the following dependencies to work:

* make (apt: `build-essential`)
* Python 3 (apt: `python3`)
* PIP (apt: `python3-pip`)
* Virtualenv (apt: `python-virtualenv`, pip: `virtualenv`)
* Git (apt: `git`)

You can easily install them with the following commands:

```
$ sudo apt install build-essential python3 python3-pip git
$ sudo pip3 install virtualenv
```

## Initialization
All of the configurations are stored in the `config.json` file, to create it run:

```
$ make init
```

Before running the but you have to edit `config.json`:

```json
{
  "telegram_token": "BOT-API-KEY",
  "school_website": "URL-OF-YOUR-SCHOOL-WEBSITE",
  "owner": "@YOUR-TELEGRAM-USERNAME"
}
```

The parameters are:

* `telegram_token` is the api key of your telegram bot, you can [generate one here](https://core.telegram.org/bots#6-botfather).
* `school_website` is the url of the homepage of your school website
* `owner` is the username on telegram you wish to be contacted.

## Running the bot
After having configured the bot you can run it by using:

```
$ make run
```

The first time it will take a few minutes to start because it has to build the virtualenv and install the dependencies.

## Contributing
I highly appreciate your contributions in the matter of fixing bugs and optimizing the bot source code, but i won't accept your pull request if it adds features that i don't want to get added to it or if it breaks compatibility with my school website.

If you want to talk to me about a feature you would like to add please open an issue and i will answer to you as soon as possible.
