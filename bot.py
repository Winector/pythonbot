from config import TOKEN

import random
import csv
import codecs
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

class GenreFilm(StatesGroup):
    waiting_for_film_genre = State()


async def set_commands(dp):
    commands = [
        types.BotCommand(command="/genre", description="Фильм по жанру"),
        types.BotCommand(command="/randomfilm", description="Случайный фильм"),
        types.BotCommand(command="/cancel", description="Отменить текущее действие")
    ]
    await bot.set_my_commands(commands)


bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


with codecs.open('genres.txt', 'r', 'utf-8') as f:
    genres = f.read().split('\n')


@dp.message_handler(commands=['cancel'], state="*")
async def cancel(message: types.Message, state: FSMContext):
    if state is None:
        return
    await state.finish()
    await message.answer('Действие отменено', reply_markup=types.ReplyKeyboardRemove())



@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer('Привет! Я - Кинобот. Открой меню и посмотри что я могу! Всю информацию я беру отсюда: https://kinoafisha.info')


@dp.message_handler(commands=["randomfilm"])
async def print_randon_film(message: types.Message):
    with codecs.open('films.csv', 'r', 'utf-8') as f:
        reader = csv.DictReader(f)
        films = list(reader)
        film = films[random.randint(0, 999)]
    await message.answer(f"Название: {film['title']}\n"
                         f"Жанр: {film['genres']}\n"
                         f"Год: {film['year']}\n"
                         f"Страна: {film['country']}\n"
                         f"Рейтинг: {film['rating']}\n")


@dp.message_handler(commands=["genre"], state="*")
async def choose_genre(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for genre in genres:
        keyboard.add(genre)
    await message.answer('Выберите жанр из списка', reply_markup=keyboard)
    await state.set_state(GenreFilm.waiting_for_film_genre.state)


@dp.message_handler(state=GenreFilm.waiting_for_film_genre)
async def print_genre_film(message: types.Message, state: FSMContext):
    if message.text.lower() not in genres:
        await message.answer("Пожалуйста, выберите жанр, используя клавиатуру ниже.")
        return
    with codecs.open('films.csv', 'r', 'utf-8') as f:
        reader = csv.DictReader(f)
        films = list(reader)
        for _ in range(999):
            film = films[random.randint(0, 999)]
            if message.text in film['genres'].split(', '):
                await message.answer(f"Название: {film['title']}\n"
                                     f"Жанр: {film['genres']}\n"
                                     f"Год: {film['year']}\n"
                                     f"Страна: {film['country']}\n"
                                     f"Рейтинг: {film['rating']}", reply_markup=types.ReplyKeyboardRemove())
                await state.finish()
                break


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=set_commands)
    