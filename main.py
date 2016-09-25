import botogram
import config
import utils
import os

bot = botogram.create(config.TELEGRAM_TOKEN)
bot.lang = "it"
bot.owner = "@Paolo565"
bot.about = "Questo bot ti da gli orari scolastici dal sito " + utils.get_short_domain(config.SCHOOL_WEBSITE)
bot.after_help = [
    "Sai programmare? Questo bot è opensource!",
    "Clicca qui sotto per andare alla pagina github dove puoi vedere il codice e contribuire",
    "https://github.com/paolo565/TelegramSchoolBot",
]

if not os.path.isdir('./images/classes/'):
    os.makedirs('./images/classes/')

if not os.path.isdir('./images/teachers/'):
    os.makedirs('./images/teachers/')


def log_request(command, chat, message, args):
    print((str(message.sender.id) if message.sender.username is None else "@" + message.sender.username) +
          ("" if chat.title is None else " - " + chat.title) + " - /" + command + " " + ' '.join(args))


@bot.timer(3600)
def timer():
    utils.update()


@bot.command('iscriviti')
def subscribe(chat, message, args):
    """Iscriviti alle notifiche"""
    utils.add_blog_subcriber(chat.id)
    chat.send('Sei stato iscritto con successo a tutte le notifiche della scuola 😀', reply_to=message)


@bot.command('disiscriviti')
def unsubscribe(chat, message, args):
    """Iscriviti alle notifiche"""
    utils.remove_blog_subcriber(chat.id)
    chat.send('Sei stato disiscritto da tutte le notifiche 😞', reply_to=message)


@bot.command('orari')
def linkorari_command(chat, message, args):
    """Link alla pagina degli orari"""
    log_request('orari', chat, message, args)

    redirect_url = utils.get_redirect_url()
    if redirect_url is None:
        chat.send('Non conosco il link alla pagina degli orari 😢\n\nProva a cercarlo su:\n' + config.SCHOOL_WEBSITE,
                  preview=False, reply_to=message)
        return

    chat.send('Orari:\n' + redirect_url, preview=False, reply_to=message, syntax='plain')


@bot.command('classe')
def linkclasse_command(chat, message, args):
    """Mostra gli orari di una classe"""
    log_request('classe', chat, message, args)

    if len(args) == 0:
        chat.send("Fai /classe <Classe>", reply_to=message, syntax='plain')
        return

    name = ' '.join(args)
    get_class_link(chat, message, name)


@bot.command('prof')
def linkprof_command(chat, message, args):
    """Mostra gli orari di un professore"""
    log_request('prof', chat, message, args)

    if len(args) == 0:
        chat.send("Fai /prof <Nome prof scritto come sul sito>", reply_to=message,
                  syntax='plain')
        return

    name = ' '.join(args)
    get_teacher_link(chat, message, name)


def get_class_link(chat, message, name):
    response_name, response_url, response_file_id = utils.get_name_url_and_file_id('classes', name)
    if response_name is None:
        chat.send('Non ho trovato la classe: <b>' + name + '</b>', reply_to=message, syntax='HTML')
        return

    file = utils.get_image_file(response_file_id, response_url, response_name, 'classes')
    if file is None:
        chat.send('Si è verificato un errore 😢', reply_to=message, syntax='plain')
        return

    image_type, image = utils.get_image_file(response_file_id, response_url, response_name, 'classes')
    if image_type is None:
        chat.send('Si è verificato un errore 😢', reply_to=message, syntax='plain')
        return

    caption = 'Classe: {}\nPagina Orari: {}'.format(response_name, response_url)
    if image_type == 'id':
        # Temporary, because botogram doesn't support sending files by the file_id
        send_cached_photo(chat, image, message, caption)
    else:
        message = chat.send_photo(image, caption=caption, reply_to=message)
        utils.update_file_id('classes', response_name, message.photo.file_id)


def get_teacher_link(chat, message, name):
    response_name, response_url, response_file_id = utils.get_name_url_and_file_id('teachers', name)
    if response_name is None:
        chat.send('Non ho trovato il prof: <b>' + name + '</b>', reply_to=message, syntax='HTML')
        return

    image_type, image = utils.get_image_file(response_file_id, response_url, response_name, 'teachers')
    if image_type is None:
        chat.send('Si è verificato un errore 😢', reply_to=message, syntax='plain')
        return

    caption = 'Docente: {}\nPagina Orari: {}'.format(response_name, response_url)
    if image_type == 'id':
        # Temporary, because botogram doesn't support sending files by the file_id
        send_cached_photo(chat, image, message, caption)
    else:
        message = chat.send_photo(image, caption=caption, reply_to=message)
        utils.update_file_id('teachers', response_name, message.photo.file_id)


def send_cached_photo(chat, file_id, message, caption):
    # Temporary, because botogram doesn't support sending files by the file_id
    args = {
        'chat_id': chat.id,
        'reply_to_message_id': message.message_id,
        'caption': caption,
        'photo': file_id
    }
    bot.api.call("sendPhoto", args)


if __name__ == '__main__':
    utils.set_bot(bot)
    bot.run()
