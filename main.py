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
def linkclasse_command(chat, message, args):
    """Mostra gli orari di un professore"""
    log_request('prof', chat, message, args)

    if len(args) == 0:
        chat.send("Fai /prof <Nome prof scritto come sul sito>", reply_to=message,
                  syntax='plain')
        return

    name = ' '.join(args)
    get_teacher_link(chat, message, name)


def get_class_link(chat, message, name):
    response_name, response_url = utils.get_class_name_and_url(name)
    if response_name is None:
        chat.send('Non ho trovato la classe: <b>' + name + '</b>', reply_to=message, syntax='HTML')
        return

    file = './images/classes/' + utils.md5(response_name) + '.png'
    utils.link_to_image(response_url, file)
    chat.send_photo(file, caption='Classe: {}\nPagina Orari: {}'.format(response_name, response_url),
                    reply_to=message)


def get_teacher_link(chat, message, name):
    response_name, response_url = utils.get_teacher_name_and_url(name)
    if response_name is None:
        chat.send('Non ho trovato il prof: <b>' + name + '</b>', reply_to=message, syntax='HTML')
        return

    file = './images/teachers/' + utils.md5(response_name) + '.png'
    utils.link_to_image(response_url, file)
    chat.send_photo(file, caption='Docente: {}\nPagina Orari: {}'.format(response_name, response_url),
                    reply_to=message)


if __name__ == '__main__':
    utils.update()
    bot.run()
