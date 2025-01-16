from .models import Person, UserContact
from flask import flash, url_for
from flask_login import login_required, current_user
from . import db
from .automation import autofill
import pandas as pd
import requests

delNone = lambda x: "" if str(x) == "nan" else x

def read_linkedin(file, all_public=False, all_autofill=False):
    df = pd.read_csv(file, skiprows=3)
    autofilled = 0
    for index, row in df.iterrows():

        contact = Person(first_name=delNone(row[0]), last_name=delNone(row[1]), linkedin_account=delNone(row[2]), email_address=delNone(row[3]), public=True if all_public else False)
        current_user.contacts.append(contact)
        db.session.commit()
        
        if all_autofill:
            autofilled += autofill(contact, silent=True)
            
    if all_autofill:
        if autofilled:
            flash(f"Successfully autofilled a total of {autofilled} field{'s' if autofilled > 1 else ''}", category = "success")
        else:
            flash("Could not find data to autofill.", category = "error")
            
def read_google(file, all_public=False, all_autofill=False):
    df = pd.read_csv(file)
    autofilled = 0
    
    for index, row in df.iterrows():
        
        pfp = requests.get(delNone(row[27])).content

        contact = Person(first_name=delNone(row[1]), last_name=delNone(row[3]), notes=delNone(row[25]), email_address=delNone(row[30]), phone_number=delNone(row[32]), profile_picture=pfp, public=True if all_public else False)
        current_user.contacts.append(contact)
        db.session.commit()
        
        if all_autofill:
            autofilled += autofill(contact, silent=True)
            
    if all_autofill:
        if autofilled:
            flash(f"Successfully autofilled a total of {autofilled} field{'s' if autofilled > 1 else ''}", category = "success")
        else:
            flash("Could not find data to autofill.", category = "error")
            