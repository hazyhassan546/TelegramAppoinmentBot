import commandHandlers
import constants as keys
import commandHandlers as cmd_hanlers
from telegram.ext import *
import os
import responses as R
import pythoncalendar as telegramcalendar
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import datetime
import logging

PORT = int(os.environ.get('PORT', 8443))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
print("Bot started...")
slot_options_again = [
        [
            InlineKeyboardButton("12:00 pm", callback_data="slot,12:00 pm"),
            InlineKeyboardButton("01:00 pm", callback_data="slot,01:00 pm"),
            InlineKeyboardButton("02:00 pm", callback_data="slot,02:00 pm")
        ],
        [
            InlineKeyboardButton("03:00 pm", callback_data="slot,03:00 pm"),
            InlineKeyboardButton("04:00 pm", callback_data="slot,04:00 pm"),
            InlineKeyboardButton("05:00 pm", callback_data="slot,05:00 pm")
        ],
        [
            InlineKeyboardButton("07:00 pm", callback_data="slot,07:00 pm"),
            InlineKeyboardButton("08:00 pm", callback_data="slot,08:00 pm"),
            InlineKeyboardButton("09:00 pm", callback_data="slot,09:00 pm")
        ],
        [
            InlineKeyboardButton("Select Date", callback_data=keys.selectDate),
        ]
    ]
slot_options = [
        [
            InlineKeyboardButton("12:00 pm", callback_data="slot,12:00 pm"),
            InlineKeyboardButton("01:00 pm", callback_data="slot,01:00 pm"),
            InlineKeyboardButton("02:00 pm", callback_data="slot,02:00 pm")
        ],
        [
            InlineKeyboardButton("03:00 pm", callback_data="slot,03:00 pm"),
            InlineKeyboardButton("04:00 pm", callback_data="slot,04:00 pm"),
            InlineKeyboardButton("05:00 pm", callback_data="slot,05:00 pm")
        ],
        [
            InlineKeyboardButton("07:00 pm", callback_data="slot,07:00 pm"),
            InlineKeyboardButton("08:00 pm", callback_data="slot,08:00 pm"),
            InlineKeyboardButton("09:00 pm", callback_data="slot,09:00 pm")
        ],
    ]
slot_markup = InlineKeyboardMarkup(slot_options)
slot_markup_again = InlineKeyboardMarkup(slot_options_again)


def start_command(update, contex):
    keyboard = [
        [InlineKeyboardButton(keys.Appointment, callback_data=keys.Appointment_)],
        [
            InlineKeyboardButton(keys.AboutUs, callback_data=keys.AboutUs),
            InlineKeyboardButton(keys.help_, callback_data=keys.help_)
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    R.save_user_to_db(update, contex)
    update.message.reply_text("Select option:", reply_markup=reply_markup)


def inline_handler(update, context: CallbackContext) -> None:
    query = update.callback_query
    print(query.data)
    date_handle = False

    if 'DAY;' in query.data or 'NEXT-MONTH;' in query.data or 'PREV-MONTH;' in query.data:
        date_handle = True

    if date_handle:
        print("Date handler!")
        selected, date = telegramcalendar.process_calendar_selection(update, context)
        if selected:
            if 'DAY;' in query.data:
                if date >= datetime.datetime.now():
                    R.set_date(update, context, date)
                    query.answer()
                    query.edit_message_text(text="You have selected :" + date.strftime("%d/%m/%Y"), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(keys.getTime, callback_data=keys.getTime)]]))
                else:
                    keyboard = [
                        [InlineKeyboardButton("Select Date", callback_data=keys.selectDate)],
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    query.answer()
                    query.edit_message_text(text="Sorry this date is not available", reply_markup=reply_markup)

    elif keys.selectDate in query.data:
        print("Again select Date handler!")
        R.send_calendar_again(update, context)
        query.answer()
        query.edit_message_text("Select date again")

    elif keys.getTime in query.data:
        print("Time handler!")
        query.answer()
        query.edit_message_text(text="Select time slot:", reply_markup=slot_markup)

    elif keys.Appointment_ in query.data:
        print("Menu handler!")
        keyboard = [
            [
                InlineKeyboardButton("Book Appointment", callback_data=keys.book_appointment),
                InlineKeyboardButton("List My Appointment", callback_data=keys.getMyAppointment)
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        res = "Select Option:"
        query.answer()
        query.edit_message_text(text=res, reply_markup=reply_markup)

    elif keys.book_appointment in query.data:
        res = cmd_hanlers.book_appointment_handler(update, context)
        query.answer()
        query.edit_message_text(text=res)

    elif keys.getMyAppointment in query.data:
        print("List appointment handler!")
        cmd_hanlers.get_my_appointments_handler(update, context)
        query.answer()

    elif keys.slot in query.data:
        print("Slot handler!")
        data = query.data.split(",")[1]
        available = R.check_slot_availability(data)
        if available:
            print("slot available")
            res = R.set_time(update, context, data)
            query.answer()
            query.edit_message_text(text=res)
        else:
            print("slot not available")
            query.answer()
            query.edit_message_text(text="Sorry this slot is not available: "+data, reply_markup=slot_markup_again)

    elif keys.update_status in query.data:
        print("update_status!")
        res = commandHandlers.update_appointment_status(query.data)
        query.answer()
        query.edit_message_text(text=res)

    elif keys.delete_appointment in query.data:
        print("delete_appointment")
        res = commandHandlers.delete_appointment(query.data)
        query.answer()
        query.edit_message_text(text=res)

    else:
        print("Normal button handler")
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


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', context.error)


def main():
    updater = Updater(keys.API_KEY, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start_command))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('cancel', R.cancel_handler))
    dispatcher.add_handler(CommandHandler('selectDate', R.send_calendar))
    dispatcher.add_handler(CallbackQueryHandler(inline_handler))
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
