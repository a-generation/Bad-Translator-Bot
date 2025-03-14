import re
import logging
from aiogram import types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from states import TranslationState
from translator import wrong_translator
from aiogram import F

def register_handlers(dp, bot):  # Добавляем параметр bot
    @dp.message(Command("start"))
    async def start(message: types.Message, state: FSMContext):
        """Стартовое сообщение"""
        await message.answer("👋 Привет! Отправь мне текст, и я переведу его случайным образом!")
        await state.set_state(TranslationState.waiting_for_text)

    @dp.message(TranslationState.waiting_for_text)
    async def get_text(message: types.Message, state: FSMContext):
        """Получаем текст от пользователя"""
        await state.update_data(text=message.text)
        await message.answer("🔢 Введи количество переводов (например, 5):")
        await state.set_state(TranslationState.waiting_for_iterations)

    @dp.message(Command("translate"))
    async def translate_in_group(message: types.Message, state: FSMContext):
        """Перевод в группе с синтаксисом: /translate <колво переводов> "текст" """
        match = re.match(r"/translate (\d+) \"(.+)\"", message.text)
        
        if not match:
            await message.answer("❌ Неверный формат! Используй так:\n`/translate 5 \"Привет, мир!\"`", parse_mode="Markdown")
            return
        
        iterations = int(match.group(1))
        text = match.group(2)

        if iterations < 1:
            await message.answer("❌ Количество переводов должно быть больше 0!")
            return
        
        await message.answer("⏳ Перевожу...")

        final_text, used_languages = wrong_translator(text, iterations)
        lang_list = ", ".join(used_languages)

        await message.answer(
            f"📜 <b>Исходный текст:</b>\n<code>{text}</code>\n\n"
            f"🔢 <b>Количество переводов:</b> {iterations}\n\n"
            f"🌍 <b>Текст проходил через языки:</b> {lang_list}\n\n"
            f"🔄 <b>Финальный результат:</b>\n<code>{final_text}</code>",
            parse_mode="HTML"
        )

    @dp.message(TranslationState.waiting_for_iterations, F.text.isdigit())
    async def get_iterations(message: types.Message, state: FSMContext):
        """Обрабатываем число итераций"""
        iterations = int(message.text)
        if iterations < 1:
            await message.answer("❌ Число должно быть больше 0!")
            return

        await state.update_data(iterations=iterations)
        user_data = await state.get_data()
        text = user_data["text"]

        await message.answer("⏳ Перевожу...")

        final_text, used_languages = wrong_translator(text, iterations)
        lang_list = ", ".join(used_languages)

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Ещё раз", callback_data="again")],
            [InlineKeyboardButton(text="🎲 Новая генерация", callback_data="new")]
        ])

        await message.answer(
            f"📜 <b>Исходный текст:</b>\n<code>{text}</code>\n\n"
            f"🔢 <b>Количество переводов:</b> {iterations}\n\n"
            f"🌍 <b>Текст проходил через языки:</b> {lang_list}\n\n"
            f"🔄 <b>Финальный результат:</b>\n<code>{final_text}</code>",
            reply_markup=kb
        )
        
        await state.set_state(TranslationState.ready_for_repeat)

    @dp.callback_query(lambda c: c.data == "again")
    async def repeat_translation(callback_query: types.CallbackQuery, state: FSMContext):
        """Повторный перевод с теми же параметрами"""
        user_data = await state.get_data()
        
        if not user_data or "text" not in user_data or "iterations" not in user_data:
            await callback_query.message.answer("❌ Нет данных, отправь новый текст!")
            await state.set_state(TranslationState.waiting_for_text)
            return

        text = user_data["text"]
        iterations = user_data["iterations"]

        await bot.send_message(callback_query.message.chat.id, "⏳ Перевожу снова...")

        final_text, used_languages = wrong_translator(text, iterations)
        lang_list = ", ".join(used_languages)

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Ещё раз", callback_data="again")],
            [InlineKeyboardButton(text="🎲 Новая генерация", callback_data="new")]
        ])

        await bot.send_message(
            callback_query.message.chat.id,
            f"📜 <b>Исходный текст:</b>\n<code>{text}</code>\n\n"
            f"🔢 <b>Количество переводов:</b> {iterations}\n\n"
            f"🌍 <b>Текст проходил через языки:</b> {lang_list}\n\n"
            f"🔄 <b>Финальный результат:</b>\n<code>{final_text}</code>",
            reply_markup=kb
        )

    @dp.callback_query(lambda c: c.data == "new")
    async def new_translation(callback_query: types.CallbackQuery, state: FSMContext):
        """Запрос нового текста"""
        await state.set_state(TranslationState.waiting_for_text)
        await bot.send_message(callback_query.message.chat.id, "✍️ Отправь новый текст!")