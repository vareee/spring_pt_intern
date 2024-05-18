import aiogram
import asyncio
import logging
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
import re
import paramiko
import psycopg2
import os
from dotenv import load_dotenv
import subprocess


load_dotenv()
router = aiogram.Router()

# класс для отслеживания состояния пользователей (для структурирования диалога)
class Action(StatesGroup):
    finding_email = State()
    finding_phone_number = State()
    pushing_email = State()
    pushing_phone_number = State()
    verifying_password = State()
    getting_apt_list = State()
    getting_apt_info = State()

# приветственное сообщение
@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Привет! Список возможных команд:\n/find_email\n/find_phone_number\n"
                         "/verify_password\n/get_release\n/get_uname\n/get_uptime\n/get_df\n/get_free\n"
                         "/get_mpstat\n/get_w\n/get_auths\n/get_critical\n/get_critical\n/get_ss\n/get_apt_list\n/get_ps\n"
                         "/get_services\n/get_repl_logs\n/get_emails\n/get_phone_numbers")

# пользователь входит в состояние "найти email"
@router.message(Command("find_email"))
async def email_start(message: Message, state: FSMContext):
    await message.answer(
        text="Введите текст для поиска в нем адресов электронной почты:"
    )
    await state.set_state(Action.finding_email)

# пользователь вводит текст для поиска в нем адресов электронной почты
@router.message(Action.finding_email)
async def find_email(message: Message, state: FSMContext):
    email_regex = re.compile(r'\b[a-zA-Z0-9._%+-]+@[A-Za-z0-9]+\.[A-Z|a-z]{2,}\b')
    email_list = email_regex.findall(message.text)
    if not email_list:
        ans = "Не было найдено ни одного адреса электронной почты!"
        await state.clear()
    else:
        ans = "Найденные в тексте адреса электронной почты:\n"
        emails = ""
        for email in email_list:
            emails += email + "\n"
        ans += emails + "Записать найденные адреса в БД? (Да/Нет)"
        await state.set_state(Action.pushing_email)
        await state.update_data(email_text=emails)
    await message.answer(
        text=ans,
    )

# пользователь входит в состояние для отправки email в бд
@router.message(Action.pushing_email)
async def insert_email(message: Message, state: FSMContext):
    if message.text.lower() == "да":
        connection = None
        ans = ""
        state_data = await state.get_data()
        emails = state_data["email_text"]
        try:
            connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                        password=os.getenv('DB_PASSWORD'),
                                        host=os.getenv('DB_HOST'),
                                        port=os.getenv('DB_PORT'), 
                                        database=os.getenv('DB_DATABASE'))

            cursor = connection.cursor()
            for email in emails.split("\n"):
                if email != "":
                    cursor.execute(f"insert into emails (email) values ('{email}');")
            connection.commit()
            ans = "Команда успешно выполнена"
            logging.info(ans)
        except (Exception, psycopg2.Error) as error:
            ans = "Ошибка при работе с PostgreSQL!"
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
            await message.answer(text=ans)
    await state.clear()
        
# пользователь входит в состояние "найти телефонный номер"
@router.message(Command("find_phone_number"))
async def phone_number_start(message: Message, state: FSMContext):
    await message.answer(
        text="Введите текст для поиска в нем номера телефона:"
    )
    await state.set_state(Action.finding_phone_number)

# пользователь вводит текст для поиска в нем телефонных номеров
@router.message(Action.finding_phone_number)
async def find_phone_number(message: Message, state: FSMContext):
    phone_number_regex = re.compile(r'(?:\+7 \d{3} \d{3} \d{2} \d{2}\b)|(?:(?<!\+)8 \d{3} \d{3} \d{2} \d{2}\b)|(?:\+7-\d{3}-\d{3}-\d{2}-\d{2}\b)|(?:(?<!\+)8-\d{3}-\d{3}-\d{2}-\d{2}\b)|(?:\+7\(\d{3}\)\d{7}\b)|(?:(?<!\+)8[\(]\d{3}[\)]\d{7}\b)|(?:\+7 [\(]\d{3}[\)] \d{3} \d{2} \d{2}\b)|(?:(?<!\+)8 [\(]\d{3}[\)] \d{3} \d{2} \d{2}\b)|(?:\+7\d{10}\b)|(?:(?<!\+)8\d{10}\b)')
    phone_number_list = phone_number_regex.findall(message.text)
    if not phone_number_list:
        ans = "Не было найдено ни одного телефонного номера!"
        await state.clear()
    else:
        ans = "Найденные в тексте телефонные номера:\n"
        phone_numbers = ""
        for phone_number in phone_number_list:
            phone_numbers += phone_number + "\n"
        ans += phone_numbers + "Записать найденные адреса в БД? (Да/Нет)"
        await state.set_state(Action.pushing_phone_number)
        await state.update_data(phone_number_text=phone_numbers)
    await message.answer(
        text=ans,
    )
    
# пользователь входит в состояние для отправки phone number в бд
@router.message(Action.pushing_phone_number)
async def insert_phone_number(message: Message, state: FSMContext):
    if message.text.lower() == "да":
        connection = None
        ans = ""
        state_data = await state.get_data()
        phone_numbers = state_data["phone_number_text"]
        try:
            connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                        password=os.getenv('DB_PASSWORD'),
                                        host=os.getenv('DB_HOST'),
                                        port=os.getenv('DB_PORT'), 
                                        database=os.getenv('DB_DATABASE'))

            cursor = connection.cursor()
            for phone_number in phone_numbers.split("\n"):
                if phone_number != "":
                    cursor.execute(f"insert into phone_numbers (phone_number) values ('{phone_number}');")
            connection.commit()
            ans = "Команда успешно выполнена"
            logging.info(ans)
        except (Exception, psycopg2.Error) as error:
            ans = "Ошибка при работе с PostgreSQL!"
            logging.error("Ошибка при работе с PostgreSQL: %s", error)
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
            await message.answer(text=ans)
    await state.clear()
    
# пользователь входит в состояние "проверить пароль на сложность"
@router.message(Command("verify_password"))
async def verify_password_start(message: Message, state: FSMContext):
    await message.answer(
        text="Введите текст для пароль для проверки его на сложность:"
    )
    await state.set_state(Action.verifying_password)

# пользователь вводит пароль для проверки его на сложность
@router.message(Action.verifying_password)
async def verify_password(message: Message, state: FSMContext):
    await state.update_data(email_text=message.text.lower())
    pass_regex_cap = re.compile(r'(?=.*[A-Z])(?=.*[a-z])(?=.*\d)') # проверка наличия хотя бы одной заглавной буквы, одной строчной буквы и одной цифры
    pass_regex_special = re.compile(r'(?=.*[!@#$%^&*()])') # проверка наличия хотя бы одного специального символа
    if not pass_regex_cap.search(message.text) or not pass_regex_special.search(message.text) or len(message.text) < 8:
        ans = "Пароль простой"
    else:
        ans = "Пароль сложный"
    await message.answer(text=ans)
    await state.clear()

# команда lsb_release
@router.message(Command("get_release"))
async def get_release(message: Message):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('lsb_release -r')
    data = stdout.read() 
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1] 
    await message.answer(
        text=data
    )
    
# команда uname
@router.message(Command("get_uname"))
async def get_uname(message: Message):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('uname -mnr')
    data = stdout.read() 
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1] 
    await message.answer(
        text=data
    )
    
# команда uptime
@router.message(Command("get_uptime"))
async def get_uptime(message: Message):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('uptime')
    data = stdout.read() 
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1] 
    await message.answer(
        text=data
    )
    
# команда df
@router.message(Command("get_df"))
async def get_df(message: Message):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('df -h')
    data = stdout.read() 
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1] 
    await message.answer(
        text=data
    )

# команда free
@router.message(Command("get_free"))
async def get_free(message: Message):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('free -h')
    data = stdout.read() 
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1] 
    await message.answer(
        text=data
    )

# команда mpstat
@router.message(Command("get_mpstat"))
async def get_mpstat(message: Message):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('mpstat')
    data = stdout.read() 
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1] 
    await message.answer(
        text=data
    )

# команда w
@router.message(Command("get_w"))
async def get_w(message: Message):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('w')
    data = stdout.read() 
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1] 
    await message.answer(
        text=data
    )

# команда get auth logs
@router.message(Command("get_auths"))
async def get_auths(message: Message):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('tail -n 10 /var/log/auth.log')
    data = stdout.read() 
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1] 
    await message.answer(
        text=data
    )

# команда get critical logs
@router.message(Command("get_critical"))
async def get_critical(message: Message):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('grep -i "critical" /var/log/syslog | tail -n 5')
    data = stdout.read() 
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1] 
    await message.answer(
        text=data
    )

# команда ps
@router.message(Command("get_ps"))
async def get_ps(message: Message):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('ps')
    data = stdout.read() 
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1] 
    await message.answer(
        text=data
    )
# команда ss
@router.message(Command("get_ss"))
async def get_ss(message: Message):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('ss | head -n 10')
    data = stdout.read() 
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1] 
    await message.answer(
        text=data
    )

# пользователь входит в состояние "узнать информацию о пакетах"
@router.message(Command("get_apt_list"))
async def apt_list_start(message: Message, state: FSMContext):
    await message.answer(
        text="Выберите интересующее вас действие:\n1. Вывести информацию о всех пакетах\n2. Вывести информацию о конкретном пакете"
    )
    await state.set_state(Action.getting_apt_list)

# пользователь выбирает вариант использования программы
@router.message(Action.getting_apt_list)
async def get_apt_list(message: Message, state: FSMContext):
    if message.text == '1':
        host = os.getenv('RM_HOST')
        port = os.getenv('RM_PORT')
        username = os.getenv('RM_USER')
        password = os.getenv('RM_PASSWORD')
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username, password=password, port=port)
        stdin, stdout, stderr = client.exec_command('apt list --installed')
        data = stdout.read() 
        client.close()
        ans = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1] 
        await state.clear()
    elif message.text == '2':
        ans = "Введите название пакета: "
        await state.set_state(Action.getting_apt_info)
    else:
        ans = "Попробуйте выбрать действие еще раз!"
    for i in range(0, len(ans), 4096):
        await message.answer(text=ans[i:i+4096])

# пользователь вводит название пакета для получения информации о нем
@router.message(Action.getting_apt_info)
async def get_apt_info(message: Message, state: FSMContext):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command(f'apt list {message.text}')
    data = stdout.read() 
    client.close()
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1] 
    await message.answer(
        text=data
    )
    await state.clear()

# запущенные службы
@router.message(Command("get_services"))
async def get_apt_services(message: Message):
    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('systemctl list-units --type=service')
    data = stdout.read() 
    client.close()
    ans = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1] 
    for i in range(0, len(ans), 4096):
        await message.answer(text=ans[i:i+4096])

# replication logs
@router.message(Command("get_repl_logs"))
async def get_repl_logs(message: Message):
    result = subprocess.run(["tail", "-n", "10", "/var/log/postgresql/postgresql.log"], capture_output=True, text=True)
    data = result.stdout
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1] 
    await message.answer(
        text=data
    )

# достать email из бд
@router.message(Command("get_emails"))
async def get_emails(message: Message):
    connection = None
    ans = ""
    try:
        connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                    password=os.getenv('DB_PASSWORD'),
                                    host=os.getenv('DB_HOST'),
                                    port=os.getenv('DB_PORT'), 
                                    database=os.getenv('DB_DATABASE'))

        cursor = connection.cursor()
        cursor.execute("SELECT email FROM emails;")
        data = cursor.fetchall()
        for row in data:
            ans += row[0] + "\n"
        logging.info("Команда успешно выполнена")
    except (Exception, psycopg2.Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
    if ans == "":
        ans = "Нет записей в таблице!"
    await message.answer(
        text=ans
    )

# достать phone number из бд
@router.message(Command("get_phone_numbers"))
async def get_phone_numbers(message: Message):
    connection = None
    ans = ""
    try:
        connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                    password=os.getenv('DB_PASSWORD'),
                                    host=os.getenv('DB_HOST'),
                                    port=os.getenv('DB_PORT'), 
                                    database=os.getenv('DB_DATABASE'))

        cursor = connection.cursor()
        cursor.execute("SELECT phone_number FROM phone_numbers;")
        data = cursor.fetchall()
        for row in data:
            ans += row[0] + "\n"
        logging.info("Команда успешно выполнена")
    except (Exception, psycopg2.Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
    if ans == "":
        ans = "Нет записей в таблице!"
    await message.answer(
        text=ans
    )

async def main():
    dp = aiogram.Dispatcher()

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        filename='bot_logs.txt'
    )


    bot = aiogram.Bot(os.getenv('TOKEN'))

    dp.include_router(router)


    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

