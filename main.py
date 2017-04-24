# -*- encoding: utf-8 -*-
import const
import func
import texts
import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

updater=Updater(token=const.token)
dispatcher=updater.dispatcher

def editor(bot, update):
    func.editor(bot, update)

def settings(bot, update):
    3

def info(bot, update):
    3

def add_user(bot, update):
    func.add_user(bot, update)

def del_user(bot, update):
    func.del_user(bot, update)

def to_aller(bot, update):
    if func.if_admin(str(update.message.chat_id)):
        func.to_all(bot, update)

def users(bot, update):
    if func.if_admin(str(update.message.chat_id)):
        func.get_users_list(bot, update)

def start(bot, update):
    func.proof_of_exist(bot, update)
    bot.sendMessage(chat_id=update.message.chat_id, text = texts.hellos, reply_markup = func.first_menu())

def hello(bot, update):
    update.message.reply_text('Hello {}'.format(update.message.from_user.first_name))

def text(bot, update):
    func.eye(update)
    text=update.message.text
    if func.proof_of_exist(bot, update): # Если пользователь найден и активен
        if text == 'Сегодня':
            func.sometext(bot, update, '', 0)
        elif text == 'Завтра':
            func.sometext(bot, update, '', 7)
        elif text == 'Пн':
            func.sometext(bot, update, '', 1)
        elif text == 'Вт':
            func.sometext(bot, update, '', 2)
        elif text == 'Ср':
            func.sometext(bot, update, '', 3)
        elif text == 'Чт':
            func.sometext(bot, update, '', 4)
        elif text == 'Пт':
            func.sometext(bot, update, '', 5)
        elif text == 'Сб':
            func.sometext(bot, update, '', 6)
        elif text == 'Неделя':
            func.week(bot, update)
        elif text == texts.alt:
            func.more(bot, update)
        elif text == texts.admin:
            func.admin_help(bot, update)
        elif text == texts.back:
            bot.sendMessage(chat_id=update.message.chat_id, text=texts.hellos, reply_markup=func.first_menu())
        elif text == texts.group:
            func.change_group(bot, update)
        elif text == 'Ссылки':
            func.link(bot, update)
        elif text == 'Контакты':
            func.contact(bot, update)
        elif text == 'Донат':
            func.donate(bot, update)
        elif text == texts.birth:
            func.birth(bot, update)
        elif text == texts.exam:
            func.exam(bot, update)
        else:#тут проверка
            func.sometext(bot, update, text, 8)
    else:  # Если пользователь не найден или не активен
        if text == 'Cсылки':
            func.link(bot, update)
        elif text == 'Контакты':
            func.contact(bot, update)
        elif text == 'Донат':
            func.donate(bot, update)
        else:
            func.accsess_denied(bot, update)
        bot.sendMessage(chat_id=update.message.chat_id, text='Ваш Telegram Id: '+str(update.message.chat_id)+ '. Отправьте это сообщение администратору.')

# Обработка админ команд
dispatcher.add_handler(CommandHandler('all', to_aller))
dispatcher.add_handler(CommandHandler('users', users))
dispatcher.add_handler(CommandHandler('add', add_user))
dispatcher.add_handler(CommandHandler('del', del_user))

# Обработка общих команд
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('settings', settings))
dispatcher.add_handler(CommandHandler('help', info))

# Обработка текстовых сообщений
dispatcher.add_handler(MessageHandler(Filters.text, text))

# Обработка специальных комманд
dispatcher.add_handler(MessageHandler(Filters.command, editor))

updater.start_webhook(listen = '88.214.236.179',
                      port = 8443,
                      url_path = const.token,
                      key = 'private.key',
                      cert = 'cert.pem',
                      webhook_url = "https://88.214.236.179:8443/"+const.token)
updater.idle()

# updater.start_polling()
# updater.idle()

#print(time.strftime('%Y-%m-%d %H:%M:%S'))
