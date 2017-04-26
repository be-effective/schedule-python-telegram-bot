# -*- encoding: utf-8 -*-
import mysql.connector
import const
import texts
import datetime
import telegram ,telegram.ext
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def switch():
    keyboard = [[InlineKeyboardButton("⬅️     ", callback_data='1'),InlineKeyboardButton("     ➡️", callback_data='2')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

def first_menu():
    custom_keyboard = [['Сегодня', 'Завтра', 'Неделя', texts.alt],
                       ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, True)
    return reply_markup

def more_menu(text):
    custom_keyboard = [[texts.back,texts.birth, texts.exam, texts.duty],
                       [texts.menu_liks, texts.menu_ask, 'Донат',texts.group]]
    if if_admin(text):
        custom_keyboard[1].insert(1, texts.admin)
    return telegram.ReplyKeyboardMarkup(custom_keyboard, True)

def to_table(sql):
    cnx = mysql.connector.connect(user=const.dbuser,
                                  password=const.dbpwd,
                                  host=const.dbhost,
                                  database=const.dbname)
    cursor = cnx.cursor()
    cursor.execute(sql)
    temp = cursor.fetchall()
    cursor.close()
    cnx.close()
    return temp

def dayofweek(day):
    if (day % 7)==1:
        return 'Воскресенье'
    if (day % 7)==2:
        return 'Понедельник'
    if (day % 7)==3:
        return 'Вторник'
    if (day % 7)==4:
        return 'Среда'
    if (day % 7)==5:
        return 'Четверг'
    if (day % 7)==6:
        return 'Пятница'
    if (day % 7)==0:
        return 'Суббота'

def get_day_month():
    now_date = datetime.date.today()
    string = str(now_date.day) + "." + str(now_date.month)
    return string

def get_next_day_month(how_many_days_increment):
    now_date = datetime.date.today() + datetime.timedelta(days=how_many_days_increment)
    string = str(now_date.day) + "." + str(now_date.month)
    return string

def sometext(bot, update, text, flag):
    sql=''
    if flag == 0:
        sql = "SELECT * FROM "+get_group(bot, update)+" WHERE `data`='" + get_day_month() + "';"
    if flag>0 and flag<7:
        # Получим день недели сегодня
        step=7
        now_date = datetime.date.today()
        number_of_day = int(now_date.strftime("%j"))
        y = number_of_day % 7
        x = (flag+1) % 7
        if (x>y):
            step=x-y
        elif (x<y):
            step = 7-(y-x)
        sql = "SELECT * FROM "+get_group(bot, update)+" WHERE `data`='" + get_next_day_month(step) + "';"
    if flag == 7:
        sql = "SELECT * FROM "+get_group(bot, update)+" WHERE `data`='" + get_next_day_month(1) + "';"
    elif flag == 8 or flag == 9:
        sql = "SELECT * FROM "+get_group(bot, update)+" WHERE `data`='" + text + "';"
    cursor = to_table(sql)
    messag = ''
    if cursor:
        for row in cursor:
            id_in_db = row[0]
            data = row[1]
            first = row[2]
            second = row[3]
            third = row[4]
            fourth = row[5]
            word = row[6]
            if flag == 0:
                now_date = datetime.date.today()
                messag += 'Сегодня (до отпуска <b>'+str(213-int(now_date.strftime("%j")))+'</b>)\n' #'('+str(id_in_db)+' до отпуска)',
            if flag == 7:
                messag += 'Завтра \n'
            if flag == 8 or flag == 9:
                now_date = datetime.date.today()
                number_of_day = int(now_date.strftime("%j"))
                preload = ''
                if (id_in_db==number_of_day):
                    preload = 'Это сегодня!\n'
                if (id_in_db>number_of_day):
                    preload = 'Вперед на '+str(id_in_db-number_of_day)+' дн.\n'
                if (id_in_db<number_of_day):
                    preload = 'Прошло: '+str(number_of_day - id_in_db)+' дн.\n'
                messag += 'По вашему запросу:\n' \
                          '{}'.format(preload)
            sql = on = tw = th = fo = ''
            prof = ''
            if flag == 9:
                prof = update.callback_query.message.chat_id
                sql = "UPDATE `bakirov_db0`.`users_for_raspisanie_bot` SET `data`='" + data + "' WHERE `telegram_id`=" + str(update.callback_query.message.chat_id)
            else:
                prof = update.message.chat_id
                sql = "UPDATE `bakirov_db0`.`users_for_raspisanie_bot` SET `data`='" + data + "' WHERE `telegram_id`=" + str(update.message.chat_id)
            cnx = mysql.connector.connect(user=const.dbuser,
                                          password=const.dbpwd,
                                          host=const.dbhost,
                                          database=const.dbname)
            cursor = cnx.cursor()
            cursor.execute(sql)
            cnx.commit()
            cursor.close()
            cnx.close()
            if if_admin(str(prof)):
                on = ' /1 or /1_add'
                tw = ' /2 or /2_add'
                th = ' /3 or /3_add'
                fo = ' /4 or /4_add'
            messag+='<b>{}</b>\n' \
                    '{}.2017   {}-й / 365\n' \
                    '<i>1) </i> {}{}\n' \
                    '<i>2) </i> {}{}\n' \
                    '<i>3) </i> {}{}\n' \
                    '<i>4) </i> {}{}\n'.format(dayofweek(id_in_db),data,id_in_db,first,on,second,tw,third,th,fourth,fo)
            if word:
                messag += '<b>А также:</b> \n' + word
            if if_admin(str(prof)):
                messag+=' '+'/word or /word_add'
            if flag == 9:
                messag = '<b>' + get_group(bot, update, 1) + '</b>\n' + messag
                return messag
    messag = '<b>'+get_group(bot, update, 1)+'</b>\n'+messag
    bot.sendMessage(chat_id=update.message.chat_id,text = messag, parse_mode = telegram.ParseMode.HTML, reply_markup=switch())

def week(bot,update):
    now_date = datetime.date.today()
    number_of_day = int(now_date.strftime("%j"))
    sql = "SELECT * FROM "+get_group(bot, update)+" WHERE `id` >= "+str(number_of_day)+" AND `id` < "+str(number_of_day+7)+";"
    cursor = to_table(sql)
    if cursor:
        sche = ''
        for row in cursor:
            id_in_db = row[0]
            if (id_in_db%7!=1):
                data = row[1]
                first = row[2]
                second = row[3]
                third = row[4]
                fourth = row[5]
                word = row[6]
                sche += '<b>'+data+' - '+dayofweek(id_in_db)+'</b>\n'
                sche += '<i>1)</i> '+first+'\n'
                sche += '<i>2)</i> '+second+'\n'
                sche += '<i>3)</i> '+third+'\n'
                sche += '<i>4)</i> '+fourth+'\n'
                if word:
                    sche += '<b>А также:</b> \n' + word + '\n'
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=sche,
                        parse_mode=telegram.ParseMode.HTML,reply_markup=first_menu())

def more(bot, update):
    reply_markup = more_menu(str(update.message.chat_id))
    bot.sendMessage(chat_id=update.message.chat_id,text=texts.ty, reply_markup=reply_markup) # text=texts.ty,

def proof_of_exist(bot, update):
    cursor = to_table("SELECT `status` FROM `users_for_raspisanie_bot` WHERE `telegram_id`={}".format(str(update.message.chat_id)))
    if cursor:
        for row in cursor:
            status = int(row[0])
            if status:
                return 1
            else:
                return 0
    else:
        sql = "INSERT INTO `bakirov_db0`.`users_for_raspisanie_bot` " \
              "(`id`, `telegram_id`, `name`, `last`, `status`) VALUES " \
              "(NULL, '" + str(update.message.chat_id) + "', '" + \
              str(update.message.from_user.first_name) + "', '" + \
              str(update.message.from_user.last_name) + "', 0);"
        cnx = mysql.connector.connect(user=const.dbuser,
                                      password=const.dbpwd,
                                      host=const.dbhost,
                                      database=const.dbname)
        #запрос на подтверждение

        cr = cnx.cursor()
        cr.execute(sql)
        cnx.commit()
        cr.close()
        cnx.close()
        return 0

def groups():
    custom_keyboard = [['641/1', '641/2']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, True)
    return reply_markup

def change_group(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=texts.change, reply_markup=groups())

def update_group(bot, update, group):
    sql = ''
    if group ==1:
        sql = "UPDATE `bakirov_db0`.`users_for_raspisanie_bot` SET `group`=" + "2" + " WHERE `telegram_id`=" + str(update.message.chat_id)
        bot.sendMessage(chat_id=update.message.chat_id, text='Выбрана группа: 641/1', reply_markup = first_menu())
    elif group == 2:
        sql = "UPDATE `bakirov_db0`.`users_for_raspisanie_bot` SET `group`=" + "1" + " WHERE `telegram_id`=" + str(update.message.chat_id)
        bot.sendMessage(chat_id=update.message.chat_id, text='Выбрана группа: 641/2', reply_markup = first_menu())
    elif group == 9:
        if group == 1:
            sql = "UPDATE `bakirov_db0`.`users_for_raspisanie_bot` SET `group`=" + "2" + " WHERE `telegram_id`=" + str(
                update.callback_query.message.chat_id)
            bot.sendMessage(chat_id=update.callback_query.message.chat_id, text='Выбрана группа: 641/1',
                            reply_markup=first_menu())
        elif group == 2:
            sql = "UPDATE `bakirov_db0`.`users_for_raspisanie_bot` SET `group`=" + "1" + " WHERE `telegram_id`=" + str(
                update.callback_query.message.chat_id)
            bot.sendMessage(chat_id=update.callback_query.message.chat_id, text='Выбрана группа: 641/2',
                            reply_markup=first_menu())

    cnx = mysql.connector.connect(user=const.dbuser,
                                  password=const.dbpwd,
                                  host=const.dbhost,
                                  database=const.dbname)
    cursor = cnx.cursor()
    cursor.execute(sql)
    cnx.commit()
    cursor.close()
    cnx.close()

def get_group(bot, update, flag=0):
    cursor = ''
    try:
        cursor = to_table("SELECT `group` FROM `users_for_raspisanie_bot` WHERE `telegram_id`={}".format(str(update.message.chat_id)))
    except AttributeError:
        cursor = to_table("SELECT `group` FROM `users_for_raspisanie_bot` WHERE `telegram_id`={}".format(str(update.callback_query.message.chat_id)))
    group = 0
    if flag == 0:
        if cursor:
            for row in cursor:
                group = row[0]
                if group == 1:
                    group = '`sche`'
                elif group == 2:
                    group = '`sche2`'
        return group
    elif flag == 1:
        if cursor:
            for row in cursor:
                group = row[0]
                if group == 1:
                    group = '641/2'
                elif group == 2:
                    group = '641/1'
        return group

def donate(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text = texts.donate, reply_markup=more_menu(str(update.message.chat_id)))

def link(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=texts.link, reply_markup=more_menu(str(update.message.chat_id)))

def contact(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=texts.contact, reply_markup=more_menu(str(update.message.chat_id)))


def duty(bot, update):
    sql = "SELECT `data`, `adword` FROM "+get_group(bot, update)+" WHERE `adword` <> '';"
    cursor = to_table(sql)
    if cursor:
        births = '<b>Список нарядов:</b>\n'
        for row in cursor:
            if (row[1].find('на ') != -1):
                births += "<b>" + row[0] + "</b> " + "<i>" + row[1] + "</i>\n"
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=births,
                        parse_mode=telegram.ParseMode.HTML)

def birth(bot, update):
    sql = "SELECT `data`, `adword` FROM "+get_group(bot, update)+" WHERE `adword` <> '';"
    cursor = to_table(sql)
    if cursor:
        births = '<b>Дни рождения! Поздравляем!</b>\n'
        for row in cursor:
            if row[1].find('др') != -1:
                births += "<b>" + row[0] + "</b> " + "<i>" + row[1] + "</i>\n"
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=births,
                        parse_mode=telegram.ParseMode.HTML)


def exam(bot, update):
    sql = "SELECT `data`, `adword` FROM "+get_group(bot, update)+" WHERE `adword` <> '';"
    cursor = to_table(sql)
    if cursor:
        births = '<b>Зачеты, экзамены, курсовые:</b>\n'
        for row in cursor:
            if (row[1].find('экз ') != -1) or (row[1].find('зач ') != -1) or (row[1].find('кур ') != -1):
                births += "<b>" + row[0] + "</b> " + "<i>" + row[1] + "</i>\n"
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=births,
                        parse_mode=telegram.ParseMode.HTML)

#Приколюхи для админа
def admin_help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=texts.admin_help, reply_markup=more_menu(str(update.message.chat_id)))
    father(update)

def accsess_denied(bot, update):
    custom_keyboard = [['Контакты','Ссылки','Донат']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, True)
    bot.sendMessage(chat_id=update.message.chat_id, text=texts.disable, reply_markup=reply_markup)

def if_admin(from_user_telegram_id):
    if from_user_telegram_id in const.idadmin:
        return True
    else:
        return False

def get_users_list(bot, update):
    sql="SELECT `id`, `telegram_id`, `name`, `last` FROM `users_for_raspisanie_bot` WHERE `status`=0"
    cursor = to_table(sql)
    text = 'Id)   Telegram id    Name    Last\n'
    if cursor:
        text+='============================\n' \
              'Блок: (use "/add id")\n' \
              '============================\n'
        for row in cursor:
            text+= str(row[0]) + ')   ' + str(row[1]) + '    ' + str(row[2]) + '    ' + str(row[3]) + '\n'
    sql="SELECT `id`, `telegram_id`, `name`, `last` FROM `users_for_raspisanie_bot` WHERE `status`=1"
    cursor = to_table(sql)
    if cursor:
        text+='============================\n' \
              'Одобренные: (use "/del id")\n' \
              '============================\n'
        for row in cursor:
            text+= str(row[0]) + ')   ' + str(row[1]) + '    ' + str(row[2]) + '    ' + str(row[3]) + '\n'
    bot.sendMessage(chat_id=update.message.chat_id, text=text, reply_markup=first_menu())
    father(update)

def to_all(bot, update):
    tospl = update.message.text
    tospl = tospl.split(" ",-1)
    if len(tospl)>=1:
        tospl.remove('/all')
        cursor = to_table("SELECT `telegram_id` FROM `users_for_raspisanie_bot` WHERE `status`=1")
        if cursor:
            text = ''
            for item in tospl:
                text+=item+" "
            for row in cursor:
                ids=int(row[0])
                bot.sendMessage(chat_id=ids,text=text)


def add_user(bot, update):
    father(update)
    if if_admin(str(update.message.chat_id)):
        adder = update.message.text
        adder = adder.split(" ",-1)
        if len(adder) >= 2:
            sql = "UPDATE `bakirov_db0`.`users_for_raspisanie_bot` SET `status`= 1 WHERE `id`='" + adder[1]+"'"
            cnx = mysql.connector.connect(user=const.dbuser,
                                          password=const.dbpwd,
                                          host=const.dbhost,
                                          database=const.dbname)
            cursor = cnx.cursor()
            cursor.execute(sql)
            cnx.commit()
            cursor.close()
            cnx.close()
            cur=to_table("SELECT `telegram_id` FROM `bakirov_db0`.`users_for_raspisanie_bot` WHERE `id`='"+adder[1]+"'")
            row = ''
            if cur:
                for ind in cur:
                    row = ind[0]
            if str(row).isdecimal():
                bot.sendMessage(chat_id=int(row), text='Ваша заявка была одобрена!', reply_markup=first_menu())


def del_user(bot, update):
    father(update)
    if if_admin(str(update.message.chat_id)):
        adder = update.message.text
        adder = adder.split(" ",-1)
        if len(adder) >= 2:
            sql = "UPDATE `bakirov_db0`.`users_for_raspisanie_bot` SET `status`=0 WHERE `id`='" +str(adder[1])+"'"
            cnx = mysql.connector.connect(user=const.dbuser,
                                          password=const.dbpwd,
                                          host=const.dbhost,
                                          database=const.dbname)
            cursor = cnx.cursor()
            cursor.execute(sql)
            cnx.commit()
            cursor.close()
            cnx.close()

def editor(bot,update):
    if if_admin(str(update.message.chat_id)):
        sche = update.message.text
        sche = sche.split(" ", -1)
        command = update.message.text
        commander = command
        commander = commander.split(' ', 1)[0]
        commands = ['/1','/2','/3','/4','/1_add','/2_add','/3_add','/4_add','/word','/word_add']
        commands_add = ['/1_add','/2_add','/3_add','/4_add','/word_add']
        if  commander in commands:
            if len(sche)>=2 and sche[0]==commander:
                sche.remove(commander)
                ready_sche = ''
                cur = to_table(
                    "SELECT `data` FROM `bakirov_db0`.`users_for_raspisanie_bot` WHERE `telegram_id`='" + str(update.message.chat_id) + "'")
                row = ''
                if cur:
                    for ind in cur:
                        row = ind[0]
                for item in sche:
                    ready_sche += item + " "
                pre_sche = ''
                para=""
                if commander == "/1" or commander == "/1_add":
                    para = "first"
                if commander == "/2" or commander == "/2_add":
                    para = "second"
                if commander == "/3" or commander == "/3_add":
                    para = "third"
                if commander == "/4" or commander == "/4_add":
                    para = "fourth"
                if commander == "/word" or commander == "/word_add":
                    para = "adword"
                if commander in commands_add:
                    cur = to_table("SELECT `"+para+"` FROM `bakirov_db0`."+get_group(bot, update)+" WHERE `data`='" + row + "'")
                    if cur:
                        for ind in cur:
                            pre_sche = ind[0]
                        pre_sche+=" "
                sql = "UPDATE `bakirov_db0`."+get_group(bot, update)+" SET `"+para+"`='"+pre_sche+ready_sche+"' WHERE `data`='"+row+"'"
                cnx = mysql.connector.connect(user=const.dbuser,
                                              password=const.dbpwd,
                                              host=const.dbhost,
                                              database=const.dbname)
                cursor = cnx.cursor()
                cursor.execute(sql)
                cnx.commit()
                cursor.close()
                cnx.close()
                sometext(bot, update, row, 8)
                father(update, row)
            else:
                bot.sendMessage(chat_id=update.message.chat_id, text=texts.use)
    else:
        accsess_denied(bot,update)

def father(update,txt=''):
    f = open('manager.txt', 'a')
    f.write(str(time.strftime('%Y-%m-%d %H:%M:%S'))+' '+update.message.from_user.first_name+' '+update.message.from_user.last_name+' '+str(update.message.chat_id)+' '+update.message.text+' '+txt+'\n')
    f.close()

def eye(update):
    5
    # f = open('users.txt', 'a')
    # try:
    #     f.write(str(time.strftime('%Y-%m-%d %H:%M:%S'))+u' '+update.message.from_user.first_name+u' '+update.message.from_user.last_name+' '+str(update.message.chat_id)+' '+update.message.text+'\n')
    # except AttributeError or UnicodeEncodeError:
    #     update = update.callback_query
    #     y = str(time.strftime('%Y-%m-%d %H:%M:%S'))+' '+update.message.from_user.first_name+' '+update.message.from_user.last_name+' '+str(update.message.chat_id)+' '+update.message.text+'\n'
    #     f.write(y.encode('utf8'))
    # f.close()