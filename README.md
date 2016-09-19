## TelegramSchoolBot
This bot allows you to check the school hours with telegram.

At the moment it is compatible only with websites that use ``Yoomla`` with the ``JSN Epic`` template and with the link to the article containing the link to the page created with ``Orario Facile 8`` on the left side of the screen.

You can easily adapt it to yor school's website by customizing the bot using BeautifulSoup4, you only need to know a little bit of Python and HTML.

### Cloning the repository and installing the dependencies
The first thing you need to do to host your bot for your school is to install python 3.5 if you didn't already.

After doing that you need to clone this repository and install the requirements by using the following commands:

    $ git clone https://github.com/paolo565/TelegramSchoolBot.git
    $ cd TelegramSchoolBot
    $ pip3 install -r requirements.txt

You also have to install ``wkhtmltopdf``, to do that simply download it from the official website http://wkhtmltopdf.org/downloads.html and extract the contents in the bot root directory

### Creating a new telegram bot
You can find all of the instruction on how to create a new bot here: https://core.telegram.org/bots#6-botfather

### Setting up the bot
Now open ``config.py`` and set the bot token to the one that BotFather gave you

You will also need to add your school's main page website full url