"""
About the some functions which is used to easier the main code without making the code complicated
"""

from config import ALLOWED_EXTENSIONS
from database.models import *

def message_temp(name, day, course, text, questions=None):
    message = f"""
Hey {name}!!!
Today is day {day} for the course {course}.
And the topic is about {text}.
Hope You Enjoy the day!
"""
    if questions is not None:
        message1 = f"""
Please answer the questions as followed
"""
        for question in questions:
            message2 = f"""
{question.question_number}. {question.text}
"""
            message1 = message1 + message2
        message = message + message1
    return message


def add_question(course_id, day_id, text):
    """
    Add new question to a day
    :param course_id: course id
    :param day_id: day id
    :param text: of type dictionary Eg: {'question':'field','type':'field','correct_answer':'field'}
    :return: questions
    """
#    course = Courses.query.get(course_id)
#    days = Days.query.filter_by(id=day_id, course_id=course_id)
    question = text['question']
    type = text['type']
    correct_answer = text['correct_answer']
    questions = Questions(text=question, type=type, correct_answer=correct_answer, day_id=day_id, course_id=course_id)
    questions.created_date = dt.datetime.now()
    db.session.add(questions)
    db.session.commit()
    return questions


def add_days(course_id, text):
    """
    Create a new day and add to the course and add questions by calling add_questions()
    :param course_id: course id
    :param text:form of dictionary Eg:{'text':'field','questions':[{'question':'field','type':'field','correct_answer':'field'}]
    :return: days
    """
    course = Courses.query.get(course_id)
    day = course.days
    output = []
    if day is None:
        day = 1
    else:
        day = len(course.days) + 1
    question = text['questions']
    days = Days(day=day, text=text['text'], course_id=course_id)
    days.created_date = dt.datetime.now()
    db.session.add(days)
    db.session.commit()
    for q in question:
        if q == [] or q is None:
            continue
        else:
            if days.questions is None:
                question_number = 1
            else:
                question_number = len(days.questions) + 1
            questions = add_question(course_id=course.id, day_id=days.id, text=q)
            questions.question_number = question_number
            output.append(questions)
    db.session.add_all(output)
    db.session.commit()
    return days


def delete_user(id):
    """
    Delete the user with all the courses and groups
    :param id: user id
    :return: None
    """
    user = User.query.get(id)
    for dl in user.delivary:
        db.session.delete(dl)
        db.session.commit()
    for c in user.courses:
        for d in c.days:
            for q in d.questions:
                db.session.delete(q)
                db.session.commit()
            db.session.delete(d)
            db.session.commit()
        db.session.delete(c)
        db.session.commit()
    groups = user.groups
    for g in groups:
        for s in g.students:
            db.session.delete(s)
            db.session.commit()
        db.session.delete(g)
        db.session.commit()
    db.session.delete(user)
    db.session.commit()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS