"""
Interact with your school website with telegram!

Copyright (c) 2016-2017 Paolo Barbolini <paolo@paolo565.org>
Released under the MIT license
"""

import botogram

from . import commands
from . import database
from . import tasks
from . import utils


class TelegramSchoolBot:
    """Main instance of the bot"""

    def __init__(self, config):
        self.config = config
        self.db = database.Database(self.config)

        self.bot = botogram.create(config["telegram_token"])
        self.bot.lang = "it"
        self.bot.owner = config["owner"]
        self.bot.about = "Ricevi gli orari scolastici e gli avvisi dal sito " \
                         + utils.shorten_url(config["school_website"])
        self.bot.after_help = [
            "Sai programmare?",
            "<a href=\"https://github.com/paolobarbolini/TelegramSchoolBot\">"
            "Questo bot è opensource!</a>",
        ]
        self.bot.link_preview_in_help = False

        self.bot.use(commands.Commands(self.db))
        self.bot.use(tasks.Tasks(self.config, self.db))

    def run(self):
        self.bot.run()
