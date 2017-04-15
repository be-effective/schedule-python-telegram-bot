# -*- encoding: utf-8 -*-
import const
import func
import texts
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

from telegram.ext import Updater,MessageHandler, Filters, CommandHandler

updater = Updater(token=const.token)
dispatcher = updater.dispatcher

def add_user(bot, update):
    func.add_user(bot, update)

def del_user(bot, update):
    func.del_user(bot, update)

def one(bot, update):
    func.for_1(bot, update)
def two(bot, update):
    func.for_2(bot, update)
def three(bot, update):
    func.for_3(bot, update)
def four(bot, update):
    func.for_4(bot, update)

def one_append(bot, update):
    func.for_1_append(bot, update)
def two_append(bot, update):
    func.for_2_append(bot, update)
def three_append(bot, update):
    func.for_3_append(bot, update)
def four_append(bot, update):
    func.for_4_append(bot, update)

def to_all(bot, update):
    if func.if_admin(str(update.message.chat_id)):
        func.to_all(bot, update)

def users(bot, update):
    if func.if_admin(str(update.message.chat_id)):
        func.get_users_list(bot, update)

def start(bot, update):
    func.proof_of_exist(bot, update)
    #print(update.message.chat_id) #debug
    bot.sendMessage(chat_id=update.message.chat_id, text = texts.hellos, reply_markup = func.first_menu())

def hello(bot, update):
    update.message.reply_text('Hello {}'.format(update.message.from_user.first_name))

def text(bot, update):
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
        elif text == 'Доп':
            func.more(bot, update)
        elif text == 'Админ':
            func.admin_help(bot, update)
        elif text == 'Назад':
            bot.sendMessage(chat_id=update.message.chat_id, text=texts.hellos, reply_markup=func.first_menu())
        elif text == 'Сменить':
            func.change_group(bot, update)
        elif text == 'Ссылки':
            func.link(bot, update)
        elif text == 'Контакты':
            func.contact(bot, update)
        elif text == 'Донат':
            func.donate(bot, update)
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
dispatcher.add_handler(CommandHandler('1', one))
dispatcher.add_handler(CommandHandler('2', two))
dispatcher.add_handler(CommandHandler('3', three))
dispatcher.add_handler(CommandHandler('4', four))
dispatcher.add_handler(CommandHandler('1_add', one_append))
dispatcher.add_handler(CommandHandler('2_add', two_append))
dispatcher.add_handler(CommandHandler('3_add', three_append))
dispatcher.add_handler(CommandHandler('4_add', four_append))
dispatcher.add_handler(CommandHandler('users', users))
dispatcher.add_handler(CommandHandler('add', add_user))
dispatcher.add_handler(CommandHandler('del', del_user))
dispatcher.add_handler(CommandHandler('all', to_all))

# Обработка общих команд
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('setting', hello))
dispatcher.add_handler(CommandHandler('help', hello))

# Обработка текстовых сообщений
echo_handler = MessageHandler(Filters.text, text)
dispatcher.add_handler(echo_handler)

updater.start_polling()
updater.idle()

#print(time.strftime('%Y-%m-%d %H:%M:%S'))