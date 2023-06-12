import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import comunity_token, access_token, db_url_object
from core import VkTools
from data_store import add_user, check_user
from sqlalchemy import create_engine

class BotInterface:
    def __init__(self, comunity_token, acces_token):
        self.interface = vk_api.VkApi(token=comunity_token)
        self.vk_tools = VkTools(access_token)
        self.api = VkTools(acces_token)
        self.params = None
        self.worksheets = []
        self.offset = 0

    def message_send(self, user_id, message, attachment=None):
        self.interface.method('messages.send',
                       {'user_id': user_id,
                        'message': message,
                        'attachment': attachment,
                        'random_id': get_random_id()}
                       )

    def event_handler(self):
        longpoll = VkLongPoll(self.interface)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                command = event.text.lower()
                if command == 'привет':
                    self.params = self.api.get_profile_info(event.user_id)
                    self.message_send(event.user_id, f'Здравствуй {self.params["name"]}')
                    self.message_send(event.user_id, 'Проверка данных...')
                    if not self.params['city'] or not self.params['sex'] or not self.params['bdate'] or not self.params['relation']:
                        if not self.params['city']:
                            self.message_send(event.user_id, f"{self.params['name']}, введите ваш город")
                            self.params['city'] = command.capitalize()
                        elif self.params['city']:
                            self.message_send(event.user_id, f"{self.params['name']}, у Вас уже введён город")
                        if not self.params['sex']:
                            self.message_send(event.user_id, f"{self.params['name']}, введите Ваш пол")
                            self.params['sex'] = int(command)
                        elif self.params['sex']:
                            self.message_send(event.user_id, f"{self.params['name']}, у Вас уже введён пол")
                        if not self.params['bdate']:
                            self.message_send(event.user_id, f"{self.params['name']}, введите Вашу дату рождения")
                            self.params['bdate'] = command
                        elif self.params['bdate']:
                            self.message_send(event.user_id, f"{self.params['name']}, у Вас уже введена дата рождения")
                        if not self.params['relation']:
                            self.message_send(event.user_id, f"{self.params['name']}, введите ваш город")
                            self.params['relation'] = int(command)
                        elif self.params['relation']:
                            self.message_send(event.user_id, f"{self.params['name']}, у Вас уже введенно семейное положение")
                    else:
                        self.message_send(event.user_id, f"{self.params['name']}, у Вас все данные!")
                elif command == 'поиск':
                    self.message_send(
                        event.user_id, 'Начинаем поиск')
                    if self.worksheets:
                        worksheet = self.worksheets.pop()
                        photos = self.vk_tools.get_photos(worksheet['id'])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}{photo["id"]}'
                    else:
                        self.worksheets = self.vk_tools.search_worksheet(
                            self.params, self.offset)
                        worksheet = self.worksheets.pop()
                        photos = self.vk_tools.get_photos(worksheet['id'])
                        photo_string = ''
                        for photo in photos:
                            photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
                        self.offset += 10
                    self.message_send(
                        event.user_id,
                        f'имя: {worksheet["name"]} ссылка: vk.com/{worksheet["id"]}',
                        attachment=photo_string
                    )
                    if not check_user(engine, event.user_id, worksheet["id"]):
                        add_user(engine, event.user_id, worksheet["id"])
                elif command == 'пока':
                    self.message_send(event.user_id, 'До новых встреч')
                else:
                    self.message_send(event.user_id, 'Вы ввели неизвестную команду')

if __name__ == '__main__':
    engine = create_engine(db_url_object)
    bot_interface = BotInterface(comunity_token, access_token)
    bot_interface.event_handler()

