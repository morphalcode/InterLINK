from . import db
from flask_login import UserMixin
from base64 import b64encode

class Base(db.Model):
    __abstract__ = True

    def __init__(self, **kwargs):
        for attr in self.__mapper__.column_attrs:
            if attr.key in kwargs:
                continue
            
            assert len(attr.columns) == 1
            col = attr.columns[0]

            if col.default and not callable(col.default.arg):
                kwargs[attr.key] = col.default.arg

        super(Base, self).__init__(**kwargs)


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    profile_picture = db.Column(db.LargeBinary, default=open("website/static/anon.png", "rb").read())
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"))
    email_address = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    reset_token = db.Column(db.String(150))
    contacts = db.relationship("Person", secondary="usercontact", backref="user")

class Person(Base):
    __tablename__ = "person"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), default="")
    last_name = db.Column(db.String(150), default="")
    profile_picture = db.Column(db.LargeBinary, default=open("website/static/anon.png", "rb").read())
    location_id = db.Column(db.Integer, db.ForeignKey("location.id"))
    email_address = db.Column(db.String(150), default="")
    phone_number = db.Column(db.Integer, default="")
    linkedin_account = db.Column(db.String, default="")
    notes = db.Column(db.Text(1000), default="")
    email_verified = db.Column(db.Boolean, default=False)
    public = db.Column(db.Boolean, default=False)
    experiences = db.relationship("Experience", backref="person")
    users = db.relationship("User", secondary="usercontact", backref="person")
    skills = db.relationship("Skill", secondary= "skillslink", backref="person")
    educations = db.relationship("Education", backref="person")

class Location(db.Model):
    __tablename__ = "location"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), default="")
    persons = db.relationship("Person", backref="location")
    users = db.relationship("User", backref="location")

class Institute(Base):
    __tablename__ = "institute"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), default="")
    description = db.Column(db.Text(1000), default="")
    institute_logo = db.Column(db.LargeBinary, default=open("website/static/anoninstitute.png", "rb").read())
    creator = db.Column(db.Integer, db.ForeignKey("user.id"))
    industry = db.Column(db.String(150), default="Unspecified")
    educations = db.relationship("Education", backref="institute")
    jobs = db.relationship("Job", backref="institute")

class Degree(db.Model):
    __tablename__ = "degree"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), default="")
    field = db.Column(db.String(150), default="")
    educations = db.relationship("Education", backref="degree")
    

class Skill(db.Model):
    __tablename__ = "skill"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), default="")
    skills_links = db.relationship("SkillsLink", backref="skill")

class Title(db.Model):
    __tablename__ = "title"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), default="")
    jobs = db.relationship("Job", backref="title")

class Job(db.Model):
    __tablename__ = "job"
    id = db.Column(db.Integer, primary_key=True)
    institute_id = db.Column(db.Integer, db.ForeignKey("institute.id"))
    title_id = db.Column(db.Integer, db.ForeignKey("title.id"))
    experiences = db.relationship("Experience", backref="job")

class Experience(db.Model):
    __tablename__ = "experience"
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"))
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    description = db.Column(db.String)
    current_experience = db.Column(db.Boolean, default=False)

class UserContact(db.Model):
    __tablename__ = "usercontact"
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"), primary_key=True)

class SkillsLink(db.Model):
    __tablename__ = "skillslink"
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"))
    skill_id = db.Column(db.Integer, db.ForeignKey("skill.id"))

class Education(db.Model):
    __tablename__ = "education"
    id = db.Column(db.Integer, primary_key=True)
    institute_id = db.Column(db.Integer, db.ForeignKey("institute.id"))
    degree_id = db.Column(db.Integer, db.ForeignKey("degree.id"))
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    description = db.Column(db.String)
    current_education = db.Column(db.Boolean, default=False)