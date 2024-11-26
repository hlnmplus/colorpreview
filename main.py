import asyncio
import logging
import colorsutils as c
from colorsys import rgb_to_hls, rgb_to_hsv
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from credentials import token

logging.basicConfig(level=logging.INFO)

bot = Bot(token=token, default=DefaultBotProperties(parse_mode = ParseMode.HTML))
dp = Dispatcher()

template = """
<a href = "https://singlecolorimage.com/get/{}/400x100">🎨</a><b> Информация о цвете {}</b>

<b>Имя</b>: {}
<b>Цвет соответствует имени</b>: {}

<b>HEX</b>: <code>{}</code>
<b>RGB</b>: <code>rgb{}</code>
<b>HSV</b>: <code>hsv{}</code>
<b>HSL</b>: <code>hsl{}</code>
<b>CMYK</b>: <code>cmyk{}</code>
"""

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply("""<b>👋 Привет!</b>
   
Этот бот позволяет выводить цвет, его базовую информацию и представление в других системах в чат.

<code>@colorpreviewbot ff7538</code>
Так же, Вы можете использовать формат RGB в качестве входной:
<code>@colorpreviewbot 255 117 56</code>
Или просто по названию цвета:
<code>@colorpreviewbot Orange</code>
     
Бот имеет <a href = 'https://github.com/hlnmplus/colorpreview'>открытый исходный код</a>.""", disable_web_page_preview = True)

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
    name = c.nearestcolor(color)

    if name[1] == 0:
        named = "да"
    else:
        named = f"нет, ближайший именованный - {c.hexbycolorname(name[0])}"
    
    name = name[0]

    rgb = c.hex2rgb(color)
    hsv = rgb_to_hsv(rgb[0], rgb[1], rgb[2])
    hls = rgb_to_hls(rgb[0], rgb[1], rgb[2])
    cmyk = c.rgb2cmyk(rgb[0], rgb[1], rgb[2])

    newhsv = []
    newhls = []
    newcmyk = []

    for i in range(len(hsv)):
        newhsv.append(round(hsv[i], 2))

    for i in range(len(hls)):
        newhls.append(round(hls[i], 2))
    
    for i in range(len(cmyk)):
        newcmyk.append(round(cmyk[i], 2))

    hsv = f"({newhsv[0]}, {newhsv[1]}, {newhsv[2]})"
    hsl = f"({newhls[0]}, {newhls[2]}%, {newhls[1]}%)"
    cmyk = f"({newcmyk[0]}%, {newcmyk[1]}%, {newcmyk[2]}%, {newcmyk[3]}%)"

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
    elif query_text in c.db.keys():
        color = c.hexbycolorname(query_text)
        title = f"🎨 Информация о цвете {query_text}"
        response = await makeresponse(color, query_text)
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
