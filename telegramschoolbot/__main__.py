"""
Interact with your school website with telegram!

Copyright (c) 2016-2017 Paolo Barbolini <paolo@paolo565.org>
Released under the MIT license
"""

from botogram.objects import Update
import click
import json

from . import bot
from . import models


@click.group()
def cli():
    pass


@cli.command()
def init():
    "Init TelegramSchoolBot"

    config = {
        "telegram_token": "BOT_TOKEN",
        "school_website": "SCHOOL_WEBSITE_HOMEPAGE_URL",
        "owner": "@TELEGRAM_BOT_OWNER_USERNAME"
    }

    with open("config.json", "w") as f:
        json.dump(config, f)

    if not models.PageModel.exists():
        models.PageModel.create_table(read_capacity_units=1, write_capacity_units=2)

    if not models.PostModel.exists():
        models.PostModel.create_table(read_capacity_units=1, write_capacity_units=1)

    if not models.SubscriberModel.exists():
        models.SubscriberModel.create_table(read_capacity_units=1, write_capacity_units=1)


@cli.command()
def run():
    "Run TelegramSchoolBot"

    with open("config.json") as f:
        config = json.load(f)

    instance = bot.TelegramSchoolBot(config)
    instance.run()


@cli.command()
@click.argument("update")
def process(update):
    "Process a telegram update"

    with open("config.json") as f:
        config = json.load(f)

    parsed_update = json.loads(update)
    update_object = Update(parsed_update)

    instance = bot.TelegramSchoolBot(config)
    instance.bot.process(update_object)


if __name__ == "__main__":
    cli()
