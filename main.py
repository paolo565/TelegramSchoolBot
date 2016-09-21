import botogram
import config
import utils
import os

bot = botogram.create(config.TELEGRAM_TOKEN)
bot.lang = "it"
bot.owner = "@Paolo565"
bot.about = "Questo bot ti da gli orari scolastici dal sito " + utils.get_short_url(config.SCHOOL_WEBSITE)
bot.after_help = [
    "Sai programmare? Questo bot è opensource!",
    "Clicca qui sotto per andare alla pagina github dove puoi vedere il codice e contribuire",
    "https://github.com/paolo565/TelegramSchoolBot",
]


if not os.path.isdir('./images/classes/'):
    os.makedirs('./images/classes/')

if not os.path.isdir('./images/teachers/'):
    os.makedirs('./images/teachers/')


def log_request(command, chat, args):
    print((str(chat.id) if chat.username is None else "@" + chat.username) + " - /" + command + " " + ' '.join(args))


@bot.command('orari')
def linkorari_command(chat, args):
    """Link alla pagina degli orari"""
    log_request('orari', chat, args)

    redirect_url = utils.get_redirect_url()
    if redirect_url is None:
        chat.send('Non conosco il link alla pagina degli orari :(\n\nProva a cercarlo tu su:\n' + config.SCHOOL_WEBSITE,
                  preview=False)
        return

    chat.send('Gli orari sono:\n' + redirect_url, preview=False)


@bot.command('classe')
def linkclasse_command(chat, args):
    """Mostra gli orari di una classe"""
    log_request('classe', chat, args)

    if len(args) == 0:
        chat.send("Fai /classe <Classe>")
        return

    name = ' '.join(args)
    get_class_link(chat, name)


@bot.command('prof')
def linkclasse_command(chat, args):
    """Mostra gli orari di un professore"""
    log_request('prof', chat, args)

    if len(args) == 0:
        chat.send("Fai /prof <Nome prof scritto nello stesso modo in cui è scritto sul sito>")
        return

    name = ' '.join(args)
    get_teacher_link(chat, name)


def get_class_link(chat, name):
    response_name, response_url = utils.get_class_name_and_url(name)
    if response_name is None:
        chat.send('Non ho trovato la classe: ' + name, preview=False)
        return

    file = './images/classes/' + utils.md5(response_name) + '.png'
    utils.link_to_image(response_url, file)
    chat.send_photo(file, caption='Gli orari della classe {} sono: {}'.format(response_name, response_url))


def get_teacher_link(chat, name):
    response_name, response_url = utils.get_teacher_name_and_url(name)
    if response_name is None:
        chat.send('Non ho trovato il prof: ' + name, preview=False)
        return

    file = './images/teachers/' + utils.md5(response_name) + '.png'
    utils.link_to_image(response_url, file)
    chat.send_photo(file, caption='Gli orari del prof {} sono: {}'.format(response_name, response_url))

if __name__ == '__main__':
    utils.update()
    bot.run()
