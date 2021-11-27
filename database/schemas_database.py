"""
Schemas
"""

from database.definations import *
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        ordered = True
        fields = ('id','name','contact','email','organization','role','created_date','updated_date','is_deleted','deleted_date')

user_schema = UserSchema()
user_schemas = UserSchema(many=True)

class CourseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Courses
        ordered = True
        fields = ('id','name','author','description','is_published','days','added_by','created_date','updated_date','is_deleted','deleted_date')
    days = ma.List(ma.Nested("DaySchema"))

class DaySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Days
        ordered = True
        order_by = 'day'
        fields = ('day','text','files','questions')
    files = ma.List(ma.Nested("FileUploadSchema"))
    questions = ma.List(ma.Nested("QuestionSchema"))

class FileUploadSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = FileUpload
        ordered = True
        fields = ('id','file_name','course_id','day')

class QuestionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Questions
        ordered = True
        fields = ('question_number','question','type','correct_answer')
        #exclude = ["text",'']
    question = auto_field("text",dump_only=True)

course_schema = CourseSchema()
course_schemas = CourseSchema(many=True)
day_schema = DaySchema()
day_schemas = DaySchema(many=True)
question_schema = QuestionSchema()
question_schemas = QuestionSchema(many=True)
file_schema = FileUploadSchema()
file_schemas = FileUploadSchema(many=True)
class GroupSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Groups
        ordered = True
        fields = ('id','name','description','students','created_date','updated_date','is_deleted','deleted_date','added_by')
    students = ma.List(ma.Nested('StudentSchema'))

class StudentSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Students
        ordered = True
        fields = ('id','name','number','channel','is_subscribed','timezone','country_code')

group_schema = GroupSchema()
group_schemas = GroupSchema(many=True)
student_schema = StudentSchema()
student_schemas = StudentSchema(many=True)
