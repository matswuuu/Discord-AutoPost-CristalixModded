from datetime import datetime, timedelta
from discum import Client
from json import loads
from random import randint, SystemRandom
from time import sleep
from pytz import timezone
from configparser import ConfigParser
from art import tprint

tprint('AutoPost      v0.0.2')
config = ConfigParser()

def check_answer(name):
    if name == 'да':
        return True
    else:
        return False

def new_config():
    save = input('Сохранить конфигурацию? (да/нет): ')
    save = check_answer(save)
        
    global discord_token
    discord_token = input('Введите Ваш Discord-token: ')
    
    global channel_ID
    channel_ID = input('Введите ID канала, в который будут отсылаться сообщения: ')
    
    global advertisements
    advertisements = input('Введите текст (можно добавить несколько вариантов, разделяя их с помощью ; ): ')
    advertisements = advertisements.split(';')
    
    global delete
    delete = input('Удалять сообщения? (да/нет): ')
    delete = check_answer(save)
        
    global random_delete
    random_delete = input('Всегда удалять сообщения? (да/нет): ')
    random_delete = check_answer(random_delete)
        
    global MIN_delay
    MIN_delay = input('Введите минимальный промежуток между сообщениями (в минутах): ')
    MIN_delay = int(MIN_delay) * 60
    
    global MAX_delay
    MAX_delay = input('Введите максимальный промежуток между сообщениями (в минутах): ')
    MAX_delay = int(MAX_delay) * 60

    global warp_names
    warp_names = input('Введите название варпа (можно добавить несколько вариантов, разделяя их с помощью ; ): ')
    warp_names = warp_names.split(';')

    if save:
        config['Config']['save'] = str(save)
        config['Config']['discord_token'] = discord_token
        config['Config']['channel_ID'] = channel_ID
        config['Config']['advertisements'] = str(advertisements)
        config['Config']['delete'] = str(delete)
        config['Config']['random_delete'] = str(random_delete)
        config['Config']['MIN_delay'] = str(MIN_delay)
        config['Config']['MAX_delay'] = str(MAX_delay)
        config['Config']['warp_names'] = str(warp_names)
               
        with open('config.ini', 'w') as config_file:
            config.write(config_file)

config.read_file(open(r'config.ini'))
save = eval(config.get('Config', 'save'))      
if save:  
    print('Последняя конфигурация: ')
    for x in config['Config']:
        print(x + ' = ' + config['Config'][x])
    choice = input('Загрузить прошлую конфигурацию? (да/нет): ')
    choice = check_answer(choice)
    if choice:
        discord_token = config.get('Config', 'discord_token')
        channel_ID = config.get('Config', 'channel_ID')
        advertisements = config.get('Config', 'advertisements')
        advertisements = advertisements.replace('\'', '')
        advertisements = advertisements.strip('][').split(', ')
        delete = eval(config.get('Config', 'delete'))
        random_delete = eval(config.get('Config', 'random_delete'))
        MIN_delay = int(config.get('Config', 'MIN_delay'))
        MAX_delay = int(config.get('Config', 'MAX_delay'))
        warp_names = config.get('Config', 'warp_names')
        warp_names = warp_names.replace('\'', '')
        warp_names = warp_names.strip('][').split(', ')
    else:
        new_config()
else:
    new_config()

bot = Client(token=discord_token)

def send_message():
    sended_message = bot.sendMessage(channelID=channel_ID, message=SystemRandom().choice(advertisements))
    sended_message = sended_message.text.encode().decode('unicode-escape')
    sended_message_json = loads(sended_message.replace('\\', ''))

    if delete:
        if random_delete:
            if randint(0, 1) == 0:
                bot.deleteMessage(channelID=channel_ID, messageID=sended_message_json['id'])
        else:
            bot.deleteMessage(channelID=channel_ID, messageID=sended_message_json['id'])

    random_time = randint(MIN_delay, MAX_delay)
    print('До следующего сообщения: ' + str(random_time) + ' сек.')
    sleep(random_time)

while True:
    last_message_id = None
    start_time = datetime.now() + timedelta(seconds=10)
    while start_time > datetime.now() - timedelta(minutes=10): 
        messages = bot.getMessages(channelID=channel_ID, num=100, beforeDate=last_message_id)
        messages = messages.text
        messages = messages.replace('\\n', '')
        messages = messages.replace('\\"', '')
        messages = messages.encode().decode("unicode-escape")
        messages = messages.replace('\\', '')

        messages = loads(messages)

        message_founded = False
        for j in messages:
            if not message_founded: 
                if j['author'].get('id') == '618536577282342912':
                    content = j['content'].lower()
                    for warp_name in warp_names:
                        if content.find(warp_name) != -1:
                            print('Найдено упоминание: ' + j['content'])
                            message_founded = True
                            message_timestamp = j['timestamp']
            last_message_id = j['id']

        if message_founded:
            message_founded = False
            last_message_id = None

            message_time = datetime.strptime(message_timestamp, '%Y-%m-%dT%H:%M:%S.%f+00:00')
            
            tz = timezone('Europe/Moscow')
            time_now = datetime.now(tz)
            time_now = time_now - timedelta(hours=3)
            time_now = time_now.replace(tzinfo=None)
            
            if message_time < time_now - timedelta(minutes=10):
                send_message()
            else:
                wait = message_time - time_now + timedelta(minutes=10, seconds=10)
                wait = wait.total_seconds()
                print('Сообщение будет отправлено через: ' + str(wait) + ' сек.')
                sleep(wait)
        else:
            sleep(1)    
    else:
        send_message()