import json
import discum
import time
from datetime import datetime, timedelta
import random
import pytz
import config

class Post:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read_file(open(r'config.ini'))
        save = eval(config.get('Config', 'save'))
        
        if save:
            load = input('Загрузить последнюю конфигурацию? (да/нет): ')
            if load == 'да':
                self.discord_token = config.get('Config', 'discord_token')
                self.bot = discum.Client(token=self.discord_token)
                self.channel_ID = config.get('Config', 'channel_ID')
                self.warp_name = config.get('Config', 'warp_name')
                self.MIN_delay = config.get('Config', 'MIN_delay')
                self.MAX_delay = config.get('Config', 'MAX_delay')
                self.advertisements = config.get('Config', 'advertisements')
            elif load == 'нет':
                self.new_config()
            else:
                print('Неизвестное значение.')
        else:
            self.new_config()

        while True:
                last_message_id = None
                messages = self.bot.getMessages(channelID=self.channel_ID, num=100, beforeDate=last_message_id)
                messages = messages.text
                messages = messages.replace('\\n', '')
                messages = messages.replace('\\"', '')
                messages = messages.encode().decode("unicode-escape")
                messages = messages.replace('\\', '')

                messages = json.loads(messages)

                message_founded = False
                for j in messages:
                    if not message_founded: 
                        if j['author'].get('id') == '618536577282342912':
                            content = j['content']
                            if content.find(self.warp_name) != -1:
                                print(content.find(self.warp_name))
                                message_founded = True
                                message_timestamp = j['timestamp']
                    last_message_id = j['id']

                if message_founded:
                    message_founded = False
                    last_message_id = None

                    message_time = datetime.strptime(message_timestamp, '%Y-%m-%dT%H:%M:%S.%f+00:00')
                    
                    timezone = pytz.timezone('Europe/Moscow')
                    time_now = datetime.now(timezone)
                    time_now = time_now - timedelta(hours=3)
                    time_now = time_now.replace(tzinfo=None)
                    
                    if message_time < time_now - timedelta(minutes=10):
                        sended_message = self.bot.sendMessage(channelID=self.channel_ID, message=random.SystemRandom().choice(self.advertisements))
                        sended_message = sended_message.text.encode().decode('unicode-escape')
                        
                        time.sleep(10)
                        sended_message_json = json.loads(sended_message.replace('\\', ''))
                        self.bot.deleteMessage(channelID=self.channel_ID, messageID=sended_message_json['id'])
                        time.sleep(600)
                    else:
                        wait = message_time - time_now + timedelta(minutes=10)
                        time.sleep(wait.total_seconds())
                        time.sleep(random.randint(self.MIN_delay, self.MAX_delay))

                else:
                    time.sleep(1)

    def new_config(self):
        save = input('Сохранить конфигурацию? (да/нет): ')
        if save == 'да':
            self.save = True
        elif save == 'нет':
            self.save = False
        else:
            print('Незивестное значение.')

        self.discord_token = input('Введите Ваш Discord-token: ')
        self.bot = discum.Client(token=self.discord_token)
        self.channel_ID = input('Введите ID канала для отправки: ')
        self.warp_name = input('Введите название рекламируемого Вами варпа: ')
        MIN_delay = input('Введите минималый промежуток для отправки (в минутах): ')
        self.MIN_delay = int(MIN_delay) * 60
        MAX_delay = input('Введите максимальный промежуток для отправки (в минутах): ')
        self.MAX_delay = int(MAX_delay) * 60 
        advertisements = input('Введите рекламу (можно ввести несколько текстов через ; ): ')
        self.advertisements = advertisements.split(';')

        if self.save:
            self.save_config()

    def save_config(self):
        config = configparser.ConfigParser()
        config.add_section('Config')
        config.set('Config', 'save', str(self.save))
        config.set('Config', 'discord_token', self.discord_token)
        config.set('Config', 'channel_ID', self.channel_ID)
        config.set('Config', 'warp_name', self.warp_name)
        config.set('Config', 'MIN_delay', str(self.MIN_delay))
        config.set('Config', 'MAX_delay', str(self.MAX_delay))
        config.set('Config', 'advertisements', str(self.advertisements))

        with open('config.ini', 'w') as config_file:
            config.write(config_file)

Post()