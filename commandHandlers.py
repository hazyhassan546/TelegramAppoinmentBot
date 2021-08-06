from datetime import datetime
import constants as keys
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient
import pytz
client = FaunaClient(secret=keys.FAUNA_API_KEY)


def book_appointment_handler(update, context):
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
    client.query(q.update(q.ref(q.collection("users"), user["ref"].id()), {"data": {"last_command": keys.getAppointmentTitle}}))
    context.bot.send_message(chat_id=chat_id, text="Please enter the title of your appointment")


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
    client.query(q.update(q.ref(q.collection("users"), user["ref"].id()), {"data": {"last_command": keys.getAppointmentTime}}))


def submit_appointment_handler(update, context, appointment_data):
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
    # now we will change user.lastCommand to empty string.
    client.query(q.update(q.ref(q.collection("users"), user["ref"].id()), {"data": {"last_command": ""}}))
    #   Now lets create appointment
    result = client.query(
        q.create(
            q.collection("appointments"),
            {"data": {"title": appointment_data["title"],
                      "appointmentDate": appointment_data["date"],
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
        print(appointment)
        status = "Not Completed"
        if appointment["data"]["completed"]:
            status = "Completed"
        reply_text = reply_text+"\n"+"Appointment title: "+appointment["data"]["title"]+"\n"+"Date: "+appointment["data"]["appointmentDate"]+"\n"+"Time: "+appointment["data"]["time_slot"]+"\n"+"Status: "+status+"\n\n"
    if reply_text == "":
        reply_text = "You don't have any appointments saved, type /"+keys.book_appointment+" to schedule."
    else:
        reply_text = "Appointment List:\n" + reply_text

    update.message.reply_text(reply_text)
