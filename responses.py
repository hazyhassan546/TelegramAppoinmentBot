from datetime import datetime
import constants as keys
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient


client = FaunaClient(secret=keys.FAUNA_API_KEY)
print("Data base Connected")


def button_response(input_text):
    if input_text in keys.register:
        return "User is registered successfully(dummy msj)"
    if input_text in keys.help_:
        return "Use /start to get started."
    if input_text in keys.AboutUs:
        return "To know more about Axios technologies visit https://www.google.com"


def sample_response(input_text):
    # create new variable to lower case the input_text
    # bcz we are going to compare strings in a lower case
    user_message = str(input_text).lower()
    if user_message in ('hello', 'hi', 'sup'):
        return "Hey! How's it going?"
    if user_message in ('who are you', 'who are you?', 'who is there'):
        return "Hello im Axios Bot how can i help you?"
    if user_message in ('time', "appointment"):
        now = datetime.now()
        date = now.strftime("%d%m%y, %H:%M:%S")
        return date
    return "i don't understand you!"
