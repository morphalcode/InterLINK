from .models import Person, UserContact
from flask import flash, url_for, request
from flask_login import login_required, current_user
from . import db
import pandas as pd
import requests
import json

api_key = "b75b0cc2c564e4a9f420a0e353411f8d1ca2f2ce"

def autofill(contact, silent=False):
    
    cflash = lambda msg, cat: flash(msg, category=cat) if not silent else None
    
    if contact.email_address:
        autofilled = 0
        
        matches = Person.query.filter_by(email_address=contact.email_address, public=True).all()
        if not contact.first_name:
            matchdata = [match.first_name for match in matches if match.first_name]
            if len(matchdata) > 0:
                contact.first_name = max(set(matchdata), key=matchdata.count)
                autofilled += 1
        if not contact.last_name:
            matchdata = [match.last_name for match in matches if match.last_name]
            if len(matchdata) > 0:
                contact.last_name = max(set(matchdata), key=matchdata.count)
                autofilled += 1
        if not contact.phone_number:
            matchdata = [match.phone_number for match in matches if match.phone_number]
            if len(matchdata) > 0:
                contact.phone_number = max(set(matchdata), key=matchdata.count)
                autofilled += 1
                
        db.session.commit()
                
        if autofilled:
            cflash(f"Successfully autofilled {autofilled} field{'s' if autofilled > 1 else ''}", "success")
        else:
            cflash("Could not find data to autofill.", "error")
            
        return autofilled
    
    else:
        cflash("Please enter an email address", "error")
        return 0
        
    
def verify(email_address):
    if email_address:
        data = requests.get(f"https://api.hunter.io/v2/email-verifier?email={email_address}&api_key={api_key}").json()
        doc = open("verified.json", "w")
        doc.write(json.dumps(data))
        if data["data"]["status"] == "unknown":
            flash(f"Couldn't verify email address", category="error")
        elif data["data"]["status"] == "invalid":
            flash(f"The email address is invalid. ({str(data['data']['score'])}% validity confidence)", category="error")
        elif data["data"]["accept_all"]:
            flash(f"The email address is valid, but emails are accepted by the server. ({str(data['data']['score'])}% validity confidence)", category="success")
        elif data["data"]["disposable"]:
            flash(f"The email address is valid, but belongs to a disposible email service provider. ({str(data['data']['score'])}% validity confidence)")
        else:
            flash(f"The email address is valid. ({str(data['data']['score'])}% validity confidence)")
    else:
        flash("Please enter an email address", category="error")
        
        
        