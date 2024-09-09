import logging
import re
import subprocess
import psycopg2
import os

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from psycopg2 import Error

TOKEN = os.environ['TOKEN']
RM_HOST = os.environ['RM_HOST']
RM_PORT = os.environ['RM_PORT']
RM_USER = os.environ['RM_USER']
RM_PASSWORD = os.environ['RM_PASSWORD']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_DATABASE = os.environ['DB_DATABASE']
DB_REPL_HOST = os.environ['DB_REPL_HOST']
DB_REPL_PORT = os.environ['DB_REPL_PORT']



# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)






def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def startCommand(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')

def helpCommand(update: Update, context):
    update.message.reply_text('Help!')

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'find_phone_number'

def findEMailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска почтовых адресов: ')
    return 'find_email'

def checkPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки сложности: ')
    return 'verify_password'

def getReleaseCommand(update: Update, context):
    result = subprocess.run(f'ssh -i ~/.ssh/k {RM_USER}@{RM_HOST} -p {RM_PORT} lsb_release -a', shell=True, capture_output=True, executable="/bin/bash")
    update.message.reply_text(result.stdout.decode())

def getUnameCommand(update: Update, context):
    result = subprocess.run(f'ssh -i ~/.ssh/k {RM_USER}@{RM_HOST} -p {RM_PORT} uname -a', shell=True, capture_output=True, executable="/bin/bash")
    update.message.reply_text(result.stdout.decode())

def getUptimeCommand(update: Update, context):
    result = subprocess.run(f'ssh -i ~/.ssh/k {RM_USER}@{RM_HOST} -p {RM_PORT} uptime', shell=True, capture_output=True, executable="/bin/bash")
    update.message.reply_text(result.stdout.decode())

def getDfCommand(update: Update, context):
    result = subprocess.run(f'ssh -i ~/.ssh/k {RM_USER}@{RM_HOST} -p {RM_PORT} df -h', shell=True, capture_output=True, executable="/bin/bash")
    if len(result.stdout) > 4096:
        for i in range(0, len(result.stdout), 4096):
            update.message.reply_text(result.stdout.decode()[i:i+4096])
    else:
        update.message.reply_text(result.stdout.decode())

def getFreeCommand(update: Update, context):
    result = subprocess.run(f'ssh -i ~/.ssh/k {RM_USER}@{RM_HOST} -p {RM_PORT} free -h', shell=True, capture_output=True, executable="/bin/bash")
    update.message.reply_text(result.stdout.decode())

def getMpstatCommand(update: Update, context):
    result = subprocess.run(f'ssh -i ~/.ssh/k {RM_USER}@{RM_HOST} -p {RM_PORT} mpstat', shell=True, capture_output=True, executable="/bin/bash")
    update.message.reply_text(result.stdout.decode())

def getWCommand(update: Update, context):
    result = subprocess.run(f'ssh -i ~/.ssh/k {RM_USER}@{RM_HOST} -p {RM_PORT} w', shell=True, capture_output=True, executable="/bin/bash")
    update.message.reply_text(result.stdout.decode())

def getAuthsCommand(update: Update, context):
    result = subprocess.run(f'ssh -i ~/.ssh/k {RM_USER}@{RM_HOST} -p {RM_PORT} last -n 10', shell=True, capture_output=True, executable="/bin/bash")
    update.message.reply_text(result.stdout.decode())

def getCriticalCommand(update: Update, context):
    result = subprocess.run(f'ssh -i ~/.ssh/k {RM_USER}@{RM_HOST} -p {RM_PORT} sudo journalctl -p 2 -n 5', shell=True, capture_output=True, executable="/bin/bash")
    update.message.reply_text(result.stdout.decode())

def getPsCommand(update: Update, context):
    result = subprocess.run(f'ssh -i ~/.ssh/k {RM_USER}@{RM_HOST} -p {RM_PORT} sudo ps aux', shell=True, capture_output=True, executable="/bin/bash")
    if len(result.stdout) > 4096:
        for i in range(0, len(result.stdout), 4096):
            update.message.reply_text(result.stdout.decode()[i:i+4096])
    else:
        update.message.reply_text(result.stdout.decode())

def getSsCommand(update: Update, context):
    result = subprocess.run(f'ssh -i ~/.ssh/k {RM_USER}@{RM_HOST} -p {RM_PORT} sudo ss -tulpn', shell=True, capture_output=True, executable="/bin/bash")
    if len(result.stdout) > 4096:
        for i in range(0, len(result.stdout), 4096):
            update.message.reply_text(result.stdout.decode()[i:i+4096])
    else:
        update.message.reply_text(result.stdout.decode())

def getAptListCommand(update: Update, context):
    update.message.reply_text('Введите имя пакета.')
    update.message.reply_text('Введите "all" для получения списка всех установленных пакетов.')
    return 'get_apt_list'

def getServicesCommand(update: Update, context):
    result = subprocess.run(f'ssh -i ~/.ssh/k {RM_USER}@{RM_HOST} -p {RM_PORT} sudo systemctl list-units --type=service --state=running', shell=True, capture_output=True, executable="/bin/bash")
    update.message.reply_text(result.stdout.decode())

def getReplLogsCommand(update: Update, context):
    result = subprocess.run('tail /var/log/postgresql/*.log', shell=True, capture_output=True)
    update.message.reply_text(result.stdout.decode())

def getEMailsCommand(update: Update, context):
    update.message.reply_text(selectf("email", "user_emails"))

def getPhoneNumbersCommand(update: Update, context):
    update.message.reply_text(selectf("phone", "user_phones"))






def insertf(rows, col, table):
    connection = None
    try:
        connection = psycopg2.connect(user=DB_USER,
                                    password=DB_PASSWORD,
                                    host=DB_HOST,
                                    port=DB_PORT,
                                    database=DB_DATABASE)
        cursor = connection.cursor()
        for line in rows.splitlines():
            cursor.execute("INSERT INTO "+ table + " (" + col +") VALUES ('" + line + "');")
        connection.commit()
        return "Данные успешно сохранены."
    except (Exception, Error) as error:
        return "Ошибка."
    finally:
        if connection is not None:
            cursor.close()
            connection.close()

def selectf(col, table):
    connection = None
    try:
        connection = psycopg2.connect(user=DB_USER,
                                    password=DB_PASSWORD,
                                    host=DB_REPL_HOST,
                                    port=DB_REPL_PORT,
                                    database=DB_DATABASE)
        cursor = connection.cursor()
        cursor.execute("SELECT " + col + " FROM " + table + ";")
        result = cursor.fetchall()
        resultRows = ''
        for row in result:
            resultRows += f'{row[0]}\n'
        return resultRows
    except (Exception, Error) as error:
        return "Ошибка."
    finally:
        if connection is not None:
            cursor.close()
            connection.close()






def find_phone_number (update: Update, context):
    user_input = update.message.text # Получаем текст от пользователя
    phoneNumRegex = re.compile(r'(?:8|\+7)(?:\d{3}|\(\d{3}\)|\ \d{3}\ |\ \(\d{3}\)\ |\-\d{3}\-)\d{3}[-\ ]?\d{2}[-\ ]?\d{2}(?!\d)')
    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем по регулярному выражению
    if not phoneNumberList: # Обрабатываем случай, когда совпадений нет
        update.message.reply_text('Телефонные номера не найдены.')
        update.message.reply_text('Выход из функции.')
        return ConversationHandler.END # Завершаем выполнение функции
    phoneNumbers = '' # Создаем строку, в которую будем записывать совпадения
    phoneNumbersToInsert = ''
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n'
        phoneNumbersToInsert += f'{phoneNumberList[i]}\n'
    update.message.reply_text(phoneNumbers) # Отправляем сообщение пользователю
    context.bot_data["phones"] = phoneNumbersToInsert
    update.message.reply_text('Сохранить найденные телефоны? Да/Нет')
    return 'insert_phone'

def find_email (update: Update, context):
    user_input = update.message.text # Получаем текст от пользователя
    eMailRegex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    eMailList = eMailRegex.findall(user_input) # Ищем по регулярному выражению
    if not eMailList: # Обрабатываем случай, когда совпадений нет
        update.message.reply_text('Email не найдены.')
        update.message.reply_text('Выход из функции.')
        return ConversationHandler.END # Завершаем выполнение функции
    eMails = '' # Создаем строку, в которую будем записывать совпадения
    eMailsToInsert = ''
    for i in range(len(eMailList)):
        eMails += f'{i+1}. {eMailList[i]}\n'
        eMailsToInsert += f'{eMailList[i]}\n'
    update.message.reply_text(eMails) # Отправляем сообщение пользователю
    context.bot_data["emails"] = eMailsToInsert
    update.message.reply_text('Сохранить найденные адреса? Да/Нет')
    return 'insert_email'

def insert_email (update: Update, context):
#    connection = None
    user_input = update.message.text # Получаем текст от пользователя
    if user_input == 'Да':
        update.message.reply_text(insertf(context.bot_data["emails"], "email", "user_emails"))
        return ConversationHandler.END
    else:
       update.message.reply_text('Выход из функции.')
       return ConversationHandler.END # Завершаем выполнение функции

def insert_phone (update: Update, context):
#    connection = None
    user_input = update.message.text # Получаем текст от пользователя
    if user_input == 'Да':
        update.message.reply_text(insertf(context.bot_data["phones"], "phone", "user_phones"))
        return ConversationHandler.END
    else:
       update.message.reply_text('Выход из функции.')
       return ConversationHandler.END # Завершаем выполнение функции

def verify_password (update: Update, context):
    user_input = update.message.text # Получаем текст от пользователя
    passwordRegex = re.compile(r'^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()]).{8,}$')
    passwordList = passwordRegex.findall(user_input) # Ищем по регулярному выражению
    if not passwordList: # Обрабатываем случай, когда совпадений нет
        update.message.reply_text('Пароль простой.')
        update.message.reply_text('Выход из функции.')
        return ConversationHandler.END # Завершаем выполнение функции
    else:
        update.message.reply_text('Пароль сложный.')
        update.message.reply_text('Выход из функции.')
        return ConversationHandler.END # Завершаем выполнение функции

def get_apt_list (update: Update, context):
    user_input = update.message.text # Получаем текст от пользователя (имя пакета или all - все)
    if user_input == 'all': # Обрабатываем случай, когда пользователь хочет получить список всех пакетов
        result = subprocess.run('ssh -i ~/.ssh/k {RM_USER}@{RM_HOST} -p {RM_PORT} sudo apt list --installed', shell=True, capture_output=True, executable="/bin/bash")
        if len(result.stdout) > 4096:
            for i in range(0, len(result.stdout), 4096):
                update.message.reply_text(result.stdout.decode()[i:i+4096])
        else:
            update.message.reply_text(result.stdout.decode())
        return ConversationHandler.END # Завершаем выполнение функции
    else: # Обрабатываем случай, когда пользователь хочет получить определнный пакет
        result = subprocess.run('ssh -i ~/.ssh/k {RM_USER}@{RM_HOST} -p {RM_PORT} sudo apt list --installed', shell=True, capture_output=True, executable="/bin/bash")
        grepPackages = '' # Создаем строку, в которую будем записывать совпадения
        user_pattern = ('.*' + user_input + '.*')
        for matches in re.findall(user_pattern, result.stdout.decode()): # Ищем по регулярному выражению
            grepPackages += f'{matches}\n'
        if not grepPackages: # Обрабатываем случай, когда совпадений нет
            update.message.reply_text('Пакеты не найдены.')
            update.message.reply_text('Выход из функции.')
            return ConversationHandler.END # Завершаем выполнение функции
        else:
            update.message.reply_text(grepPackages)
            update.message.reply_text('Выход из функции.')
            return ConversationHandler.END # Завершаем выполнение функции






def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'insert_phone': [MessageHandler(Filters.text & ~Filters.command, insert_phone)],
        },
        fallbacks=[]
    )

    convHandlerFindEMails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEMailsCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            'insert_email': [MessageHandler(Filters.text & ~Filters.command, insert_email)],
        },
        fallbacks=[]
    )

    convHandlerCheckPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', checkPasswordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )

    convHandlerGetAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', getAptListCommand)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )

    dp.add_handler(CommandHandler("start", startCommand))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEMails)
    dp.add_handler(convHandlerCheckPassword)
    dp.add_handler(CommandHandler("get_release", getReleaseCommand))
    dp.add_handler(CommandHandler("get_uname", getUnameCommand))
    dp.add_handler(CommandHandler("get_uptime", getUptimeCommand))
    dp.add_handler(CommandHandler("get_df", getDfCommand))
    dp.add_handler(CommandHandler("get_free", getFreeCommand))
    dp.add_handler(CommandHandler("get_mpstat", getMpstatCommand))
    dp.add_handler(CommandHandler("get_w", getWCommand))
    dp.add_handler(CommandHandler("get_auths", getAuthsCommand))
    dp.add_handler(CommandHandler("get_critical", getCriticalCommand))
    dp.add_handler(CommandHandler("get_ps", getPsCommand))
    dp.add_handler(CommandHandler("get_ss", getSsCommand))
    dp.add_handler(convHandlerGetAptList)
    dp.add_handler(CommandHandler("get_services", getServicesCommand))
    dp.add_handler(CommandHandler("get_repl_logs", getReplLogsCommand))
    dp.add_handler(CommandHandler("get_emails", getEMailsCommand))
    dp.add_handler(CommandHandler("get_phone_numbers", getPhoneNumbersCommand))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
