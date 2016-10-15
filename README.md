## TelegramSchoolBot [![MIT License](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](LICENSE)
_Check your school hours with telegram!_

This bot was created for my school to simplify the interaction with their website by using telegram.

It allows you to check the school hours of a class or of a teacher and to receive notifications when new announcements are posted on the website.

### Compatibility
This bot has only been tested on my school website which is using the [Yoomla CMS](https://www.joomla.org/) with the [JSN Epic](https://www.joomlashine.com/joomla-templates/jsn-epic-joomla-template-details.html) template with the link to the article containing the link to the page created with [Orario Facile 8](https://www.orariofacile.com/) on the left side of the screen. The path to the page created with ``Orario Facile`` must start with ``/web_orario`` or ``/weborario``.

You can easily adapt it to your school website by customizing it, you only need to know a little bit of Python and understand the basic concepts of HTML.

### Cloning the repository and installing the dependencies
The first thing you need to do to host this bot for your school is to install python 3.5 if you didn't already.

Now clone this repository and install the requirements by using the following commands:

    $ git clone https://github.com/paolobarbolini/TelegramSchoolBot.git
    $ cd TelegramSchoolBot
    $ pip3 install -r requirements.txt

Now download ``wkhtmltopdf`` from their [official website](http://wkhtmltopdf.org/downloads.html) and extract the contents into the bot main directory.

### Compatibility with botogram 0.3.4
The latest version of the bot is using an in dev version of botogram, if you want to use the version compatible with botogram 0.3.4 remove ``bot.link_preview_in_help = False`` and remove the ``order`` argument from all of the ``@bot.command`` decorators

### Creating a new telegram bot
You can find all of the instructions on how to create a new bot [here](https://core.telegram.org/bots#6-botfather)

### Setup
Now open ``config.py`` and set the bot token that BotFather gave you.

You also must configure your school website home page url.

### Contributing
I highly appreciate your contributions in the matter of fixing bugs and optimizing the bot source code, but i won't accept your pull request if it adds features that i don't want to get added to the bot for my school or if it breaks compatibility with my school website.

If you want to talk to me about a feature you would like to add please open an issue and i will answer to you as soon as possible.
