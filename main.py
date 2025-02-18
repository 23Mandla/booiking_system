import click
import firebase_admin
from firebase_admin import credentials, firestore
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
            print("Succesfully registered : ", response.json())
        else:
            print("An error occured", response.json())
            
    except Exception as error:
        print(error)

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
            print("Succesfully loged in : ")
            result = response.json()
            return result.get('idToken')
        else:
            print("An error occured", response.json())
            
    except Exception as error:
        print(error)

#arguments using click
@click.option("--name", "-n", prompt = "Enter your name ", help = "Your name")
@click.option("--email", "-n", prompt = "Enter your email ", help = "Your email address")
@click.option("--role", "-n", prompt = "Are you a mentor or mentee ", help = "Mentor or mentee")
@click.option("--expertise", "-n", prompt = "Experience [beginner, intermediate, senior] ", help = "Your experience")

# code in progress
@click.command()
def store_user_details(name, email, role, expertise):

    id = store_user_details.id
    db.collection("users").document(id).set({
        "name" : name,
        "email" : email,
        "role" : role,
        "expertise" : expertise
    })

#arguments using click
@click.option("--password", "-n", prompt = "Enter your password ", help = "Your name")
@click.option("--email", "-n", prompt = "Enter your email ", help = "Your name")
@click.option("--sign", "-n", prompt = "Would you like to sign in or up ", help = "Your name")

# code in progress
@click.command()
def main(sign, email, password):
   
    if sign == "up":
        sign_up(email, password)
    else:
        id = sign_in(email, password)
        while True:
            if input("Here is what you can do : ['register'] ? ") == "register":
                store_user_details.id = id
                store_user_details()

            input("Here are other operetions you can perform ...")

if __name__ == "__main__":
    print("Welcome to booking metors!")
    main()