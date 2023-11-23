import logging # 13. стандартный модуль логирования, фиксирует все возникающие в боте исключения
import structlog # 15. библиотека для удобной работы с логами (фиксируется время и дата системного сообщения)
import ephem # 24. Ипортируем модуль астрономии ephem(промежуточная задача). Добавим в бота блок по определению местоположения планет на сегодняшнюю дату
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import date # 27. из модуля datetime импортируем класс date, чтобы получить сегодняшнюю дату для блока ephem
import settings # 3. импортируем данные из файла settings.py, создаем его для хранения персональных настроек бота (токен, прокси и др.), настройки хранятся в виде переменных, файл вносим в gitignore, чтобы не загружать на git hub
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

def main(): # 2. создаем функцию без аргументов для тела бота
    mybot = Updater(settings.API_KEY, use_context=True) # 3. в переменную помещаем коммуникатор, в котором указываем токен бота (переменную из файла settings.py), и второй параметр (const), возможно уже не нужен
    
    dp = mybot.dispatcher # 8. прописываем диспетчер для приема комманд боту, кладем для удобства в переменную
    dp.add_handler(CommandHandler('start', greet_user)) # 9. связываем обработчик команд с диспетчером, в зависимости от команды, переданной боту, обработчик будет вызывать соответствующую функцию, прописываем их в этой строчке
    dp.add_handler(CommandHandler('planet', my_planet)) # 25. связываем обработчик команд с диспетчером для обработки команды \planet. Функцию my_planet прописываем также в обработчике сообщений, так как будем отвечать пользователю на его текст
    dp.add_handler(CommandHandler('wordcount', user_wordcount)) # 28. обрабатываем команду /wordcount, которая запускает функцию user_wordcount
    dp.add_handler(MessageHandler(Filters.text, talk_to_me, my_planet, user_wordcount)) # 19. связываем обработчик сообщений с диспетчером, для вызова функции при поступлении запроса пользователя, бот будет принимать только текстовые сообщения (прописываем в параметрах с помощью библиотеки Filters)
    ### MessageHandler должен всегда находиться ниже других обработчиков при написании кода ###
    
    logger.info('Бот стартовал') # 17. Добовляем в логи информационное сообщение о старте бота
    mybot.start_polling() # 4. связь с сервером ТГ
    mybot.idle() # 5. постоянная работа бота

if __name__ == '__main__': # 6. данное условие позволить при импорте из данного файла не запустить функцию
    main() # 6 тело простого бота готово, вызываем функцию