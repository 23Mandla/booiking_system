import click
import firebase_admin
from firebase_admin import credentials
import requests

# initilise firebase admin
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# authentication api
API_KEY = "my_api_key"
SIGN_UP = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
SIGN_IN = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"

#arguments using click
@click.option("--password", "-n", prompt = "Enter your password ", help = "Your name")
@click.option("--email", "-n", prompt = "Enter your email ", help = "Your name")
@click.option("--sign", "-n", prompt = "Would you like to sign in or up ", help = "Your name")

# sign up a user
def sign_up(email, password):
    try:
        user = {
        "email" : email,
        "password": password,
        "returnSecureToken": True
     }
        
        # http request
        response = requests.post(SIGN_UP, json = user, headers = {"Content-Type" : "application/json"})
        if response.status_code == 200:
            print("Succesfully registered : ", response.json())
        else:
            print("An error occured", response.json())
            
    except Exception as error:
        print(error)

def sign_in(email, password):
    pass

# code in progress
@click.command()
def main(sign, email, password):
   
    if sign == "in":
        sign_up(email, password)
    else:
        sign_in(email, password)

if __name__ == "__main__":
    print("Welcome to booking metors!")
    main()