from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from time import ctime
from datetime import date, datetime
from .parse_excel import read_linkedin, read_google
from .automation import autofill, verify
from .statistics import generate_combined_analysis
from .models import User, UserContact, Person, Institute, Location, Experience, Title, Job, Degree, Education
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


views = Blueprint("views", __name__)

@views.route("/", methods=["GET", "POST"])
@login_required
def home():
        
    contact_ids = [contact.person_id for contact in UserContact.query.filter_by(user_id=current_user.id).all()]
    contacts = Person.query.filter(Person.id.in_(contact_ids)).all()
    
    editable = False
    
    sort_by = request.args.get("sort_by", "id")
    sort_order = request.args.get("sort_order", "asc")
    search_query = request.form.get('search_query', '')
    delete_target = request.form.get("delete_target")
    
    if sort_by == 'first_name':
        contacts.sort(key=lambda x: x.first_name, reverse=(sort_order == 'desc'))
    elif sort_by == 'last_name':
        contacts.sort(key=lambda x: x.last_name, reverse=(sort_order == 'desc'))
    elif sort_by == 'email_address':
        contacts.sort(key=lambda x: x.email_address, reverse=(sort_order == 'desc'))
    else:
        contacts.sort(key=lambda x: x.id, reverse=(sort_order == 'desc'))
    
    time = ctime().split()[-2]
    if int(time[0:2]) >= 18:
        period = "evening"
    elif int(time[0:2]) >= 12:
        period = "afternoon"
    elif int(time[0:2]) >= 6:
        period = "morning"
    else:
        period = "night"
    
    if request.method == 'POST':
        
        if search_query:
            contacts = [contact for contact in contacts if search_query.lower().replace(" ","") in (contact.first_name + contact.last_name).lower().replace(" ","")]
        if delete_target:
            contact = Person.query.get(delete_target)
            if contact:
                contactlink = UserContact.query.filter_by(person_id=delete_target, user_id=current_user.id).first()
                db.session.delete(contactlink)
                db.session.commit()
                if not contact.public:
                    db.session.delete(contact)
                    db.session.commit()
            return redirect(url_for("views.home"))
        if "filterButton" in request.form:
            if request.form.get("filter_type") == "location":
                contacts = [contact for contact in contacts if Location.query.get(contact.location_id) and request.form.get("filter_input").lower() in Location.query.get(contact.location_id).name.lower()]
    
    return render_template("home.html", name="Home", user=current_user, period=period, contacts=contacts, sort_by=sort_by, sort_order=sort_order, editable=editable, search_query=search_query)

@views.route("/edit_contact", methods=["POST","GET"])
@login_required
def edit_contact():
    
    contact_id = request.args.get("contact_id")
    if contact_id:
        contact = Person.query.get(contact_id)
    else:
        contact = Person()
    
    if request.method == "POST":
        
        if "addTheExperience" in request.form:
            new_title = Title(name=request.form.get("title"))
            db.session.add(new_title)
            db.session.commit()
            
            new_job = Job(title_id=new_title.id)
            db.session.add(new_job)
            db.session.commit()
            
            if request.form.get("company"):
                new_job.institute_id = request.form.get("company")
            start = datetime(int(request.form.get("newExperienceStart")[:4]), int(request.form.get("newExperienceStart")[-2:]), 1)
            end = datetime(int(request.form.get("newExperienceEnd")[:4]), int(request.form.get("newExperienceEnd")[-2:]), 1)
            current_experience = True if request.form.get("newExperienceCurrent") == "on" else False
            description = request.form.get("experienceDescription")
            new_experience = Experience(person_id=contact_id, job_id=new_job.id, start_date=start, end_date=end, current_experience=current_experience, description=description)
            db.session.add(new_experience)
            db.session.commit()
        
        elif "addTheEducation" in request.form:
            
            new_degree = Degree(name=request.form.get("degree"),field=request.form.get("field"))
            db.session.add(new_degree)
            db.session.commit()
            
            start = datetime(int(request.form.get("newEducationStart")[:4]), int(request.form.get("newEducationStart")[-2:]), 1)
            end = datetime(int(request.form.get("newEducationEnd")[:4]), int(request.form.get("newEducationEnd")[-2:]), 1)
            current_education = True if request.form.get("newEducationCurrent") == "on" else False
            description = request.form.get("educationDescription")
            new_education = Education(person_id=contact_id, degree_id=new_degree.id, start_date=start, end_date=end, current_education=current_education, description=description)
            if request.form.get("school"):
                new_education.institute_id = int(request.form.get("school"))
            db.session.add(new_education)
            db.session.commit()
            
            
        else:
            profile_pic = request.files.get("profilePicture")
            email_address = request.form.get("emailAddress")
            location = request.form.get("location")
            
            
            if not contact_id:
                contact = Person()
                current_user.contacts.append(contact)
                db.session.commit()
                new_contact_id = contact.id
                
            if profile_pic:
                contact.profile_picture = profile_pic.read()
            contact.first_name = request.form.get("firstName")
            contact.last_name = request.form.get("lastName")
            if contact.email_address != email_address:
                contact.email_verified = False
                contact.email_address = email_address
            contact.phone_number = request.form.get("phoneNumber")
            if location:
                new_location = Location(name=location)
                db.session.add(new_location)
                db.session.commit()
                contact.location_id = new_location.id
                db.session.commit()
            else:
                contact.location_id = None
                db.session.commit()
            contact.linkedin_account = request.form.get("linkedinLink")
            contact.notes = request.form.get("contactNotes")
            contact.public = False
            
            if request.form.get("visibility") == "on":
                if contact.email_address:
                    contact.public = True
                else:
                    flash("Contact can only be made public with email address present", category="error")
                    
            db.session.commit()
        
        if not contact_id:
            return redirect(url_for("views.edit_contact", contact_id=new_contact_id))

                
        elif "saveExperience" in request.form:
            new_title = Title(name=request.form.get("title"))
            db.session.add(new_title)
            db.session.commit()
            
            new_job = Job(title_id=new_title.id)
            db.session.add(new_job)
            db.session.commit()
            
            experience = Experience.query.get(request.form.get("experience_id"))
            
            if request.form.get("company"):
                new_job.institute_id = request.form.get("company")
            start = datetime(int(request.form.get("editExperienceStart")[:4]), int(request.form.get("editExperienceStart")[-2:]), 1)
            end = datetime(int(request.form.get("editExperienceEnd")[:4]), int(request.form.get("editExperienceEnd")[-2:]), 1)
            current_experience = True if request.form.get("editExperienceCurrent") == "on" else False
            description = request.form.get("experienceDescription")
            experience.start_date, experience.end_date, experience.current_experience, experience.job_id, experience.description = start, end, current_experience, new_job.id, description
            db.session.commit()
            
        elif "saveEducation" in request.form:
            new_degree = Degree(name=request.form.get("degree"),field=request.form.get("field"))
            db.session.add(new_degree)
            db.session.commit()
            
            education = Education.query.get(int(request.form.get("education_id")))
            
            start = datetime(int(request.form.get("editEducationStart")[:4]), int(request.form.get("editEducationStart")[-2:]), 1)
            end = datetime(int(request.form.get("editEducationEnd")[:4]), int(request.form.get("editEducationEnd")[-2:]), 1)
            current_education = True if request.form.get("editEducationCurrent") == "on" else False
            description = request.form.get("educationDescription")
            education.start_date, education.end_date, education.current_education, education.degree_id, education.description = start, end, current_education, new_degree.id, description
            if request.form.get("school"):
                education.institute_id = int(request.form.get("school"))
            db.session.commit() 

                
        elif "deleteExperienceButton" in request.form:
            experience = Experience.query.get(request.form.get("deleteExperienceButton"))
            db.session.delete(experience)
            db.session.commit()
        
        elif "deleteEducationButton" in request.form:
            education = Education.query.get(request.form.get("deleteEducationButton"))
            db.session.delete(education)
            db.session.commit()
            
        elif "autofillButton" in request.form:
            autofill(contact)
            
        elif "verifyEmailButton" in request.form:
            email_address = request.form.get("emailAddress")
            verify(email_address)
            contact.email_verified = True
            
    location_name = Location.query.get(contact.location_id).name if Location.query.get(contact.location_id) else ""
    present = f"{datetime.now().year:04d}-{datetime.now().month:02d}"
    institutes = Institute.query.all()
            
    return render_template("edit_contact.html", name="Edit Contact", user=current_user, contact=contact, location_name=location_name, present=present, institutes=institutes)

@views.route("/edit_institute", methods=["POST","GET"])
@login_required
def edit_institute():
    
    industries = open("website/static/industries.txt", "r").read().split("\n")
    
    institute_id = request.args.get("institute_id")
    if institute_id:
        institute = Institute.query.get(institute_id)
        if institute.creator != current_user:
            return redirect(url_for('views.institutes'))
    else:
        institute = Institute()
    
    if request.method == "POST":
        
        logo = request.files.get("instituteLogo")
        name = request.form.get("instituteName")
        description = request.form.get("description")
        industry = request.form.get("industry")
        
        if not institute_id:
            institute = Institute(creator=current_user.id)
            db.session.add(institute)
            db.session.commit()
            new_institute_id = institute.id
            
        db.session.add(institute)
        db.session.commit()
        
        institute.name = name
        institute.industry = industry
        institute.description = description
        if logo:
            institute.institute_logo = logo.read()
        if industry:
            institute.industry = industry
                
        db.session.commit()
        
        if not institute_id:
            return redirect(url_for("views.edit_institute", institute_id=new_institute_id))
            
    return render_template("edit_institute.html", name="Edit Institute", user=current_user, institute=institute, industries=industries)

@views.route("/upload", methods=["POST", "GET"])
@login_required
def upload():
    if request.method == "POST":
        if "upload_type" in request.args:
            upload_type = request.args.get("upload_type")
        if request.files.get("contacts_file"):
            try:
                all_public = True if request.form.get("all_public") == "checked" else False
                all_autofill = True if request.form.get("all_autofill") == "checked" else False
                contacts_file = request.files.get("contacts_file")
                if upload_type == "linkedin":
                    read_linkedin(contacts_file, all_public=all_public, all_autofill=all_autofill)
                    flash("Uploaded Linkedin connections successfully", category="success")
                elif upload_type == "google":
                    read_google(contacts_file, all_public=all_public, all_autofill=all_autofill)
                    flash("Uploaded Google contacts successfully", category="success")
                else:
                    flash("Select an upload type first", category="error")
            except:
                flash("An error occured. Ensure your data is formatted correctly.", category="error")
            
    return render_template("upload.html", name="Upload", user=current_user)

@views.route("/account", methods=["POST", "GET"])
@login_required
def account():
    if request.method == "POST":
        if request.files.get("profilePicture"): 
            current_user.profile_picture = request.files.get("profilePicture").read()
        current_user.first_name = request.form.get("firstName")
        current_user.last_name = request.form.get("lastName")
        db.session.commit()
        if "verifyEmailButton" in request.form:
            email_address = request.form.get("emailAddress")
            verify(email_address)
    
    return render_template("account.html", name="Account", user=current_user)

@views.route("/institutes", methods=["POST", "GET"])
@login_required
def institutes():
    search_query = request.form.get('search_query', '')
    
    institutes = Institute.query.all()
    if search_query:
        institutes = [institute for institute in institutes if search_query.lower().replace(" ","") in institute.name.lower().replace(" ","")]    
    
    return render_template("institutes.html", name="Institutes", user=current_user, institutes=institutes, search_query=search_query)

@views.route("/statistics", methods=["POST", "GET"])
@login_required
def statistics():

    generate_combined_analysis()
    
    return render_template("statistics.html", name="Statistics", user=current_user)

@views.route("/verify_profile", methods=["POST", "GET"])
def verify_profile():
    
    
    return render_template("verify_profile.html", name="Verify details")

@views.route("/change_password", methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        new_password_retype = request.form.get("new_password_retype")
        
        if not check_password_hash(current_user.password, old_password):
            flash("Old password is incorrect", category="error")
        elif new_password != new_password_retype:
            flash("Passwords do not match", category="error")
        elif len(new_password) < 7:
            flash("Password too short", category="error")
        else:
            current_user.password = generate_password_hash(new_password, method="sha256")
            db.session.commit()
            flash("Password changed successfully", category="success")
            return redirect(url_for("views.account"))
            
    return render_template("change_password.html", name="Forgot Password", user=current_user)
