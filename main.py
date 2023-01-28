from datetime import datetime, timedelta
import requests
import json
import random
import time
from configparser import ConfigParser
from pytz import timezone
from art import tprint
import plyer

tprint('AutoPost      v0.0.2')
config = ConfigParser()
api_version = '9'

def check_answer(name):
    if name == 'да' or 'lf':
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
    
    global warp_names
    warp_names = input('Введите название варпа (можно добавить несколько вариантов, разделяя их с помощью ; ): ')

    global delete
    delete = input('Удалять сообщения? (да/нет): ')
    delete = check_answer(delete)
        
    global random_delete
    random_delete = input('Всегда удалять сообщения? (да/нет): ')
    random_delete = check_answer(random_delete)
        
    global notification
    notification = input('Уведомлять о отправке сообщения? (да/нет): ')
    notification = check_answer(notification)
        
    global MIN_delay
    MIN_delay = input('Введите минимальный промежуток между сообщениями (в минутах): ')
    
    global MAX_delay
    MAX_delay = input('Введите максимальный промежуток между сообщениями (в минутах): ')

    if save:
        config['Config']['save'] = str(save)
        config['Config']['discord_token'] = discord_token
        config['Config']['channel_ID'] = channel_ID
        config['Config']['advertisements'] = str(advertisements)
        config['Config']['delete'] = str(delete)
        config['Config']['random_delete'] = str(random_delete)
        config['Config']['MIN_delay'] = MIN_delay
        config['Config']['MAX_delay'] = MAX_delay
        config['Config']['warp_names'] = str(warp_names)
        config['Config']['notification'] = str(notification)
               
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
        warp_names = config.get('Config', 'warp_names')
        delete = eval(config.get('Config', 'delete'))
        random_delete = eval(config.get('Config', 'random_delete'))
        notification = eval(config.get('Config', 'notification'))
        MIN_delay = config.get('Config', 'MIN_delay')
        MAX_delay = config.get('Config', 'MAX_delay')
    else:
        new_config()
else:
    new_config()

headers = {
    'authorization': discord_token
}

advertisements = advertisements.split(';')
warp_names = warp_names.split(';')
MIN_delay = int(MIN_delay) * 60
MAX_delay = int(MAX_delay) * 60

def send_message():
    content = {
        'content': random.SystemRandom().choice(advertisements)
    }
    sended_message = requests.post(f'https://discord.com/api/v{api_version}/channels/{channel_ID}/messages', headers=headers, data=content)
    sended_message = sended_message.text.encode().decode('unicode-escape')
    sended_message_json = json.loads(sended_message.replace('\\', ''))
    message_id = sended_message_json['id']
    
    if delete:
        if random_delete:
            if random.randint(0, 1) == 0:
                requests.delete(f'https://discord.com/api/v{api_version}/channels/{channel_ID}/messages/{message_id}', headers=headers)
        else:
            requests.delete(f'https://discord.com/api/v{api_version}/channels/{channel_ID}/messages/{message_id}', headers=headers)

    if notification:
        plyer.notification.notify(title='AutoPost', message='Сообщение было успешно отправлено.')
        
    random_time = random.randint(MIN_delay, MAX_delay)
    print('До следующего сообщения: ' + str(random_time) + ' сек.')
    time.sleep(random_time)

while True:
    start_time = datetime.now() + timedelta(seconds=10)
    while start_time > datetime.now() - timedelta(minutes=10): 
        messages = requests.get(f'https://discord.com/api/v{api_version}/channels/{channel_ID}/messages?limit=100', headers=headers)
        messages = messages.text
        messages = messages.replace('\\n', '')
        messages = messages.replace('\\"', '')
        messages = messages.encode().decode("unicode-escape")
        messages = messages.replace('\\', '')

        messages = json.loads(messages)

        message_founded = False
        for j in messages:
            if not message_founded: 
                if j['author'].get('id') == '1064118278231949342': #618536577282342912
                    content = j['content'].lower()
                    for warp_name in warp_names:
                        if content.find(warp_name) != -1:
                            print('Найдено упоминание: ' + j['content'])
                            message_founded = True
                            message_timestamp = j['timestamp']

        if message_founded:
            message_founded = False

            message_time = datetime.strptime(message_timestamp, '%Y-%m-%dT%H:%M:%S.%f+00:00')
            
            time_now = datetime.now(timezone('Europe/Moscow'))
            time_now = time_now - timedelta(hours=3)
            time_now = time_now.replace(tzinfo=None)
            
            if message_time < time_now - timedelta(minutes=10):
                send_message()
            else:
                wait = message_time - time_now + timedelta(minutes=10, seconds=10)
                wait = wait.total_seconds()
                print('Сообщение будет отправлено через: ' + str(round(wait)) + ' сек.')
                time.sleep(wait)
        else:
            time.sleep(1)    
    else:
        send_message()