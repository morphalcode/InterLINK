import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from geopy.geocoders import Nominatim
from .models import Person, UserContact, Location, Experience, Education, Job, Title, Institute
from flask import flash, url_for
from datetime import datetime
from flask_login import login_required, current_user
from collections import Counter
from . import db

def generate_combined_analysis():
    #Preparing document & geolocator
    geolocator = Nominatim(user_agent="Stefan")
    doc = open(r"coords.txt", "w")
    doc.write("longitude,latitude\n")
    
    contacts = current_user.contacts
    location_names = [Location.query.get(person.location_id).name for person in contacts if Location.query.get(person.location_id)]
        
    #Geocoding locations
    for location in location_names:
        coordinates = geolocator.geocode(location)
        if coordinates:
            doc.write(f"{str(coordinates.longitude)},{str(coordinates.latitude)}\n")
        
    doc.close()

    df = pd.read_csv(r"coords.txt")
    c = Counter(zip(df.longitude,df.latitude))
    s = [10*c[(xx,yy)] for xx,yy in zip(df.longitude,df.latitude)]
    BBox = (-180, 180, -90, 90)
    mymap = plt.imread(r"website/static/world_map.webp")
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: Map
    ax = axes[0, 0]
    ax.scatter(df.longitude, df.latitude, zorder=1, alpha= 1, c='black', s=s)
    ax.set_title("Your contacts mapped")
    ax.set_xlim(BBox[0],BBox[1])
    ax.set_ylim(BBox[2],BBox[3])
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.imshow(mymap, zorder=0, extent = BBox, aspect= 'equal')

    # Plot 2: Industry breakdown
    ax = axes[0, 1]
    industries ={l:0 for l in open("website/static/industries.txt","r").read().split("\n")}
    for contact in current_user.contacts:
        for experience in contact.experiences:
            if experience.current_experience:
                industries[experience.job.institute.industry] += 1
            
    sizes = list(industries.values())
    labels = list(industries.keys())
    if any(sizes):
        colours = open("website/static/colours.txt","r").read().split("\n")[:len(labels)]
        ax.pie(sizes, startangle=140, radius=1, colors=colours)
        ax.legend(labels, loc="upper right", prop={'size': 6})
        ax.axis('equal')
        ax.set_title("Your contacts' industries")
    else:
        ax.axis('off')

    # Plot 3: Experience distribution
    ax = axes[1, 0]
    yearsofexperience = {
        "0-4":0, "5-9":0, "10-14":0, "15-19":0, "20-24":0,
        "25-29":0, "30-34":0, "35-39":0, "40-44":0, "45-49":0,
        "50+":0
    }
    ranges = list(yearsofexperience.keys())
    for contact in current_user.contacts:
        years = 0
        for experience in contact.experiences:
            years += (experience.end_date - experience.start_date).days / 365.25
        for i in range(10):
            if round(years) <= 4 + 5*i:
                yearsofexperience[ranges[i]] += 1
                break
        else:
            yearsofexperience["50+"] += 1

    frequency = list(map(int,yearsofexperience.values()))
    ax.bar(ranges,frequency)
    ax.set_xlabel("No. of years of experience")
    ax.set_ylabel("No. of contacts")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_title("Your contacts' years of experience")

    # Plot 4: Education distribution
    ax = axes[1, 1]
    yearsofeducation = {
        "0":0, "1":0, "2":0, "3":0, "4":0,
        "5":0, "6":0, "7":0, "8":0, "9":0,
        "10+":0
    }
    ranges = list(yearsofeducation.keys())
    for contact in current_user.contacts:
        years = 0
        for education in contact.educations:
            years += (education.end_date - education.start_date).days / 365.25
        if round(years) >= 10:
            yearsofeducation["10+"] += 1
        else:
            yearsofeducation[str(round(years))] += 1

    frequency = list(map(int, yearsofeducation.values()))
    ax.bar(ranges,frequency)
    ax.set_xlabel("No. of years of education")
    ax.set_ylabel("No. of contacts")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_title("Your contacts' years of education")

    #save
    plt.tight_layout()

    plt.savefig("website/static/combined_analysis.png", dpi=100)
    plt.close()
