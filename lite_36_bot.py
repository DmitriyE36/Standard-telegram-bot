import logging # 13. стандартный модуль логирования, фиксирует все возникающие в боте исключения
import structlog # 15. библиотека для удобной работы с логами (фиксируется время и дата системного сообщения)
import ephem # 24. Ипортируем модуль астрономии ephem(промежуточная задача). Добавим в бота блок по определению местоположения планет на сегодняшнюю дату
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import date, datetime # 27. из модуля datetime импортируем класс date, чтобы получить сегодняшнюю дату для блока ephem. Импортируем класс datetime для рпеобразования даты из строки в блоке next_full_moon
import re # 37. Импортируем модуль re для работы с регулярными выражениями (блок user_calculator)
from random import randint, choice # 40. для игры в числа импортируем функцию randint для генерации целых чисел (int)
# 45. для функции send_cat_picture импортируем модуль choice из библиотеки random, позволяет выдавать рандомный элемент из заданного списка
from glob import glob # 44. импортируем модуль glob для поиска файлов в заданной папке по определенному шаблону 
import settings # 3. импортируем данные из файла settings.py, создаем его для хранения персональных настроек бота (токен, прокси и др.), настройки хранятся в виде переменных, файл вносим в gitignore, чтобы не загружать на git hub
from cities_play import cities # 34. импортируем данные из файла cities_play(список городов)
# 1. импортируем коммуникатор - Updater
# 7. импортируем обработчик команд - CommandHandler
# 18. импортируем обработчик сообщений и библиотеку с фильтрами по типу входящих данных - MessageHandler и Filters

logging.basicConfig(level=logging.INFO) # 14. прописываем перехват системных сообщений и выводим их сразу в консоль, устанавливаем сообщения с уровня INFO
logger = structlog.getLogger() # 16. заменяем стандартный модуль логирования на библиотеку structlog, результат кладем в переменную

def greet_user(update, context): # 10. cоздаем функцию для приветсятвия пользователя, при нажатии /start, аргументы update, context в данном случае const
    logger.debug('Вызвана команда "старт"') # 11. выводим в консоль, что поступила команда /start (впоследствии изменияем на debug-сообщение в консоль)
    update.message.reply_text('Привет, Пользователь! Ты вызвал команду /start') # 12. ответить пользователю

def talk_to_me(update, context): # 20. создаем функцию для работы с текстовыми сообщениями пользователя
    text = update.message.text # 21. сообщения пользователя поступают в директорию update.message.text, кладем результат в переменную, для дальнейшего удобства работы
    logger.debug(text) # 22. выводим сообщение пользователя в консоль
    update.message.reply_text(text) # 23. Отвечаем пользователю

def play_random_numbers(user_number): # 41 создаем отдельно функцию, которая будет генерировать случайно число и сравнивать его с числом из функции guess_number
    bot_number = randint(user_number - 10, user_number + 10) # randint принимает два аргумента, нижняя и верхняя граница генерируемых чисел, в данном случае отталкиваемся от числа пользователя
    if user_number > bot_number: # прописываем логику игры
        message = f'Ваше число {user_number}, мое {bot_number}, вы выиграли'
    elif user_number == bot_number:
        message = f'Ваше число {user_number}, мое {bot_number}, ничья'
    else:
        message = f'Ваше число {user_number}, мое {bot_number}, вы проиграли'
    return message

def guess_number(update, context): # 39. создаем функцию для игры в числа
    logger.debug(context.args)
    if context.args: # context.args это аргументы, которые следуют после комманды, в данном случае проверяем их наличие через if-конструкцию
        try: # обрабатываем исключение в том случае, если пользователь после команды ввел не число, а любое другое значение
            user_number = int(context.args[0]) # забираем первое значение которое ввел пользователь после команды и преобразуем его из строки в целое число
            message = play_random_numbers(user_number) # 42. в переменную кладем результат выполнения функции с аргументом user_number
        except(TypeError, ValueError):
            message = 'Введите целое число'
    else:
        message = 'Введите число'
    update.message.reply_text(message) # отправляем сообщение пользователю в зависимости от отработки логики if

def my_planet(update, context): # 26. (далее по функции) создадим функцию для команды \planet, которая возвращает пользователю созвездие, в котором находится выбранная им планета
    try:
        logger.debug('Вызвана команда "planet"') # выводим в консоль
        user_text = update.message.text.split() # c помощью команды split разбиваем строку на элементы и создаем список, где планета - второй элемент
        user_planet = user_text[1].lower().capitalize() # приводим название планеты к нужному формату
        logger.debug(user_planet)
        planet_atr = getattr(ephem, user_planet) #(заменяет ephem.Mars, ephem.Moon) метод getattr позволяет нам получить значение атрибута(в данном случае название планеты) из объекта(класса) ephem
        day = date.today() # сегодняшная дата
        planet_loc = planet_atr(day) # положение планеты
        const = ephem.constellation(planet_loc) # созвездие
        logger.debug(const)
        update.message.reply_text(f'Сегодня {day}, планета {user_planet} находится в созвездии {const}') # вывод результата пользователю
    except(AttributeError):
        update.message.reply_text('Введите название другой планеты') # обходим исключение, если пользовательно ошибся в названии планеты

def user_wordcount(update, context): # 29. создаем функцию, которая при вводе команды \wordcount считает слова, введенные пользователем и возвращает их количество
    logger.debug('Вызвана команда "wordcount"')
    user_words = update.message.text.split()
    del user_words[0] # убираем команду из списка введенных слов
    logger.debug(user_words)
    if len(user_words) == 0: # проверяем на пустую строку
        update.message.reply_text('Введите хотя бы одно слово')
    elif user_words[0].lstrip('-+').isdigit(): # проверяем на цифры
        update.message.reply_text('Это цифра, введите слово')
    else:
        update.message.reply_text(f'{len(user_words)} слова')

def user_full_moon(update, context): # 31. создаем функцию, которая при вводе команды next_fool_moon и даты выдает пользователю ближайшую дату полнолуния 
    try:
        logger.debug('Вызвана команда "next_full_moon"')
        user_text = update.message.text.split()
        del user_text[0] # убираем из полученного списка команду
        logger.debug(user_text)
        user_date = datetime.strptime(user_text[0], '%Y-%m-%d') # извлекаем из строки объект даты
        logger.debug(user_date)
        full_moon = ephem.next_full_moon(user_date) # определяем ближайшее полнолуние с помощью библиотеки ephem
        update.message.reply_text(f'Ближайшее полнолуние наступит {full_moon}')
    except(ValueError): # обрабатываем исключение, если пользователь ввел не дату, а совсем другое значение или дату в другом формате
        update.message.reply_text('Введите дату в формате гггг-мм-дд')

def play_cities(update, context): # 33. Создаем фунцию для игры в города при вызове команды \cities
    logger.debug('Вызвана команда "cities"')
    user_text = update.message.text.split()
    user_city = user_text[1].lower().capitalize()
    logger.debug(user_city)
    if user_city in cities:
        cities.remove(user_city) # удаляем город, введенный пользователем, из списка
        bot_city = [ city for city in cities if city.lower().startswith(user_city[-1])] # создаем список городов, которые начинаются на последнюю букву города, введенного пользователем
        logger.debug(bot_city)
        update.message.reply_text(f'{bot_city[0]}, Ваш ход') # отдаем пользователю первый город из списка
        cities.remove(bot_city[0])      
    else:
        update.message.reply_text('Введите другой город')

def user_calculator(update, context): # 36. Создаем функцию для простого калькулятора, который выполняет сложение, вычитание, умножение, деление двух чисел введенных пользователем
    logger.debug('Вызвана команда "calc"')
    user_text = update.message.text.split()
    del user_text[0]
    expression = ' '.join(user_text) # собираем элементы списка в строку
    logger.debug(expression)
    pattern = r"(\s?)(\-?\d+[\.|,]?\d*?)(\s?)([\+\-\*\/])(\s?)(\d+[\.|,]?\d*?)$(\s?)" # составляем шаблон регулярного выражения для поиска в строке математического выражения 
    match = re.search(pattern, expression) # c помощью метода search находим по шаблону выражение в строке
    logger.debug(match)
    try:
        if match:
            a = float(match.group(2).replace(',', '.')) # с помощью метода group достаем из полученного выражения переменные и оператор математического действия
            logger.debug(a)
            b = float(match.group(6).replace(',', '.'))
            logger.debug(b)
            operator = match.group(4)
            logger.debug(operator)
            if operator == '+': # прописываем логику действия программы в зависимости от оператора в выражении
                update.message.reply_text(f'Результат вашего выражения = {a + b}')
            elif operator == '-':
                update.message.reply_text(f'Результат вашего выражения = {a - b}')
            elif operator == '*':
                update.message.reply_text(f'Результат вашего выражения = {round(a * b, 2)}')
            elif operator == '/':
                update.message.reply_text(f'Результат вашего выражения = {round(a / b, 2)}')
        else:
            update.message.reply_text("Вы не ввели числа или ввели неправильно")
    except ZeroDivisionError: # прописываем обработку исключения при делении на 0
        update.message.reply_text('Деление на 0 невозможно')

def send_cat_picture(update, context): # 43. Создаем функцию, которая при поступлении команды cat будет выдавать случайнвм образом из папки images файлы jpg или jpeg, начинающиеся с "cat" 
    cat_photo_list = glob('images/cat*.jp*g') # с помощью модуля  glob формируем список из картинок в папке images c с расширением jpg или jpeg, которые начинаются на cat. * - заменяет любые символы или их отсутствие
    cat_pic_filename = choice(cat_photo_list) # выьираем рандомно элемент из заданного списка (в данном случае картинку)
    chat_id = update.effective_chat.id # из update получаем id чата с текущим пользователем
    context.bot.send_photo(chat_id=chat_id, photo=open(cat_pic_filename, 'rb')) # команда отправки в текущий чат картинки, имеет 2 аргумента - id чата и photo(указываем какой файл открываем и признак 'rb'-открытие бинарных файлов)

def main(): # 2. создаем функцию без аргументов для тела бота
    mybot = Updater(settings.API_KEY, use_context=True) # 3. в переменную помещаем коммуникатор, в котором указываем токен бота (переменную из файла settings.py), и второй параметр (const), возможно уже не нужен
    
    dp = mybot.dispatcher # 8. прописываем диспетчер для приема комманд боту, кладем для удобства в переменную
    dp.add_handler(CommandHandler('start', greet_user)) # 9. связываем обработчик команд с диспетчером, в зависимости от команды, переданной боту, обработчик будет вызывать соответствующую функцию, прописываем их в этой строчке
    dp.add_handler(CommandHandler('guess', guess_number)) # 38. обрабатываем команду guess для запуска функции guess_number
    dp.add_handler(CommandHandler('planet', my_planet)) # 25. связываем обработчик команд с диспетчером для обработки команды \planet. Функцию my_planet прописываем также в обработчике сообщений, так как будем отвечать пользователю на его текст
    dp.add_handler(CommandHandler('wordcount', user_wordcount)) # 28. обрабатываем команду /wordcount, которая запускает функцию user_wordcount
    dp.add_handler(CommandHandler('next_full_moon', user_full_moon)) # 30. Обрабатываем команду /next_full_time для запуска функции user_fool_moon
    dp.add_handler(CommandHandler('cities', play_cities)) # 32. Обрабатываем команду /cities для запуска функции play_cities
    dp.add_handler(CommandHandler('calc', user_calculator)) # 35. Обрабатываем команду /calc для запуска функции user_calculator
    dp.add_handler(CommandHandler('cat', send_cat_picture)) # 42. добавляем команду "cat"
    dp.add_handler(MessageHandler(Filters.text, talk_to_me)) # 19. связываем обработчик сообщений с диспетчером, для вызова функции при поступлении запроса пользователя, бот будет принимать только текстовые сообщения (прописываем в параметрах с помощью библиотеки Filters)
    ### MessageHandler должен всегда находиться ниже других обработчиков при написании кода ###
    ### Обрабатывает в данном случае текстовые сообщения пользователя, введенные без команды ###
    logger.info('Бот стартовал') # 17. Добовляем в логи информационное сообщение о старте бота
    mybot.start_polling() # 4. связь с сервером ТГ
    mybot.idle() # 5. постоянная работа бота

if __name__ == '__main__': # 6. данное условие позволить при импорте из данного файла не запустить функцию
    main() # 6 тело простого бота готово, вызываем функцию