api_key = "b75b0cc2c564e4a9f420a0e353411f8d1ca2f2ce"


import requests
import json

def verify(email_address):
    data = requests.get(f"https://api.hunter.io/v2/email-verifier?email={email_address}&api_key={api_key}").json()
    doc = open("test.json", "w")
    doc.write(json.dumps(data))
    if data["data"]["status"] == "unknown":
        print(f"Couldn't verify email address")
    elif data["data"]["status"] == "invalid":
        print(f"The email address is invalid. ({str(data['data']['score'])}% validity confidence)")
    elif data["data"]["accept_all"]:
        print(f"The email address is valid, but emails are accepted by the server. ({str(data['data']['score'])}% validity confidence)")
    elif data["data"]["disposable"]:
        print(f"The email address is valid, but belongs to a disposible email service provider. ({str(data['data']['score'])}% validity confidence)")
    else:
        print(f"The email address is valid. ({str(data['data']['score'])}% validity confidence)")
        
verify("morne.fourie@fourie-design.com")
        