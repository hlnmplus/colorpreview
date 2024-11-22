import asyncio
import logging
import aiohttp
from aiogram import Bot, Dispatcher, types, filters
from aiogram.filters.command import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from json import loads as jsd
from credentials import token

logging.basicConfig(level=logging.INFO)

bot = Bot(token=token, default=DefaultBotProperties(parse_mode = ParseMode.HTML))
dp = Dispatcher()

template = """
<a href = "https://singlecolorimage.com/get/{}/400x100">🎨</a><b> Информация о цвете {}</b>

<b>Имя</b>: {}
<b>Цвет соответствует имени</b>: {}

<b>HEX</b>: <code>{}</code>
<b>RGB</b>: <code>{}</code>
<b>HSV</b>: <code>{}</code>
<b>HSL</b>: <code>{}</code>
<b>CMYK</b>: <code>{}</code>
"""

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply("<b>👋 Привет!</b>\n\nЭтот бот позволяет выводить цвет, его базовую информацию и представление в других системах в чат.\n\n<code>@colorpreviewbot #f9d509</code>\nТак же, вы можете использовать формат RGB в качестве входной\n<code>@colorpreviewbot 249 213 9</code>\n\nБот имеет <a href = 'https://github.com/hlnmplus/colorpreview'>открытый исходный код></a>.", disable_web_page_preview = True)

async def areq(hex):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://www.thecolorapi.com/id?hex={hex}') as resp:
            return await resp.text()

async def getcolorinfo(hex):
    js = await areq(hex)
    js = jsd(js)

    name = js['name']['value']
    named = js['name']['exact_match_name']
    closestnamed = js['name']['closest_named_hex']
    rgb = js['rgb']['value']
    hsv = js['hsv']['value']
    hsl = js['hsl']['value']
    cmyk = js['cmyk']['value']

    return [name, named, closestnamed, rgb, hsv, hsl, cmyk]

def ishex(color):
    if len(color) != 6 or not all(c in "0123456789ABCDEFabcdef" for c in color):
        if len(color[1:]) != 6 or not all(c in "0123456789ABCDEFabcdef" for c in color[1:]):
            return False
        else:
            return True
    else:
        return True

def isnum(num):
    try:
        num = int(num)
        return True
    except ValueError:
        return False

async def makeresponse(color, query_text):
    pkg = await getcolorinfo(color)
    name = pkg[0]
    named = pkg[1]
    closestnamed = pkg[2]
    rgb = pkg[3]
    hsv = pkg[4]
    hsl = pkg[5]
    cmyk = pkg[6]

    if named == True:
        named = "да"
    elif named == False:
        named = f"нет, ближайший именованный - {closestnamed}"

    return template.format(color, query_text, name, named, color, rgb, hsv, hsl, cmyk)

@dp.inline_query()
async def inline(query: types.InlineQuery):
    query_text = query.query
    if ishex(query_text) == True:
        if len(query_text) == 7:
            color = query_text[1:]
        else:
            color = query_text

        title = f"🎨 Информация о цвете {query_text}"
        response = await makeresponse(color, query_text)
    elif (len(query_text.split(' ')) == 3) and all(isnum(c) for c in query_text.split(' ')) and all(int(c) <= 255 for c in query_text.split(' ')) and all(int(c) >= 0 for c in query_text.split(' ')):
        rgb = query_text.split(' ')
        color = '%02x%02x%02x' % (int(rgb[0]), int(rgb[1]), int(rgb[2]))
        if ishex(color) == True:
            response = await makeresponse(color, query_text)
            title = f"🎨 Информация о цвете {query_text}"
        else:
            response = f"<b>😓 Неподдерживаемый или некорректный цвет</b>"
            title = "😓 Неподдерживаемый или некорректный цвет"
    else:
        response = f"<b>😓 Неподдерживаемый или некорректный цвет</b>"
        title = "😓 Неподдерживаемый или некорректный цвет"

    result = types.InlineQueryResultArticle(
        id = query.id,
        title = title,
        input_message_content = types.InputTextMessageContent(message_text=response)
    )

    await bot.answer_inline_query(query.id, results=[result])

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())