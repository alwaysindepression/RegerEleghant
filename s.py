import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# ============================
# Настройки
# ============================

BOT_TOKEN = ""

# Список валидных ключей (можно заменить на БД или файл)
VALID_KEYS = {
    "#GJ437834FD",
    "#AB123456CD",
    "#XY987654ZZ",
    # Добавляй свои ключи сюда
}

# Состояния диалога
WAITING_FOR_KEY = 1

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ============================
# Клавиатура
# ============================

def get_main_keyboard():
    """Главная ReplyKeyboard с кнопкой ввода ключа."""
    keyboard = [["🔐 Ввести ключ"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


# ============================
# Хендлеры
# ============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    await update.message.reply_text(
        "Приветствуем тебя, дорогой пушистик! 🐾\n\n"
        "Следуй инструкции ниже, вводи свой ключ и получай свой товар.",
        reply_markup=get_main_keyboard(),
    )


async def ask_for_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Когда пользователь нажал кнопку '🔐 Ввести ключ'."""
    await update.message.reply_text(
        "🔑 Введи свой ключ активации.\n\n"
        "Ключ должен начинаться с символа *#*\n"
        "Пример: `#GF43ARI83T`",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),  # Убираем клавиатуру пока ждём ввод
    )
    return WAITING_FOR_KEY


async def validate_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Проверка введённого ключа."""
    user_input = update.message.text.strip()

    # Проверяем формат ключа
    if not user_input.startswith("#"):
        await update.message.reply_text(
            "⚠️ Неверный формат ключа!\n\n"
            "Ключ должен начинаться с символа *#*\n"
            "Пример: `#GJ437834FD`\n\n"
            "Попробуй ещё раз:",
            parse_mode="Markdown",
        )
        return WAITING_FOR_KEY  # Остаёмся в том же состоянии

    # Проверяем, существует ли ключ
    if user_input in VALID_KEYS:
        await update.message.reply_text(
            f"✅ Ключ *{user_input}* успешно активирован!\n\n"
            "Введите ваш номер в формате +7999XXXXXXX",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard(),
        )
        # Здесь можно добавить свою логику после активации ключа
        # Например: выдать доступ, записать в БД и т.д.
    else:
        await update.message.reply_text(
            f"❌ Ключ *{user_input}* не существует.\n\n"
            "Проверь правильность ключа и попробуй снова, или обратись в поддержку.",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard(),
        )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена ввода ключа."""
    await update.message.reply_text(
        "Отменено. Нажми кнопку ниже, чтобы ввести ключ.",
        reply_markup=get_main_keyboard(),
    )
    return ConversationHandler.END


# ============================
# Запуск бота
# ============================

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    # ConversationHandler для логики ввода ключа
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🔐 Ввести ключ$"), ask_for_key)
        ],
        states={
            WAITING_FOR_KEY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, validate_key)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("start", start),
        ],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    logger.info("Бот запущен...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()