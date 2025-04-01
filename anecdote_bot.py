import os
import random
import asyncio
import logging
from telegram import Bot, ChatMember
from telegram.error import TimedOut, NetworkError

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Резервные анекдоты на случай проблем с файлом
DEFAULT_ANECDOTES = [
    "Анекдот 1: Шла бабка через болото...",
    "Анекдот 2: Встречаются два друга...",
    "Анекдот 3: Заходит мужик в бар..."
]

# Настройки
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
ANEC_DOT_FILE = 'anekdots.txt'  # Относительный путь к файлу с анекдотами
POSTS_PER_DAY = 10  # Количество анекдотов в день
POST_INTERVAL = 86400 // POSTS_PER_DAY  # Интервал между публикациями (в секундах)

# Проверка переменных окружения
if not TELEGRAM_BOT_TOKEN or not CHANNEL_ID:
    logging.error("Ошибка: не установлены переменные окружения TELEGRAM_BOT_TOKEN или CHANNEL_ID.")
    exit(1)

# Чтение анекдотов из файла
def load_anecdotes(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        # Разделяем анекдоты по двойным переносам строк (пустым строкам)
        return [a.strip() for a in content.split('\n\n') if a.strip()]
    except FileNotFoundError:
        logging.warning(f"Файл '{file_path}' не найден. Использую резервные анекдоты.")
        return DEFAULT_ANECDOTES
    except Exception as e:
        logging.error(f"Ошибка при чтении файла: {e}")
        return DEFAULT_ANECDOTES

# Проверка прав бота
async def check_bot_permissions(bot, channel_id):
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=bot.id)
        if member.status != ChatMember.ADMINISTRATOR:
            logging.error("Бот не является администратором канала.")
            exit(1)
    except Exception as e:
        logging.error(f"Ошибка при проверке прав бота: {e}")
        exit(1)

# Асинхронная публикация анекдотов
async def post_anecdotes(bot, channel_id, anecdotes):
    while True:
        random.shuffle(anecdotes)  # Перемешиваем анекдоты
        for i in range(POSTS_PER_DAY):
            anecdote = anecdotes[i % len(anecdotes)]  # Берем анекдот по кругу
            try:
                await bot.send_message(chat_id=channel_id, text=anecdote)  # Асинхронная отправка
                logging.info(f"Опубликован анекдот: {anecdote}")
            except TimedOut:
                logging.warning("Ошибка: превышено время ожидания. Повторная попытка...")
            except NetworkError as e:
                logging.error(f"Сетевая ошибка: {e}. Повторная попытка...")
            except Exception as e:
                logging.error(f"Неизвестная ошибка: {e}")
            finally:
                await asyncio.sleep(POST_INTERVAL)  # Ждем перед следующей публикацией

# Основная функция
async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Инициализация бота
    try:
        await bot.initialize()
        logging.info("Бот успешно инициализирован.")
    except Exception as e:
        logging.error(f"Ошибка при инициализации бота: {e}")
        exit(1)

    # Проверяем права бота
    await check_bot_permissions(bot, CHANNEL_ID)

    # Загружаем анекдоты
    anecdotes = load_anecdotes(ANEC_DOT_FILE)

    logging.info("Бот запущен. Начинаю публикацию анекдотов...")
    await post_anecdotes(bot, CHANNEL_ID, anecdotes)

# Точка входа
if __name__ == "__main__":
    asyncio.run(main())
