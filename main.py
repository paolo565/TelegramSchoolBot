import botogram
import config
from utils import Utils
import html

bot = botogram.create(config.TELEGRAM_TOKEN)
bot_utils = Utils(bot)

bot.lang = "it"
bot.owner = "@Paolo565"
bot.about = "Questo bot ti da gli orari scolastici dal sito " + bot_utils.get_short_domain(config.SCHOOL_WEBSITE)
bot.after_help = [
    "Sai programmare? Questo bot è opensource!",
    "Clicca qui sotto per andare alla pagina github dove puoi vedere il codice e contribuire",
    "https://github.com/paolobarbolini/TelegramSchoolBot",
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
    message.reply('Ti sei iscritto con successo alle notifiche della scuola')


@bot.command('disiscriviti')
def unsubscribe_command(chat, message, args):
    """Iscriviti alle notifiche"""
    log_request('disiscriviti', chat, message, args)

    bot_utils.remove_blog_subscriber(chat.id)
    message.reply('Ti sei disiscritto con successo dalle notifiche della scuola')


@bot.command('orari')
def school_hours_link_command(chat, message, args):
    """Link alla pagina degli orari"""
    log_request('orari', chat, message, args)

    redirect_url = bot_utils.get_redirect_url()
    if redirect_url is None:
        message.reply('Non conosco il link alla pagina degli orari 😢\n\n'
                      '<a href="%s">Clicca Qui</a> per andare sul sito della scuola.' %
                      (html.escape(config.SCHOOL_WEBSITE),), preview=False)
        return

    message.reply('<a href="%s">Clicca Qui</a> per andare alla pagina degli orari\n\n'
                  '<b>Ci sono altri comandi che potrebbero interessarti:</b>\n'
                  '/classe Mostra gli orari di una classe\n'
                  '/prof Mostra gli orari di un professore' % (html.escape(redirect_url),),
                  preview=False, syntax='HTML')


@bot.command('classe')
def class_command(chat, message, args):
    """Mostra gli orari di una classe"""
    log_request('classe', chat, message, args)

    if len(args) == 0:
        message.reply("Ok, ora dimmi qual'è la classe di cui vuoi sapere l'orario", syntax='plain',
                      extra=botogram.ForceReply(data={
                          'force_reply': True,
                          'selective': True
                      }))
        return

    name = ' '.join(args)
    get_link(chat, message, name, 'classes', 'Non ho trovato la classe: <b>%s</b>' % (html.escape(name),),
             'Classe: %s\nPagina Orari: %s')


@bot.command('prof')
def prof_command(chat, message, args):
    """Mostra gli orari di un professore"""
    log_request('prof', chat, message, args)

    if len(args) == 0:
        message.reply("Ok, ora dimmi il nome del docente di cui vuoi sapere l'orario", syntax='plain',
                      extra=botogram.ForceReply(data={
                          'force_reply': True,
                          'selective': True
                      }))
        return

    name = ' '.join(args)
    get_link(chat, message, name, 'teachers', 'Non ho trovato il docente: <b>%s</b>' % (html.escape(name),),
             'Docente: %s\nPagina Orari: %s')


@bot.message_matches('[\s\S]*')
def message_received(chat, message):
    print('"%s" "%s" - "%s"' % (
        message.sender.name if message.sender.username is None else "@" + message.sender.username,
        '-' if chat.title is None else chat.title,
        message.text,
    ))

    name = message.text.replace('@' + bot.itself.username, '').lstrip().rstrip()
    if not get_link(chat, message, name, 'classes', None, 'Classe: %s\nPagina Orari: %s'):
        get_link(chat, message, name, 'teachers', 'Non ho trovato nessuna classe o docente di nome <b>%s</b>' %
                 (html.escape(name),), 'Docente: %s\nPagina Orari: %s')


def get_link(chat, message, name, table_name, not_found_message, caption):
    response_name, response_url, response_file_id = bot_utils.get_name_url_and_file_id(table_name, name)
    if response_name is None:
        if not_found_message is not None:
            message.reply(not_found_message, syntax='HTML')
        return False

    image_type, image = bot_utils.get_image_file(response_file_id, response_url, response_name, table_name)
    if image_type is None:
        message.reply('Si è verificato un errore 😢', syntax='plain')
        return True

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
        message = message.reply_with_photo(image, caption=caption)
        bot_utils.update_file_id(table_name, response_name, message.photo.file_id)
    return True


if __name__ == '__main__':
    bot.run()
