import click
import firebase_admin
from firebase_admin import credentials, firestore, auth
import requests
from constance import const
from calendar_service import *
from datetime import datetime

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

# create event
def create_event_(topic, description, startDate, startTime, endDate, endTime, attendees):

    f_startTime = [int(time_start) for time_start in startTime.split(":")]
    f_date = [int(date_start) for date_start in startDate.split("-")]
    start_date = datetime(f_date[0], f_date[1], f_date[2], f_startTime[0], f_startTime[1]).isoformat()

    f_endTime = [int(time_ends) for time_ends in endTime.split(":")]
    f_end_date = [int(date_ends) for date_ends in endDate.split("-")]
    end_date = datetime(f_end_date[0], f_end_date[1], f_end_date[2], f_endTime[0], f_endTime[1]).isoformat()

    try:
        #TODO Serialize json object
        event_ceation = create_event(topic, description, start_date, end_date, attendees)
        print(event_ceation)
    except Exception as error:
        print(f"An error occured : {error}")

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
            # create events
            topic = click.prompt("Enter meeting topic ")
            description = click.prompt("Briefly decribe the nature of the meeting ")
            startDate = click.prompt("Enter start date (YYYY-MM-DD): ")
            startTime = click.prompt("from what time (HH:MM, 24-hour format): ")
            endDate = click.prompt("Enter end date (YYYY-MM-DD): ")
            endTime = click.prompt("To what time (HH:MM, 24-hour format): ")
            attendees = click.prompt("Add email address of the attendee  ")

            create_event_(topic, description, startDate, startTime, endDate, endTime, attendees)
        else:
            break