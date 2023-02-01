from datetime import datetime, timedelta
import json
import requests
import random
import time
from pytz import timezone
from configparser import ConfigParser
from art import tprint
from plyer import notification

tprint('AutoPost')
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
    
    servers = [ 'NeoTech-1', 'Magica-1', 'Magica-2', 'Magica-3', 'DivinePVP-1', 'TechnoMagic-1', 'TechnoMagic-2', 'SkyVoid-1', 'SkyVoid-2', 'Galax-1' ]
    server = 1
    for i in servers:
        print(str(server) + '. ' + i)
        server = server + 1 
    
    server_input = input('Введите номер сервера: ')
    global channel_ID
    if server_input == '1': # NeoTech-1
        channel_ID = '755004580047224883'
    elif server_input == '2': # Magica-1
        channel_ID = '755004657054646292'
    elif server_input == '3': # Magica-2
        channel_ID = '770297440561135616'
    elif server_input == '4': # Magica-3
        channel_ID = '774325305396559913'
    elif server_input == '5': # DivinePVP-1
        channel_ID = '755004714298507325'
    elif server_input == '6': # TechnoMagic-1
        channel_ID = '755004863502352454'
    elif server_input == '7': # TechnoMagic-2
        channel_ID = '755004894775345164'
    elif server_input == '8': # SkyVoid-1
        channel_ID = '864707584535691265'
    elif server_input == '9': # SkyVoid-2
        channel_ID = '1041323357108445275'
    elif server_input == '10': # Galax-1
        channel_ID = '803444951970086964'
    
    global advertisements
    advertisements = input('Введите текст (можно добавить несколько вариантов через ^ ): ')
    
    global warp_names
    warp_names = input('Введите название варпа (можно добавить несколько вариантов через ^ ): ')
    
    global delete
    delete = input('Удалять сообщения? (да/нет): ')
    delete = check_answer(delete)
        
    global random_delete
    if delete:
        random_delete = input('Всегда удалять сообщения? (да/нет): ')
        random_delete = check_answer(random_delete)
    else:
        random_delete = False

    global notification
    notification = input('Уведолмлять об отправке сообщения? (да/нет): ')
    notification = check_answer(notification)

    global MIN_delay
    MIN_delay = input('Введите минимальный промежуток между сообщениями (в минутах): ')
    
    global MAX_delay
    MAX_delay = input('Введите максимальный промежуток между сообщениями (в минутах): ')

    if save:
        config['Config']['save'] = str(save)
        config['Config']['discord_token'] = discord_token
        config['Config']['channel_ID'] = channel_ID
        config['Config']['advertisements'] = advertisements
        config['Config']['delete'] = str(delete)
        config['Config']['random_delete'] = str(random_delete)
        config['Config']['notification'] = str(notification)
        config['Config']['MIN_delay'] = MIN_delay
        config['Config']['MAX_delay'] = MAX_delay
        config['Config']['warp_names'] = warp_names
               
        with open('config.ini', 'w') as config_file:
            config.write(config_file)

config.read_file(open(r'config.ini'))
save = eval(config.get('Config', 'save'))      
if save:  
    print('Последняя конфигурация: ')
    for x in config['Config']:
        print(x + ' = ' + config['Config'][x])

    choice = input('Загрузить последнюю конфигурацию? (да/нет): ')
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

advertisements = advertisements.split('^')
warp_names = warp_names.split('^')
MIN_delay = int(MIN_delay) * 60
MAX_delay = int(MAX_delay) * 60

api_version = '9'
while True:
    for warp_name in warp_names:
        results = requests.get(f'https://discord.com/api/v{api_version}/channels/{channel_ID}/messages/search?channel_id={channel_ID}&author_id=618536577282342912&content={warp_name}&sort_by=timestamp&sort_order=desc&limit=5', headers={'authorization': discord_token})
        results = json.loads(results.text)
        for i in results['messages']:
            for o in i:
                message_timestamp = o['timestamp']
                message_time = datetime.strptime(message_timestamp, '%Y-%m-%dT%H:%M:%S.%f+00:00')
                
                time_now = datetime.now(timezone('Europe/Moscow'))
                time_now = time_now - timedelta(hours=3)
                time_now = time_now.replace(tzinfo=None)
                
    if message_time < time_now - timedelta(minutes=10, seconds=10):
        sended_message = requests.post(f'https://discord.com/api/v{api_version}/channels/{channel_ID}/messages', headers={'authorization': discord_token}, data={
            'content': random.SystemRandom().choice(advertisements)})
        sended_message = sended_message.text.encode().decode('unicode-escape')
        sended_message_json = json.loads(sended_message.replace('\\', ''))
        message_id = sended_message_json['id']

        if delete:
            if random_delete:
                if random.randint(0, 1) == 0:
                    requests.delete(f'https://discord.com/api/v{api_version}/channels/{channel_ID}/messages/{message_id}', headers={'authorization': discord_token})
            else:
                requests.delete(f'https://discord.com/api/v{api_version}/channels/{channel_ID}/messages/{message_id}', headers={'authorization': discord_token})

        if notification:
            notification.notify(message='Сообщение было отправлено.')

        random_time = random.randint(MIN_delay, MAX_delay)
        print('До следующего сообщения: ' + str(random_time) + ' сек.')
        time.sleep(random_time)
    else:
        wait = message_time - time_now + timedelta(minutes=10, seconds=10)
        wait = wait.total_seconds()
        print('Сообщение будет отправлено через: ' + str(round(wait)) + ' сек.')
        time.sleep(wait)