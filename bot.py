import constants as keys
import commandHandlers as cmd_hanlers
from telegram.ext import *
import os
import responses as R
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
PORT = int(os.environ.get('PORT', 8443))


print("Bot started...")


def start_command(update, contex):
    keyboard = [
        [InlineKeyboardButton(keys.Appointment, callback_data=keys.Appointment)],
        [
            InlineKeyboardButton(keys.AboutUs, callback_data=keys.AboutUs),
            InlineKeyboardButton(keys.help_, callback_data=keys.help_)
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    R.save_user_to_db(update, contex)
    update.message.reply_text("Select option:", reply_markup=reply_markup)


def button(update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    res = R.button_response(query.data)
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    query.edit_message_text(text=res)


def help_command(update, contex):
    update.message.reply_text("Use /start to get started.")


def handle_message(update, contex):
    response = R.message_response(update, contex)
    update.message.reply_text(response)


def error(update, contex):
    print("Something went wrong")


def main():
    updater = Updater(keys.API_KEY, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start_command))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler(keys.book_appointment, cmd_hanlers.book_appointment_handler))
    dispatcher.add_handler(CommandHandler(keys.getMyAppointment, cmd_hanlers.get_my_appointments_handler))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_message))
    dispatcher.add_error_handler(error)

    updater.start_polling()    # For local run
    # updater.start_webhook(listen="0.0.0.0",           # For Heroku run
    #                       port=int(PORT),
    #                       url_path=keys.API_KEY,
    #                       webhook_url=('https://gentle-cove-69794.herokuapp.com/' + keys.API_KEY)
    #                       )
    updater.idle()


main()
