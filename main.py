import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp
from json import loads as jsd

logging.basicConfig(level=logging.INFO)

bot = Bot(token="7964695569:AAEFo8LpkAF6dueaHGCUky_SikTzXngSmls", default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply("<b>👋 Привет!</b>\n\nЭтот бот позволяет выводить цвет, его базовую информацию и представление в других системах в чат.\n\n<code>@colorpreviewbot #f9d509</code>\n\n")

async def areq(hex):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://www.thecolorapi.com/id?hex={hex}') as resp: # Getting info from API
            return await resp.text() # Returning info back to getcolorinfo()

def getcolorinfo(hex):
    js = areq(hex)
    js = jsd(js) # Decoding JSON response

    name = js['name']['value']
    named = js['name']['exact_match_name']
    closestnamed = js['name']['closest_named_hex']
    rgb = js['rgb']['value']
    hsv = js['hsv']['value']
    hsl = js['hsl']['value']
    cmyk = js['cmyk']['value']

    return [name, named, closestnamed, rgb, hsv, hsl, cmyk] # Packing and returning info to inline query handler

@dp.inline_query()
async def inline_echo(query: types.InlineQuery):
    query_text = query.query
    if len(query_text) != 0 and query_text[0] == "#" and len(query_text) == 7:
        querynojail = query_text[1:]
        pkg = getcolorinfo(querynojail)
        name = pkg[0]
        named = pkg[1]
        closestnamed = pkg[2]
        rgb = pkg[3]
        hsv = pkg[4]
        hsl = pkg[5]
        cmyk = pkg[6] # Unpacking (yes, shitcode)

        if named == True:
            named = "да"
        elif named == False:
            named = f"нет, ближайший именованный - {closestnamed}"
        
        title = f"🎨 Информация о цвете {query_text}"

        response = f"<b>🎨 Информация о цвете {query_text}</b>\n\nИмя: {name}\nЦвет соответствует имени: {named}\n\nRGB: <code>{rgb}</code>\nHSV: <code>{hsv}</code>\nHSL: <code>{hsl}</code>\nCMYK: <code>{cmyk}</code>"
    else:
        response = f"<b>😓 Неподдерживаемый или некорректный цвет</b>"
        title = "😓 Неподдерживаемый или некорректный цвет"

    result = types.InlineQueryResultArticle(
        id=query.id,
        title=title,
        input_message_content=types.InputTextMessageContent(message_text=response)
    )
    
    # Sending answer to user
    await bot.answer_inline_query(query.id, results=[result])

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())