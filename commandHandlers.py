from datetime import datetime
import constants as keys
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
import pytz
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
client = FaunaClient(secret=keys.FAUNA_API_KEY)


tz = pytz.timezone('US/Pacific')


def book_appointment_handler(update, context):
    # we can use chat_id to fetch user from db
    chat_id = update.callback_query.from_user.id
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
    client.query(q.update(q.ref(q.collection("users"), user["ref"].id()), {"data": {"last_command": keys.getAppointmentTitle}}))
    return "Please enter the Title of your appointment\nTo cancel booking use /cancel "


def get_appointment_start_date_handler(update, context):
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
    client.query(q.update(q.ref(q.collection("users"), user["ref"].id()), {"data": {"last_command": keys.getAppointmentDate}}))


def get_appointment_end_date_handler(update, context):
    # we can use chat_id to fetch user from db
    chat_id = update.callback_query.from_user.id
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
    client.query(q.update(q.ref(q.collection("users"), user["ref"].id()), {"data": {"last_command": keys.getAppointmentTime}}))


def date_to_utc(d):
    aware_d = tz.localize(d, is_dst=None)
    utc_d = aware_d.astimezone(pytz.utc)
    return utc_d


def utc_to_date(fauna_time):
    return fauna_time.to_datetime().strftime("%d/%m/%Y")


def submit_appointment_handler(update, context, appointment_data):
    # we can use chat_id to fetch user from db
    chat_id = update.callback_query.from_user.id
    # now fetch user to change the last command parameter with which we can perform actions
    user = client.query(
        q.get(
            q.match(
                q.index("users"),
                chat_id
            )
        )
    )
    # now we will change user.lastCommand to empty string.
    client.query(q.update(q.ref(q.collection("users"), user["ref"].id()), {"data": {"last_command": ""}}))
    #   Now lets create appointment
    result = client.query(
        q.create(
            q.collection("appointments"),
            {"data": {"title": appointment_data["title"],
                      "appointmentDate": date_to_utc(appointment_data["date"]),
                      "time_slot": appointment_data["time"],
                      "completed": False,
                      "user": chat_id
                      }}
        )
    )


def get_my_appointments_handler(update, context):
    chat_id = update.effective_chat.id
    appointments = client.query(q.paginate(q.match(q.index("appointments"), chat_id)))
    reply_text = ""
    for i in appointments["data"]:
        appointment = client.query(q.get(q.ref(q.collection("appointments"), i.id())))
        status = "Not Completed"
        if appointment["data"]["completed"]:
            continue
        reply_text = "Appointment title: "+appointment["data"]["title"]+"\n"+"Date: "+utc_to_date(appointment["data"]["appointmentDate"])+"\n"+"Time: "+appointment["data"]["time_slot"]+"\n"+"Status: "+status
        options = [
            [
                InlineKeyboardButton("Complete", callback_data="updateStatus_"+i.id()),
                InlineKeyboardButton("Delete", callback_data="deleteAppointments_"+i.id())
            ]
        ]
        markup = InlineKeyboardMarkup(options)
        update.callback_query.message.reply_text(reply_text, reply_markup=markup)
    if reply_text == "":
        keyboard = [
            [
                InlineKeyboardButton("Book Appointment", callback_data=keys.book_appointment),
                InlineKeyboardButton("List My Appointment", callback_data=keys.getMyAppointment)
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        reply_text = "You don't have any appointments Pending"
        update.callback_query.message.reply_text(reply_text, reply_markup=reply_markup)


def update_appointment_status(data):
    message = data
    appointment_id = message.split("_")[1]
    event = client.query(q.get(q.ref(q.collection("appointments"), appointment_id)))

    if event["data"]["completed"]:
        new_status = False

    else:
        new_status = True

    client.query(q.update(q.ref(q.collection("appointments"), appointment_id), {"data": {"completed": new_status}}))
    return "Your appointment has been completed successfully."


def delete_appointment(data):
    appointment_id = data.split("_")[1]
    client.query(q.delete(q.ref(q.collection("appointments"), appointment_id)))
    return "Your appointment has been deleted successfully."

