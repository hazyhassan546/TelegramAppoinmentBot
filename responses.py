from datetime import datetime

import commandHandlers
import constants as keys
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
import pytz

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
        # in below function we are just changing up last command for the user to get date.
        commandHandlers.get_appointment_start_date_handler(update, contex)
        return "Please enter date of the appointment\nExample: 20/02/2021"
    if last_command == keys.getAppointmentDate:
        set_appointment('date', user_message)
        # in below function we are just changing up last command for the user to get date.
        commandHandlers.get_appointment_end_date_handler(update, contex)
        return "Now please enter time of the appointment\nExample: 2:00pm,3:00pm"
    if last_command == keys.getAppointmentTime:
        set_appointment('time', user_message)
        # in below function we are just changing up last command for the user to get date.
        commandHandlers.submit_appointment_handler(update, contex, appointmentData)
        # reset appointments data
        reset_appointment()
        return "Thanks for the information.\nUse this command to list your appointments: /"+keys.getMyAppointment

    # now look for ordinary messages
    user_message = str(user_message).lower()
    if user_message in ('hello', 'hi', 'sup'):
        return "Hey! How's it going?"
    if user_message in ('who are you', 'who are you?', 'who is there'):
        return "Hello im Axios Bot how can i help you?"
    if user_message in ('time', "appointment"):
        now = datetime.now()
        date = now.strftime("%d%m%y, %H:%M:%S")
        return date
    return "i don't understand you!"
