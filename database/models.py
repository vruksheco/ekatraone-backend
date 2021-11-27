"""
Iinitializing the database and creating tables using db models
"""

from app import *
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy(app)
migrate = Migrate(app,db)
ma = Marshmallow(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    organization = db.Column(db.String(200), nullable=True, default='organization')
    role = db.Column(db.String(200), nullable=True, default='role')
    created_date = db.Column(db.DateTime, nullable=False, default=dt.datetime.now())
    updated_date = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)
    courses = db.relationship("Courses", backref='courses')
    groups = db.relationship('Groups', backref='groups')
    is_admin = db.Column(db.Boolean, default=False)
    delivary = db.relationship('Delivary', backref='delivary')

    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    def check_password(self, password):
        return check_password_hash(self.password, password)



class Courses(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    activation_message = db.Column(db.Text, default='Welcome to this course.Lets get started')
    is_published = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=dt.datetime.now())
    updated_date = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)
    files = db.relationship('FileUpload',backref='course_files',order_by='FileUpload.id')
    days = db.relationship('Days', backref='days',order_by='Days.day')
    questions = db.relationship('Questions',order_by='Questions.question_number')
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    delivary = db.relationship('Delivary')

class FileUpload(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(120),nullable=True)
    course_id = db.Column(db.Integer,db.ForeignKey('course.id'))
    day_id = db.Column(db.Integer, db.ForeignKey('days.id'))
    day = db.Column(db.Integer)

class Days(db.Model):
    __tablename__ = 'days'
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, default=0)
    text = db.Column(db.Text, nullable=False)
    file_name = db.Column(db.String(300), nullable=True)
    files = db.relationship('FileUpload',backref='files',order_by='FileUpload.id')
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    questions = db.relationship('Questions', backref='questions')
    created_date = db.Column(db.DateTime, default=dt.datetime.now())
    updated_date = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)
    delivary = db.relationship('Delivary')


class Questions(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question_number = db.Column(db.Integer)
    text = db.Column(db.Text)
    type = db.Column(db.Text)
    correct_answer = db.Column(db.Text)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    day_id = db.Column(db.Integer, db.ForeignKey('days.id'))
    created_date = db.Column(db.DateTime, default=dt.datetime.now())
    updated_date = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)


class Groups(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    created_date = db.Column(db.DateTime, default=dt.datetime.now())
    updated_date = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    students = db.relationship('Students', backref='students',order_by='Students.id')
    delivary = db.relationship('Delivary')


class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    number = db.Column(db.String(15), nullable=False)
    channel = db.Column(db.String(15), nullable=False, default='sms')
    is_subscribed = db.Column(db.Boolean, default=True)
    timezone = db.Column(db.String(35), default='Asia/Kolkata')
    country_code = db.Column(db.String(5), default='+1')
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    created_date = db.Column(db.DateTime, default=dt.datetime.now())
    updated_date = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)


class Delivary(db.Model):
    __tablename__ = 'delivery'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    day_id = db.Column(db.Integer, db.ForeignKey('days.id'))
    status = db.Column(db.String, default='SCHEDULED')
    created_date = db.Column(db.DateTime, default=dt.datetime.now())
    updated_date = db.Column(db.DateTime)
    scheduled_time = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_date = db.Column(db.DateTime)
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'))


db.create_all()