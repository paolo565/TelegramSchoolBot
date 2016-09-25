import botogram
import config
from utils import Utils

bot = botogram.create(config.TELEGRAM_TOKEN)
bot_utils = Utils(bot)

bot.lang = "it"
bot.owner = "@Paolo565"
bot.about = "Questo bot ti da gli orari scolastici dal sito " + bot_utils.get_short_domain(config.SCHOOL_WEBSITE)
bot.after_help = [
    "Sai programmare? Questo bot è opensource!",
    "Clicca qui sotto per andare alla pagina github dove puoi vedere il codice e contribuire",
    "https://github.com/paolo565/TelegramSchoolBot",
]


def log_request(command, chat, message, args):
    print('"%s" "%s" - "/%s %s"' % (
        message.sender.name if message.sender.username is None else "@" + message.sender.username,
        '-' if chat.title is None else chat.title,
        command,
        ' '.join(args)
    ))


@bot.timer(3600)
def hourly_timer():
    bot_utils.update()


@bot.chat_unavailable
def chat_unavailable(chat_id):
    bot_utils.remove_blog_subscriber(chat_id)


@bot.command('iscriviti')
def subscribe_command(chat, message, args):
    """Iscriviti alle notifiche"""
    log_request('iscriviti', chat, message, args)

    bot_utils.add_blog_subscriber(chat.id)
    chat.send('Ti sei iscritto con successo alle notifiche della scuola', reply_to=message)


@bot.command('disiscriviti')
def unsubscribe_command(chat, message, args):
    """Iscriviti alle notifiche"""
    log_request('disiscriviti', chat, message, args)

    bot_utils.remove_blog_subscriber(chat.id)
    chat.send('Ti sei disiscritto con successo dalle notifiche della scuola', reply_to=message)


@bot.command('orari')
def school_hours_link_command(chat, message, args):
    """Link alla pagina degli orari"""
    log_request('orari', chat, message, args)

    redirect_url = bot_utils.get_redirect_url()
    if redirect_url is None:
        chat.send('Non conosco il link alla pagina degli orari 😢\n\nProva a cercarlo su:\n' + config.SCHOOL_WEBSITE,
                  preview=False, reply_to=message)
        return

    chat.send('Orari:\n' + redirect_url, preview=False, reply_to=message, syntax='plain')


@bot.command('classe')
def class_command(chat, message, args):
    """Mostra gli orari di una classe"""
    log_request('classe', chat, message, args)

    if len(args) == 0:
        chat.send("Fai /classe <Classe>", reply_to=message, syntax='plain')
        return

    name = ' '.join(args)
    get_class_link(chat, message, name)


@bot.command('prof')
def prof_command(chat, message, args):
    """Mostra gli orari di un professore"""
    log_request('prof', chat, message, args)

    if len(args) == 0:
        chat.send("Fai /prof <Nome prof scritto come sul sito>", reply_to=message, syntax='plain')
        return

    name = ' '.join(args)
    get_teacher_link(chat, message, name)


def get_class_link(chat, message, name):
    get_link(chat, message, name, 'classes', 'Non ho trovato la classe: <b>%s</b>' % (name,),
             'Classe: %s\nPagina Orari: %s')


def get_teacher_link(chat, message, name):
    get_link(chat, message, name, 'teachers', 'Non ho trovato il docente: <b>%s</b>' % (name,),
             'Docente: %s\nPagina Orari: %s')


def get_link(chat, message, name, table_name, not_found_message, caption):
    response_name, response_url, response_file_id = bot_utils.get_name_url_and_file_id(table_name, name)
    if response_name is None:
        chat.send(not_found_message, reply_to=message, syntax='HTML')
        return

    image_type, image = bot_utils.get_image_file(response_file_id, response_url, response_name, table_name)
    if image_type is None:
        chat.send('Si è verificato un errore 😢', reply_to=message, syntax='plain')
        return

    caption = caption % (response_name, response_url)
    if image_type == 'id':
        # Temporary, because botogram doesn't support sending files by the file_id
        args = {
            'chat_id': chat.id,
            'reply_to_message_id': message.message_id,
            'caption': caption,
            'photo': image
        }
        bot.api.call("sendPhoto", args)
    else:
        message = chat.send_photo(image, caption=caption, reply_to=message)
        bot_utils.update_file_id(table_name, response_name, message.photo.file_id)


if __name__ == '__main__':
    bot.run()
