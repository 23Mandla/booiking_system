import click
import firebase_admin
from firebase_admin import credentials, firestore, auth
import requests
from constance import const
from calendar_service import *

# initialise database
cred = credentials.Certificate(const.SERVICE_ACC_KEY)
firebase_admin.initialize_app(cred)
db = firestore.client()

# sign up a user
def sign_up(email : str, password):
    """
    Sign in first time app users.

    Args:
        email (string): Email to use for authentication

    Returns:
        String: Message indicating whether the user was successfully authenticated
    """
    try:
        user = {
        "email" : email,
        "password": password,
        "returnSecureToken": True
     }
        
        # http request
        response = requests.post(const.SIGN_UP, json = user, headers = {"Content-Type" : "application/json"})
        if response.status_code == 200:
            click.echo("Succesfully registered")
        else:
            click.echo("An error occured", response.json())
            
    except Exception as error:
        click.echo(error)

# sign in
def sign_in(email, password):
    try:
        user_ = {
        "email" : email,
        "password": password,
        "returnSecureToken": True
     }
        
        # http request
        response = requests.post(const.SIGN_IN, json = user_, headers = {"Content-Type" : "application/json"})
        if response.status_code == 200:
            click.echo("Succesfully loged in : ")
            return email
        else:
            click.echo("An error occured", response.json())
            
    except Exception as error:
        click.echo(error)

#arguments using click

def store_user_details(id, name, email, role, expertise):

    user = db.collection("users").document(id)
    userExist = user.get()

    if not userExist.exists:
        db.collection("users").document(id).set({
        "name" : name,
        "email" : email,
        "role" : role,
        "expertise" : expertise
         })

        click.echo("Succsfully registered")

    else:
        raise ValueError("User already exist")
    
def get_firebase_user_id(email):
    """Fetches the Firebase Authentication UID based on email."""
    try:
        user = auth.get_user_by_email(email)
        return user.uid
    
    except Exception as e:
        click.echo(e)
    
# view meetings
def meeting():
    # TODO  # get mentor / mentee from the 
    events_meeting = view_calendar_events()

    for event_id, organiser, attendees, time, status in events_meeting:

        meeting_data = {
            "mentor_id": organiser,
            "mentee_id": "mentee_id",
            "time": time,
            "status": status
        }

        meetings = db.collection("meetings").document(event_id)
        meetingExist = meetings.get()

        if not meetingExist:
            db.collection("meetings").document(event_id).set(meeting_data)
   
    docs = db.collection("meetings").stream()

    for doc in docs:
        click.echo(f"{doc.id} => {doc.to_dict()}")

# create events
@click.add_argument("topic", prompt = "Enter meeting topic ", help = "meeting topic")
@click.add_argument("descripton", prompt = "Briefly decribe the nature of the meeting ", help = "description of the meeting")
@click.add_argument("startTime", prompt = "from what time ", help = "Start meeting @")
@click.add_argument("endTime", prompt = "To what time ", help = "End meeting @")
@click.add_argument("attendees", prompt = "Add email address of the attendee  ", help = "Add meeting attendees email addresses")
@click.command()
def create_event_():
    # event schema
    """
     event = {
        'summary' : 'mentor meeting - functions',
        'description' : 'A breif tutorial on function and their use case',
        'color' : 6,
        'start': {
            'dateTime': '2025-03-04T09:00:00-07:00',
            'timeZone': 'Africa/Johannesburg',
        },
        'end': {
            'dateTime': '2025-03-04T17:00:00-07:00',
            'timeZone': 'Africa/Johannesburg',
        },
        'attendees' : [
            {'email': 'geekgeekadict@gmail.com'},
        ],
        'reminders' : {
            'useDefault' : False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }
    """

#arguments using click
@click.option("--password", "-p", prompt = "Enter your password ", help = "Your name")
@click.option("--email", "-e", prompt = "Enter your email ", help = "Your name")
@click.option("--sign", "-s", prompt = "Would you like to sign in or sign up ", help = "Your name")
@click.command()

def main(sign, email, password):
    
    if sign == "in":
        
        userEmail = sign_in(email, password)
        id = get_firebase_user_id(userEmail)
        click.echo()
        action = click.prompt("Here is what you can d:\n <register> <view avalable mentors> <request meeting with mentors> <search peers>")
        
        if userEmail:
            if action == "register":

                name = click.prompt("Enter your name : ")
                role = click.prompt("Are you a mentor or mentee? : ")
                expertise = click.prompt("Experience [beginner, intermediate, senior]")

                try:
                    store_user_details(id, name, userEmail,  role, expertise)
                    click.echo("User details stored successfully!")
                    input("Would you like to view mentor ?")
                except Exception as e:
                    click.echo(f"Error storing user details: {e}")
            else:
                meeting()
    else:
        sign_up(email, password)
        
if __name__ == "__main__":
    print("Welcome to booking metors!")
    while True:
        ans = click.prompt("Continue")
        if ans == "yes":
            main()
        else:
            break