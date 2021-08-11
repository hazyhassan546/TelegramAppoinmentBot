from datetime import datetime
import commandHandlers
import constants as keys
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import pytz
import pythoncalendar as telegramcalendar


client = FaunaClient(secret=keys.FAUNA_API_KEY)
print("Data base Connected")


appointmentData = {
  "title": "",
  "date": "",
  "time": "",
}


def reset_appointment():
    global appointmentData
    appointmentData = {
        "title": "",
        "date": "",
        "time": "",
    }


def set_appointment(key, value):
    global appointmentData
    appointmentData[key] = value


def set_date(update, context, date):
    set_appointment('date', date)
    commandHandlers.get_appointment_end_date_handler(update, context)


def set_time(update, context, time):
    set_appointment('time', time)
    # save appointment to db
    commandHandlers.submit_appointment_handler(update, context, appointmentData)
    keyboard = [
        [
            InlineKeyboardButton("List My Appointment", callback_data=keys.getMyAppointment)
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.callback_query.message.reply_text("Your Appointment is now submitted.", reply_markup=reply_markup)
    return "Thanks for the information."


def send_calendar(update, contex):
    update.message.reply_text("Please select a date: ", reply_markup=telegramcalendar.create_calendar())


def send_calendar_again(update, contex):
    update.callback_query.message.reply_text("Please select a date: ", reply_markup=telegramcalendar.create_calendar())


def check_slot_availability(data):
    appointments = client.query(q.paginate(q.match(q.index("appointments_by_date"), commandHandlers.date_to_utc(appointmentData["date"]), data, False)))
    print(appointments["data"])
    if appointments["data"]:
        return False
    else:
        return True


def save_user_to_db(update, context):
    chat_id = update.effective_chat.id
    first_name = update["message"]["chat"]["first_name"]
    username = update["message"]["chat"]["username"]
    update.message.reply_text("Hello "+first_name+", Welcome to Axios Technologies")
    try:
        client.query(q.get(q.match(q.index("users"), chat_id)))
    except:
        user = client.query(q.create(q.collection("users"), {
            "data": {
                "id": chat_id,
                "first_name": first_name,
                "username": username,
                "last_command": "",
                "date": datetime.now(pytz.UTC)
            }
        }))
        update.message.reply_text("Your Information is stored in our system.")


def button_response(input_text):
    if input_text in keys.Appointment:
        return "Welcome to Axios Appointment Scheduler:\n\nUse following commands \nBook Appointment: /"+keys.book_appointment+"\nMy Appointments: /"+keys.getMyAppointment
    if input_text in keys.help_:
        return "Use /start to get started."
    if input_text in keys.AboutUs:
        return "To know more about Axios technologies visit https://axios.tech/"


def cancel_handler(update, context):
    reset_appointment()
    # we can use chat_id to fetch user from db
    chat_id = update.effective_chat.id
    # now fetch user to change the last command parameter with which we can perform actions
    user = client.query(
        q.get(
            q.match(
                q.index("users"),
                chat_id
            )
        )
    )
    # now we will change user.lastCommand to new one.
    if user["data"]["last_command"] == "":
        update.message.reply_text("You are doing nothing.")
    else:
        client.query(
            q.update(q.ref(q.collection("users"), user["ref"].id()), {"data": {"last_command": ""}}))
        update.message.reply_text("Canceled Successfully")


def message_response(update, contex):
    user_message = update.message.text
    chat_id = update.effective_chat.id
    user = client.query(q.get(q.match(q.index("users"), chat_id)))
    # till now we have our user now lets check its previous command.
    last_command = user["data"]["last_command"]

    # code blocks to book appointment
    if last_command == keys.getAppointmentTitle:
        reset_appointment()
        set_appointment('title', user_message)
        commandHandlers.get_appointment_start_date_handler(update, contex)
        send_calendar(update, contex)
        return

        # now look for ordinary messages
    user_message = str(user_message).lower()
    if user_message in ('hello', 'hi', 'sup'):
        msg = "Hey! How's it going?"
        update.message.reply_text(msg)
        return

    if user_message in ('who are you', 'who are you?', 'who is there'):
        msg = "Hello im Axios Bot how can i help you?"
        update.message.reply_text(msg)
        return

    if user_message in ('time', "appointment"):
        now = datetime.now()
        date = now.strftime("%d%m%y, %H:%M:%S")
        msg = date
        update.message.reply_text(msg)
        return

    msg = "i don't understand you!"
    update.message.reply_text(msg)
