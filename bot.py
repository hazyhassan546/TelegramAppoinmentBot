import constants as keys
from telegram.ext import *
import os
import responses as R
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
PORT = int(os.environ.get('PORT', 8443))


print("Bot started...")


def start_command(update, contex):
    keyboard = [
        [InlineKeyboardButton(keys.register, callback_data=keys.register)],
        [
            InlineKeyboardButton(keys.AboutUs, callback_data=keys.AboutUs),
            InlineKeyboardButton(keys.help_, callback_data=keys.help_)
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Welcome to Axios Technologies")
    update.message.reply_text("select option:", reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    res = R.button_response(query.data)
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    query.edit_message_text(text=f"Selected Option: {query.data} ,\n\n\n\n Response Message: {res} ")


def help_command(update, contex):
    update.message.reply_text("You can ask google for help!")


def handle_message(update, contex):
    text = str(update.message.text).lower()
    response = R.sample_response(text)
    update.message.reply_text(response)


def error():
    print("Something went wrong")


def main():
    updater = Updater(keys.API_KEY, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start_command))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
    dispatcher.add_error_handler(error)
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=keys.API_KEY)
    updater.bot.setWebhook('https://gentle-cove-69794.herokuapp.com/' + keys.API_KEY)
    updater.idle()


main()
