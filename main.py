import click
from click.testing import CliRunner
import firebase_admin
from firebase_admin import credentials, firestore, auth
import requests
from constance import const

# initialise database
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# sign up a user
def sign_up(email, password):

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
    
# schedule meeting
def meeting(mentor_id, mentee_id, time, status):
    # TODO  # get mentor / mentee from the database

    meeting_id = "meeting_1" 
    meeting_data = {
        "mentor_id": mentor_id,
        "mentee_id": mentee_id,
        "time": time,
        "status": status
    }

    db.collection("meetings").document(meeting_id).set(meeting_data)
    click.echo(f"Meeting scheduled successfully")

#arguments using click
@click.option("--password", "-n", prompt = "Enter your password ", help = "Your name")
@click.option("--email", "-n", prompt = "Enter your email ", help = "Your name")
@click.option("--sign", "-n", prompt = "Would you like to sign in or up ", help = "Your name")
@click.command()

def main(sign, email, password):
    
    if sign == "in":
        action = input("Here is what you can do : ['register'] if registered view mentor ? ")
        
        userEmail = sign_in(email, password)
        id = get_firebase_user_id(userEmail)
        if userEmail:
            if action == "register":
             
                name = click.prompt("Enter your name : ")
                role = click.prompt("Are you a mentor or mentee? : ")
                expertise = click.prompt("Experience [beginner, intermediate, senior]")

                try:
                    store_user_details(id, name, userEmail,  role, expertise)
                    click.echo("User details stored successfully!")
                except Exception as e:
                    click.echo(f"Error storing user details: {e}")
            else:
                meeting()
    else:
        sign_up(email, password)
        
if __name__ == "__main__":
    print("Welcome to booking metors!")
    main()