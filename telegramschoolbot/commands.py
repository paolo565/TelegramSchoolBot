"""
Interact with your school website with telegram!

Copyright (c) 2016-2017 Paolo Barbolini <paolo@paolo565.org>
Released under the MIT license
"""

import botogram
import html

from . import models
from . import utils


class Commands(botogram.components.Component):
    """All of the TelegramSchoolBot commands"""

    component_name = "tsb-commands"

    TABLES = {
        "Di quale classe vuoi sapere l'orario?": "class",
        "Qual'è il nome del prof di cui vuoi sapere l'orario?": "teacher",
        "Di quale aula vuoi sapere l'orario?": "classroom",
    }

    TABLE_MESSAGE = {
        "class": "Classe: %s",
        "teacher": "Prof: %s",
        "classroom": "Aula: %s",
    }

    def __init__(self, db):
        self.db = db
        self.add_command("start", self.start_command, hidden=True)
        self.add_command("notifiche", self.notification_command, order=10)
        self.add_command("classe", self.class_command, order=20)
        self.add_command("prof", self.prof_command, order=30)
        self.add_command("aula", self.classroom_command, order=40)
        self.add_process_message_hook(self.message_received)
        self.add_chat_unavailable_hook(self.chat_unavailable)


    def start_command(self, bot, chat):
        lines = [
            bot.about,
            "",
            "Utilizza /help per ricevere la lista dei comandi.",
            "Per ricevere una notifica quando esce un nuovo avviso fai /notifiche",
        ]

        chat.send("\n".join(lines))


    def notification_command(self, bot, chat, message, args):
        """Abilita/Disabilita le notifiche."""

        session = self.db.Session()

        subscriber = session.query(models.Subscriber).filter(models.Subscriber.chat_id == chat.id).first()
        if not subscriber:
            session.add(models.Subscriber(chat_id=chat.id))

            lines = [
                "Iscrizione alle notifiche completata con successo.",
                "Entro un'ora dalla pubblicazione di una circolare sul sito riceverai una notifica.",
                "Non bloccare il bot altrimenti sarai disiscritto automaticamente dalle notifiche.",
            ]
        else:
            session.delete(subscriber)

            lines = [
                "Disiscrizione dalle notifiche completata con successo.",
                "Per riabilitarle fai /notifiche",
            ]

        session.commit()

        message.reply("\n".join(lines))


    def class_command(self, bot, chat, message, args):
        """Mostra gli orari di una classe."""

        if len(args) == 0:
            message.reply("Di quale classe vuoi sapere l'orario?", syntax="plain",
                          extra=botogram.ForceReply(data={
                              "force_reply": True,
                              "selective": True,
                          }))
            return

        name = " ".join(args)
        session = self.db.Session()
        page = session.query(models.Page).filter((models.Page.name.ilike(name)) & (models.Page.type == "class")).first()

        if not page:
            message.reply("Non ho trovato la classe <b>%s</b>" % html.escape(name), syntax="html")
            return

        utils.send_page(self.db, bot, message, page, "Classe: %s" % page.name)


    def prof_command(self, bot, chat, message, args):
        """Mostra gli orari di un prof."""

        if len(args) == 0:
            message.reply("Qual'è il nome del prof di cui vuoi sapere l'orario?", syntax="plain",
                          extra=botogram.ForceReply(data={
                              "force_reply": True,
                              "selective": True,
                          }))
            return

        name = " ".join(args)
        session = self.db.Session()
        pages = session.query(models.Page).filter((models.Page.name.ilike(name + "%")) & (models.Page.type == "teacher")).limit(2)
        pages = list(pages)

        if len(pages) == 0:
            message.reply("Non ho trovato il prof <b>%s</b>" % html.escape(name), syntax="html")
            return
        if len(pages) > 1:
            message.reply("I criteri di ricerca inseriti coincidono con più di un risultato.")
            return

        utils.send_page(self.db, bot, message, pages[0], "Prof: %s" % pages[0].name)


    def classroom_command(self, bot, chat, message, args):
        """Mostra gli orari di un'aula."""

        if len(args) == 0:
            message.reply("Di quale aula vuoi sapere l'orario?", syntax="plain",
                          extra=botogram.ForceReply(data={
                              "force_reply": True,
                              "selective": True,
                          }))
            return

        name = " ".join(args)
        session = self.db.Session()
        pages = session.query(models.Page).filter((models.Page.name.ilike(name + "%")) & (models.Page.type == "classroom")).limit(2)
        pages = list(pages)

        if len(pages) == 0:
            message.reply("Non ho trovato l'aula <b>%s</b>" % html.escape(name), syntax="html")
            return
        if len(pages) > 1:
            message.reply("I criteri di ricerca inseriti coincidono con più di un risultato.")
            return

        utils.send_page(self.db, bot, message, pages[0], "Aula: %s" % pages[0].name)


    def message_received(self, bot, chat, message):
        query = message.text

        session = self.db.Session()

        if message.reply_to_message is not None and message.reply_to_message.text in self.TABLES:
            type = self.TABLES[message.reply_to_message.text]
            pages = session.query(models.Page).filter((models.Page.type == type) & (((models.Page.name.ilike(query + "%")) & (models.Page.type != "class")) | (models.Page.name.ilike(query)))).limit(2)
        else:
            pages = session.query(models.Page).filter(((models.Page.name.ilike(query + "%")) & (models.Page.type != "class")) | (models.Page.name.ilike(query))).limit(2)

        pages = list(pages)

        if len(pages) == 0:
            message.reply("I criteri di ricerca inseriti non hanno portato a nessun risultato.")
            return

        if len(pages) > 1:
            message.reply("I criteri di ricerca inseriti coincidono con più di un risultato.")
            return

        utils.send_page(self.db, bot, message, pages[0], self.TABLE_MESSAGE[pages[0].type] % pages[0].name)


    def chat_unavailable(self, chat_id):
        session = self.db.Session()

        subscriber = session.query(models.Subscriber).filter(models.Subscriber.chat_id == chat.id).first()
        if subscriber:
            session.delete(subscriber)
            session.commit()
