"""
Interact with your school website with telegram!

Copyright (c) 2016-2017 Paolo Barbolini <paolo@paolo565.org>
Released under the MIT license
"""

from botogram.objects import Update
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import click
import json
import os.path

from . import bot
from . import models


@click.group()
def cli():
    pass


@cli.command()
def init():
    """Init TelegramSchoolBot"""

    config = {
        "telegram_token": "BOT_TOKEN",
        "school_website": "SCHOOL_WEBSITE_HOMEPAGE_URL",
        "owner": "@TELEGRAM_BOT_OWNER_USERNAME",
        "database_url": "sqlite:///database.db",
    }

    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)
        f.write("\n")


@cli.command()
def initdb():
    """Init the database"""
    with open("config.json") as f:
        config = json.load(f)

    engine = create_engine(config["database_url"])
    session = sessionmaker()
    session.configure(bind=engine)

    models.Base.metadata.create_all(engine)


@cli.command()
def run():
    """Run TelegramSchoolBot"""

    with open("config.json") as f:
        config = json.load(f)

    instance = bot.TelegramSchoolBot(config)
    instance.run()


if __name__ == "__main__":
    cli()
