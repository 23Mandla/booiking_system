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
        print(f" ID: {event_id}, Meeting: {organiser}, status: {status}, attendee : {attendees}, time : {time['dateTime']}")

        meeting_data = {
            "mentor_id": organiser,
            "mentee_id": "mentee_id",
            "time": time,
            "status": status
        }

        meeting = db.collection("meetings").document(event_id)
        meetingExist = meeting.get()

        if not meetingExist:
            db.collection("meetings").document(event_id).set(meeting_data)
   
    click.echo(db.collection("meetings").get())

#arguments using click
@click.option("--password", "-n", prompt = "Enter your password ", help = "Your name")
@click.option("--email", "-n", prompt = "Enter your email ", help = "Your name")
@click.option("--sign", "-n", prompt = "Would you like to sign in or sign up ", help = "Your name")
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
    meeting()