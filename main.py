from datetime import datetime, timedelta
from discum import Client
from json import loads
from random import randint, SystemRandom
from time import sleep
from pytz import timezone

bot = Client(token=input('Введите Ваш Discord-token: '))
channel_ID = input('Введите ID канала для отправки: ')
warp_names = input('Введите название рекламируемого Вами варпа (можно ввести несколько названий через ; ): ')
warp_names = warp_names.split(';')
MIN_delay = input('Введите минималый промежуток для отправки (в минутах): ')
MIN_delay = int(MIN_delay) * 60
MAX_delay = input('Введите максимальный промежуток для отправки (в минутах): ')
MAX_delay = int(MAX_delay) * 60 
advertisements = input('Введите рекламу (можно ввести несколько текстов через ; ): ')
advertisements = advertisements.split(';')

def send_message():
    sended_message = bot.sendMessage(channelID=channel_ID, message=SystemRandom().choice(advertisements))
    sended_message = sended_message.text.encode().decode('unicode-escape')
    sended_message_json = loads(sended_message.replace('\\', ''))

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
