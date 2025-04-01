import random
import asyncio
from telegram import Bot
from telegram.error import TimedOut, NetworkError

# Настройки
TELEGRAM_BOT_TOKEN = '7597993035:AAHDu-SSrBqQK_rvokwLikv5L1Vf34llXro'  # Замените на ваш токен
CHANNEL_ID = '@ortxt'  # Замените на имя вашего канала (начинается с @)
ANEC_DOT_FILE = r'anekdots.txt'  # Путь к файлу с анекдотами
POSTS_PER_DAY = 10  # Количество анекдотов в день
POST_INTERVAL = 86400 // POSTS_PER_DAY  # Интервал между публикациями (в секундах)

# Чтение анекдотов из файла
def load_anecdotes(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        # Разделяем анекдоты по двойным переносам строк (пустым строкам)
        anecdotes = content.split('\n\n')
        # Убираем лишние пробелы и пустые строки
        return [a.strip() for a in anecdotes if a.strip()]
    except FileNotFoundError:
        print(f"Ошибка: файл '{file_path}' не найден.")
        exit(1)
    except Exception as e:
        print(f"Произошла ошибка при чтении файла: {e}")
        exit(1)

# Асинхронная публикация анекдотов
async def post_anecdotes(bot, channel_id, anecdotes):
    while True:
        random.shuffle(anecdotes)  # Перемешиваем анекдоты
        for i in range(POSTS_PER_DAY):
            anecdote = anecdotes[i % len(anecdotes)]  # Берем анекдот по кругу
            try:
                await bot.send_message(chat_id=channel_id, text=anecdote)  # Асинхронная отправка
                print(f"Опубликован анекдот: {anecdote}")
            except TimedOut:
                print("Ошибка: превышено время ожидания. Повторная попытка...")
            except NetworkError as e:
                print(f"Сетевая ошибка: {e}. Повторная попытка...")
            except Exception as e:
                print(f"Неизвестная ошибка: {e}")
            finally:
                await asyncio.sleep(POST_INTERVAL)  # Ждем перед следующей публикацией

async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    anecdotes = load_anecdotes(ANEC_DOT_FILE)
    print("Бот запущен. Начинаю публикацию анекдотов...")
    await post_anecdotes(bot, CHANNEL_ID, anecdotes)

if __name__ == "__main__":
    asyncio.run(main())
