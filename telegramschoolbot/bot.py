"""
Interact with your school website with telegram!

Copyright (c) 2016-2017 Paolo Barbolini <paolo@paolo565.org>
Released under the MIT license
"""

import botogram
import html
import os

from . import commands
from . import tasks
from . import models
from . import utils


class TelegramSchoolBot:
    """Main instance of the bot"""

    def __init__(self, config):
        self.config = config
        self.bot = botogram.create(self.config["telegram_token"])

        self.bot.lang = "it"

        self.bot.owner = self.config["owner"]
        self.bot.about = "Questo bot ti da gli orari scolastici dal sito " + utils.shorten_url(self.config["school_website"])
        self.bot.after_help = [
            "Sai programmare? Questo bot è opensource!",
            "<a href=\"https://github.com/paolobarbolini/TelegramSchoolBot\">Clicca qui</a> per andare alla pagina github.",
        ]
        self.bot.link_preview_in_help = False

        self.bot.use(commands.Commands())
        self.bot.use(tasks.Tasks(self.config))


    def run(self):
        self.bot.run()
