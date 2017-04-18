# -*- encoding: utf-8 -*-
import mysql.connector
import const
import texts
import datetime
import telegram
import time

def first_menu():
    custom_keyboard = [['Сегодня', 'Завтра', 'Неделя', 'Доп'],
                       ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, True)
    return reply_markup

def more_menu(text):
    custom_keyboard = [['Назад', 'Сменить'],
                       ['Ссылки', 'Контакты', 'Донат']]
    if if_admin(text):
        custom_keyboard[0].insert(1,'Админ')
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
        sql = "SELECT * FROM `sche` WHERE `data`='" + get_day_month() + "';"
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
        sql = "SELECT * FROM `sche` WHERE `data`='" + get_next_day_month(step) + "';"
    if flag == 7:
        sql = "SELECT * FROM `sche` WHERE `data`='" + get_next_day_month(1) + "';"
    if flag == 8:
        sql = "SELECT * FROM `sche` WHERE `data`='" + text + "';"
    cursor = to_table(sql)
    if cursor:
        messag = ''
        for row in cursor:
            id_in_db = row[0]
            data = row[1]
            first = row[2]
            second = row[3]
            third = row[4]
            fourth = row[5]
            if flag==0:
                now_date = datetime.date.today()
                messag += 'Сегодня (до отпуска <b>'+str(213-int(now_date.strftime("%j")))+'</b>)\n' #'('+str(id_in_db)+' до отпуска)',
            if flag == 7:
                messag += 'Завтра \n'
            if flag == 8:
                now_date = datetime.date.today()
                number_of_day = int(now_date.strftime("%j"))
                preload = ''
                if (id_in_db==number_of_day):
                    preload = 'Это сегодня!\n'
                if (id_in_db>number_of_day):
                    preload = 'Вперед на '+str(id_in_db-number_of_day)+' дн.\n'
                if (id_in_db<number_of_day):
                    preload = 'Прошло: ' + str(number_of_day - id_in_db)+' дн.\n'
                messag += 'По вашему запросу:\n' \
                          '{}'.format(preload)
            on = tw = th = fo = ''
            if if_admin(str(update.message.chat_id)):
                sql = "UPDATE `bakirov_db0`.`users_for_raspisanie_bot` SET `data`='"+data+"' WHERE `telegram_id`="+str(update.message.chat_id)
                cnx = mysql.connector.connect(user=const.dbuser,
                                              password=const.dbpwd,
                                              host=const.dbhost,
                                              database=const.dbname)
                cursor = cnx.cursor()
                cursor.execute(sql)
                cnx.commit()
                cursor.close()
                cnx.close()
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
        bot.sendMessage(chat_id=update.message.chat_id,text = messag, parse_mode = telegram.ParseMode.HTML)

def week(bot,update):
    now_date = datetime.date.today()
    number_of_day = int(now_date.strftime("%j"))
    sql = "SELECT * FROM `sche` WHERE `id` >= "+str(number_of_day)+" AND `id` < "+str(number_of_day+7)+";"
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
                sche += '<b>'+data+' - '+dayofweek(id_in_db)+'</b>\n'
                sche += '<i>1)</i> '+first+'\n'
                sche += '<i>2)</i> '+second+'\n'
                sche += '<i>3)</i> '+third+'\n'
                sche += '<i>4)</i> '+fourth+'\n'
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=sche,
                        parse_mode=telegram.ParseMode.HTML)

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

def change_group(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=texts.change)

def donate(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text = texts.donate)

def link(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=texts.link)

def contact(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=texts.contact)

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
    text = 'Id)   Telegram id    :    Name:   :   Last name:\n'
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
    father(update)
    if len(tospl)>=1:
        tospl.remove('/all')
        cursor = to_table("SELECT `telegram_id` FROM `users_for_raspisanie_bot` WHERE `status`=1")
        if cursor:
            text = ''
            for item in tospl:
                text+=item+" "
            for row in cursor:
                bot.sendMessage(chat_id=str(row[0]), text=text)

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


def for_1(bot,update):
    if if_admin(str(update.message.chat_id)):
        sche = update.message.text
        sche = sche.split(" ", -1)
        if len(sche)>=2 and sche[0]=='/1':
            sche.remove("/1")
            ready_sche = ''
            cur = to_table(
                "SELECT `data` FROM `bakirov_db0`.`users_for_raspisanie_bot` WHERE `telegram_id`='" + str(update.message.chat_id) + "'")
            row = ''
            if cur:
                for ind in cur:
                    row = ind[0]
            for item in sche:
                ready_sche += item + " "
            sql = "UPDATE `bakirov_db0`.`sche` SET `first`='"+ready_sche+"' WHERE `data`='"+row+"'"
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
            bot.sendMessage(chat_id=update.message.chat_id, text=texts.use1)
    else:
        accsess_denied(bot,update)

def for_2(bot,update):
    if if_admin(str(update.message.chat_id)):
        sche = update.message.text
        sche = sche.split(" ", -1)
        if len(sche)>=2 and sche[0]=='/2':
            sche.remove("/2")
            ready_sche = ''
            cur = to_table(
                "SELECT `data` FROM `bakirov_db0`.`users_for_raspisanie_bot` WHERE `telegram_id`='" + str(update.message.chat_id) + "'")
            row = ''
            if cur:
                for ind in cur:
                    row = ind[0]
            for item in sche:
                ready_sche += item + " "
            sql = "UPDATE `bakirov_db0`.`sche` SET `second`='"+ready_sche+"' WHERE `data`='"+row+"'"
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
            bot.sendMessage(chat_id=update.message.chat_id, text=texts.use2)
    else:
        accsess_denied(bot,update)

def for_3(bot,update):
    if if_admin(str(update.message.chat_id)):
        sche = update.message.text
        sche = sche.split(" ", -1)
        if len(sche)>=2 and sche[0]=='/3':
            sche.remove("/3")
            ready_sche = ''
            cur = to_table(
                "SELECT `data` FROM `bakirov_db0`.`users_for_raspisanie_bot` WHERE `telegram_id`='" + str(update.message.chat_id) + "'")
            row = ''
            if cur:
                for ind in cur:
                    row = ind[0]
            for item in sche:
                ready_sche += item + " "
            sql = "UPDATE `bakirov_db0`.`sche` SET `third`='"+ready_sche+"' WHERE `data`='"+row+"'"
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
            bot.sendMessage(chat_id=update.message.chat_id, text=texts.use3)
    else:
        accsess_denied(bot,update)

def for_4(bot,update):
    if if_admin(str(update.message.chat_id)):
        sche = update.message.text
        sche = sche.split(" ", -1)
        if len(sche)>=2 and sche[0]=='/4':
            sche.remove("/4")
            ready_sche = ''
            cur = to_table(
                "SELECT `data` FROM `bakirov_db0`.`users_for_raspisanie_bot` WHERE `telegram_id`='" + str(update.message.chat_id) + "'")
            row = ''
            if cur:
                for ind in cur:
                    row = ind[0]
            for item in sche:
                ready_sche += item + " "
            sql = "UPDATE `bakirov_db0`.`sche` SET `fourth`='"+ready_sche+"' WHERE `data`='"+row+"'"
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
            bot.sendMessage(chat_id=update.message.chat_id, text=texts.use4)
    else:
        accsess_denied(bot,update)

def for_1_append(bot,update):
    if if_admin(str(update.message.chat_id)):
        sche = update.message.text
        sche = sche.split(" ", -1)
        if len(sche)>=2 and sche[0]=='/1_add':
            sche.remove("/1_add")
            ready_sche = ''
            cur = to_table("SELECT `data` FROM `bakirov_db0`.`users_for_raspisanie_bot` WHERE `telegram_id`='" +
                           str(update.message.chat_id) + "'")
            row = ''
            if cur:
                for ind in cur:
                    row = ind[0]
            pre_sche = ''
            cur = to_table("SELECT `first` FROM `bakirov_db0`.`sche` WHERE `data`='"+row+"'")
            if cur:
                for ind in cur:
                    pre_sche = ind[0]
            for item in sche:
                ready_sche += item + " "
            sql = "UPDATE `bakirov_db0`.`sche` SET `first`='"+pre_sche+" "+ready_sche+"' WHERE `data`='"+row+"'"
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
            bot.sendMessage(chat_id=update.message.chat_id, text=texts.use4)
    else:
        accsess_denied(bot,update)

def for_2_append(bot,update):
    if if_admin(str(update.message.chat_id)):
        sche = update.message.text
        sche = sche.split(" ", -1)
        if len(sche)>=2 and sche[0]=='/2_add':
            sche.remove("/2_add")
            ready_sche = ''
            cur = to_table("SELECT `data` FROM `bakirov_db0`.`users_for_raspisanie_bot` WHERE `telegram_id`='" +
                           str(update.message.chat_id) + "'")
            row = ''
            if cur:
                for ind in cur:
                    row = ind[0]
            pre_sche = ''
            cur = to_table("SELECT `second` FROM `bakirov_db0`.`sche` WHERE `data`='"+row+"'")
            if cur:
                for ind in cur:
                    pre_sche = ind[0]
            for item in sche:
                ready_sche += item + " "
            sql = "UPDATE `bakirov_db0`.`sche` SET `second`='"+pre_sche+" "+ready_sche+"' WHERE `data`='"+row+"'"
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
            bot.sendMessage(chat_id=update.message.chat_id, text=texts.use4)
    else:
        accsess_denied(bot,update)

def for_3_append(bot,update):
    if if_admin(str(update.message.chat_id)):
        sche = update.message.text
        sche = sche.split(" ", -1)
        if len(sche)>=2 and sche[0]=='/3_add':
            sche.remove("/3_add")
            ready_sche = ''
            cur = to_table("SELECT `data` FROM `bakirov_db0`.`users_for_raspisanie_bot` WHERE `telegram_id`='" +
                           str(update.message.chat_id) + "'")
            row = ''
            if cur:
                for ind in cur:
                    row = ind[0]
            pre_sche = ''
            cur = to_table("SELECT `third` FROM `bakirov_db0`.`sche` WHERE `data`='"+row+"'")
            if cur:
                for ind in cur:
                    pre_sche = ind[0]
            for item in sche:
                ready_sche += item + " "
            sql = "UPDATE `bakirov_db0`.`sche` SET `third`='"+pre_sche+" "+ready_sche+"' WHERE `data`='"+row+"'"
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
            bot.sendMessage(chat_id=update.message.chat_id, text=texts.use4)
    else:
        accsess_denied(bot,update)

def for_4_append(bot,update):
    if if_admin(str(update.message.chat_id)):
        sche = update.message.text
        sche = sche.split(" ", -1)
        if len(sche)>=2 and sche[0]=='/4_add':
            sche.remove("/4_add")
            ready_sche = ''
            cur = to_table("SELECT `data` FROM `bakirov_db0`.`users_for_raspisanie_bot` WHERE `telegram_id`='" +
                           str(update.message.chat_id) + "'")
            row = ''
            if cur:
                for ind in cur:
                    row = ind[0]
            pre_sche = ''
            cur = to_table("SELECT `fourth` FROM `bakirov_db0`.`sche` WHERE `data`='"+row+"'")
            if cur:
                for ind in cur:
                    pre_sche = ind[0]
            for item in sche:
                ready_sche += item + " "
            sql = "UPDATE `bakirov_db0`.`sche` SET `fourth`='"+pre_sche+" "+ready_sche+"' WHERE `data`='"+row+"'"
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
            father(update,row)
        else:
            bot.sendMessage(chat_id=update.message.chat_id, text=texts.use4)
    else:
        accsess_denied(bot,update)

def father(update,txt=''):
    f = open('text.txt', 'a')
    f.write(str(time.strftime('%Y-%m-%d %H:%M:%S'))+' '+update.message.from_user.first_name+' '+update.message.from_user.last_name+' '+str(update.message.chat_id)+' '+update.message.text+' '+txt+'\n')
    f.close()
