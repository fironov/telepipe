import asyncio
import os
from io import BytesIO

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiohttp import ClientSession, FormData
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set. Check bot/.env")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def handle_start(message: Message) -> None:
    await message.answer("Отправь мне видео или файл, я сохраню его в медиатеке.")


def _resolve_filename(message: Message, fallback: str) -> str:
    if message.document and message.document.file_name:
        return message.document.file_name
    if message.video and message.video.file_name:
        return message.video.file_name
    return f"{fallback}.mp4"


def _resolve_mime_type(message: Message) -> str:
    if message.document and message.document.mime_type:
        return message.document.mime_type
    if message.video and message.video.mime_type:
        return message.video.mime_type
    return "video/mp4"


async def _upload_to_backend(
    file_bytes: bytes,
    filename: str,
    title: str | None,
    content_type: str,
) -> str:
    async with ClientSession() as session:
        form = FormData()
        if title:
            form.add_field("title", title)
        form.add_field("file", file_bytes, filename=filename, content_type=content_type)
        async with session.post(f"{BACKEND_URL}/upload", data=form) as response:
            if response.status != 201:
                detail = await response.text()
                raise RuntimeError(f"Backend error: {response.status} {detail}")
            payload = await response.json()
            return str(payload.get("id"))


@dp.message(F.video | F.document)
async def handle_media(message: Message) -> None:
    file_id = message.video.file_id if message.video else message.document.file_id

    # Получаем актуальный file_path через getFile при каждом сообщении
    telegram_file = await bot.get_file(file_id)
    file_stream: BytesIO = await bot.download_file(telegram_file.file_path)
    file_stream.seek(0)

    filename = _resolve_filename(message, file_id)
    title = message.caption or filename
    mime_type = _resolve_mime_type(message)

    try:
        video_id = await _upload_to_backend(file_stream.read(), filename, title, mime_type)
    except Exception as exc:
        await message.answer(f"Не удалось сохранить файл: {exc}")
        return

    await message.answer(f"Видео сохранено! ID: {video_id}")


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
