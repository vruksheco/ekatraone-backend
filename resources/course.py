"""
About courses
"""

from database.schemas_database import *
import os
from services.s3_services import create_presigned_url, upload_file


class CourseDetails(Resource):
    @jwt_required
    def get(self):
        """
        Retrieving all the courses added by user
        :return: details of all the courses
        """
        try:
            user_id = get_jwt_identity()
            if user_id is None:
                raise UnauthorizedError
            courses = Courses.query.filter_by(added_by=user_id).order_by(Courses.id).all()
            if not courses:
                return {'message': "Course not found"}, 400
            output = course_schemas.dump(courses)
            return {'courses':output}
        except WrongTokenError:
            raise BadTokenError
        except UnauthorizedError:
            raise BadRequest('Token is missing')
        except BadTokenError:
            raise BadRequest('Token is invalid')
        except InternalServerError:
            db.session.rollback()
            raise BadRequest(errors['InternalServerError']['message'])

    @jwt_required
    @ns_course.expect(detail_courses)
    #@ns_course.doc(params={'uploadfile': {'description':'uploadfile','in':'formdata','type':'file'}})
    def post(self):
        """
        Creating new course
        :return: success when course is created
        """
        try:
            user_id = get_jwt_identity()
            if not User.query.filter_by(id=user_id).first():
                raise UserNotExistsError
            body = request.get_json()
            name = body.get('name')
            author = body.get('author')
            description = body.get('description')
            text = body.get('days')
            course = Courses.query.filter_by(name=name, author=author, description=description, added_by=user_id).first()
            if course is not None:
                output1 = []
                for t in text:
                    days = add_days(course_id=course.id, text=t)
                    output1.append(days)
                db.session.add_all(output1)
                db.session.commit()
                return {'message': 'Days added'}, 200

            new_course = Courses(name=name, author=author, description=description, added_by=user_id)
            db.session.add(new_course)
            db.session.commit()
            new_course.created_date = dt.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
            db.session.commit()
            output1 = []
            for t in text:
                days = add_days(course_id=new_course.id, text=t)
                output1.append(days)
            db.session.add_all(output1)
            db.session.commit()
            return {'message': "Course created successfully", 'id': str(new_course.id)}, 200
        except UserNotExistsError:
            raise BadRequest('User with id {} not exists'.format(user_id))
        except SchemaValidationError:
            raise BadRequest('Fields not filled')
        except NoAuthorizationError:
            raise UnauthorizedError
        except WrongTokenError:
            raise BadTokenError
        except UnauthorizedError:
            raise BadRequest('Token is missing')
        except BadTokenError:
            raise BadRequest('Token is invalid')
        except InternalServerError:
            db.session.rollback()
            raise BadRequest(errors['InternalServerError']['message'])


class UpdatingCourse(Resource):
    @jwt_required
    def get(self, id):
        """
        Retrieving one course
        :param id: course id
        :return: returns the course details of course of id "id" else raises Not found 404 error
                    if course isn't present
        """
        try:
            user_id = get_jwt_identity()
            if user_id is None:
                raise UnauthorizedError
            if not User.query.filter_by(id=user_id).first():
                raise UserNotExistsError
            course = Courses.query.filter_by(id=id, added_by=user_id).first()
            if not course:
                return {'message': 'Course not found'}, 404
            output = course_schema.dump(course)
            return output
        except UserNotExistsError:
            raise BadRequest('User with id {} not exists'.format(user_id))
        except WrongTokenError:
            raise BadTokenError
        except UnauthorizedError:
            raise BadRequest('Token is missing')
        except BadTokenError:
            raise BadRequest('Token is invalid')
        except InternalServerError:
            db.session.rollback()
            raise BadRequest(errors['InternalServerError']['message'])

    @jwt_required
    def delete(self, id):
        """
        Deleting a course.
        :param id: course id
        :return: success when course is deleted else raises Not found 404 error if course not found
        """
        try:
            user_id = get_jwt_identity()
            if user_id is None:
                raise UnauthorizedError
            if not User.query.filter_by(id=user_id).first():
                raise UserNotExistsError
            course = Courses.query.filter_by(id=id, added_by=user_id).first()
            if not course:
                return {'message': "Not found"}, 404
            delivery_paused = Delivary.query.filter_by(course_id=id, status='PAUSED').all()
            delivery_scheduled = Delivary.query.filter_by(course_id=id, status='SCHEDULED').all()
            if delivery_paused or delivery_scheduled:
                return {'message': f"The group '{course.name}' cannot be deleted as it is scheduled"}, 400
            days = course.days
            for i in range(len(days)):
                db.session.delete(days[i])
                db.session.commit()
            db.session.delete(course)
            db.session.commit()
            return {'message': 'Deleted successfully'}, 200
        except UserNotExistsError:
            raise BadRequest('User with id {} not exists'.format(user_id))
        except WrongTokenError:
            raise BadTokenError
        except UnauthorizedError:
            raise BadRequest('Token is missing')
        except BadTokenError:
            raise BadRequest('Token is invalid')
        except InternalServerError:
            db.session.rollback()
            raise BadRequest(errors['InternalServerError']['message'])

    @jwt_required
    @ns_course.expect(api.model('add days in update course', {'days': fields.List(fields.Nested(days_of_courses, skip_none=True))}))
    def put(self, id):
        """
        Update course here
        :param id: is course id
        :return: updated course with days
        """
        try:
            user_id = get_jwt_identity()
            if user_id is None:
                raise UnauthorizedError
            if not User.query.filter_by(id=user_id).first():
                raise UserNotExistsError
            courses = Courses.query.filter_by(id=id, added_by=user_id).first()
            if not courses:
                return {'message': 'Course not found'}, 404
            delivery_paused = Delivary.query.filter_by(course_id=id, status='PAUSED').all()
            delivery_scheduled = Delivary.query.filter_by(course_id=id, status='SCHEDULED').all()
            if delivery_paused or delivery_scheduled:
                return {'message': f"The group '{courses.name}' cannot be deleted as it is scheduled"}, 400
            body = request.get_json()
            if body is None:
                db.session.rollback()
                raise SchemaValidationError
#            courses.name = body.get('name')
#            courses.author = body.get('author')
#            courses.description = body.get('description')
            courses.updated_date = dt.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
            db.session.commit()
            text = body.get('days')
            output1 = []
            for t in text:
                days = add_days(course_id=id, text=t)
                output1.append(days)
            db.session.add_all(output1)
            db.session.commit()
            return {'message': 'Update Successful'}, 200
        except UserNotExistsError:
            raise BadRequest('User with id {} not exists'.format(user_id))
        except WrongTokenError:
            raise BadRequest(errors['BadTokenError']['message'])
        except SchemaValidationError:
            e = errors['SchemaValidationError']['message']
            raise BadRequest(e)
        except TypeError:
            e = errors['SchemaValidationError']['message']
            raise BadRequest(e)
        except UnauthorizedError:
            raise BadRequest('Token is missing')
        except BadTokenError:
            raise BadRequest('Token is invalid')
        except InternalServerError:
            db.session.rollback()
            raise BadRequest(errors['InternalServerError']['message'])


class OperationDays(Resource):
    @ns_course.expect(days_of_courses)
    #@ns_course.doc(params={'uploadfile': {'description': 'uploadfile', 'in': 'formdata', 'type': 'file'}})
    @jwt_required
    def put(self, c_id, day):
        """
        Updating Day
        :param c_id: is course id
        :param day: is day number present in course id
        :return: update the particular day if present in course of id else returns "Day not found"
        """
        try:
            user_id = get_jwt_identity()
            course = Courses.query.filter_by(id=c_id, added_by=user_id).first()
            if not course:
                raise BadRequest('Course not found!!')
            ds = Days.query.filter_by(day=day, course_id=c_id).first()
            if not ds:
                raise BadRequest('Day not found')
            delivery_paused = Delivary.query.filter_by(course_id=id, status='PAUSED').all()
            delivery_scheduled = Delivary.query.filter_by(course_id=id, status='SCHEDULED').all()
            if delivery_paused or delivery_scheduled:
                return {'message': f"The group '{course.name}' cannot be deleted as it is scheduled"}, 400
            body = request.get_json()
            ds.text = body['text']
            questions = body['questions']
            if questions == [] or questions is None:
                ds.updated_date = dt.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
                db.session.commit()
                return {'message': 'success'}, 201
            out = []
            for q in questions:
                if ds.questions is None:
                    qes = 1
                else:
                    qes = len(ds.questions) + 1
                ques = add_question(course_id=c_id, day_id=ds.id, text=q)
                ques.question_number = qes
                out.append(ques)
            db.session.add_all(out)
            db.session.commit()
            ds.updated_date = dt.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
            db.session.commit()
            return {'message': 'success'}, 200
        except InternalServerError:
            db.session.rollback()
            raise BadRequest(errors['InternalServerError']['message'])

    @jwt_required
    def delete(self, c_id, day):
        """
        Deleting Day
        :param c_id: is course id
        :param day: is a day which you want to delete
        :return: if day is in course it deletes the day else returns not found
        """
        try:
            user_id = get_jwt_identity()
            if not User.query.get(user_id):
                raise UserNotExistsError
            course = Courses.query.filter_by(id=c_id, added_by=user_id).first()
            if not course:
                raise BadRequest('Course not found')
            delivery_paused = Delivary.query.filter_by(course_id=c_id, status='PAUSED').all()
            delivery_scheduled = Delivary.query.filter_by(course_id=c_id, status='SCHEDULED').all()
            if delivery_paused or delivery_scheduled:
                return {'message': f"The group '{course.name}' cannot be deleted as it is scheduled"}, 400
            ds = Days.query.filter_by(day=day, course_id=course.id).first()
            if not ds:
                raise BadRequest('Days Not found')
            part_day = ds.day
            for d in course.days:
                if d.day < part_day:
                    continue
                elif d.day > part_day:
                    d.day = d.day - 1
                    db.session.commit()
                elif d.day == part_day:
                    db.session.delete(ds)
                    db.session.commit()
            return {'message': "success"}, 201

        except UserNotExistsError:
            raise BadRequest(f'User with id {user_id} not exists')
        except InternalServerError:
            db.session.rollback()
            raise BadRequest(errors['InternalServerError']['message'])


class OperationQuestions(Resource):
    @jwt_required
    def delete(self, c_id, day, q_id):
        """
        Deleting the Questions
        :param c_id: course id
        :param day: day number
        :param q_id: question id
        :return: success if the question of id "q_id" is deleted
        """
        try:
            user_id = get_jwt_identity()
            if not User.query.get(user_id):
                raise BadRequest(f"User with id {user_id} not exist's")
            course = Courses.query.filter_by(id=c_id, added_by=user_id).first()
            if not course:
                raise BadRequest('Course not found!')
            delivery_paused = Delivary.query.filter_by(course_id=id, status='PAUSED').all()
            delivery_scheduled = Delivary.query.filter_by(course_id=id, status='SCHEDULED').all()
            if delivery_paused or delivery_scheduled:
                return {'message': f"The group '{course.name}' cannot be deleted as it is scheduled"}, 400
            days = Days.query.filter_by(day=day, course_id=c_id).first()
            if not days:
                raise BadRequest('Day not found!')
            question = Questions.query.filter_by(id=q_id, day_id=days.id).first()
            number = question.question_number
            if not question:
                db.session.rollback()
                raise BadRequest('Question not found!')
            for q in days.questions:
                if q.question_number < number:
                    continue
                elif q.question_number > number:
                    q.question_number -= 1
                    db.session.commit()
                else:
                    db.session.delete(question)
                    db.session.commit()
            return {'message': 'success'}, 200
        except InternalServerError:
            db.session.rollback()
            raise BadRequest(errors['InternalServerError']['message'])

    @jwt_required
    @ns_course.expect(questions)
    def put(self, c_id, day, q_id):
        """
        Updating question
        :param c_id: course id
        :param day: day number
        :param q_id: question id
        :return: success when question of id "q_id" is updated
        """
        try:
            user_id = get_jwt_identity()
            if not User.query.get(user_id):
                raise BadRequest(f"User with id {user_id} not exist's")
            course = Courses.query.filter_by(id=c_id, added_by=user_id).first()
            if not course:
                raise BadRequest('Course not found!')
            delivery_paused = Delivary.query.filter_by(course_id=id, status='PAUSED').all()
            delivery_scheduled = Delivary.query.filter_by(course_id=id, status='SCHEDULED').all()
            if delivery_paused or delivery_scheduled:
                return {'message': f"The group '{course.name}' cannot be deleted as it is scheduled"}, 400
            days = Days.query.filter_by(day=day, course_id=c_id).first()
            if not days:
                raise BadRequest('Day not found!')
            question = Questions.query.filter_by(id=q_id, day_id=days.id).first()
            if not question:
                raise BadRequest('Question not found!')
            body = request.get_json()
            if not body or body == None or body == {}:
                raise BadRequest(errors['SchemaValidationError']['message'])
            question.text = body['question']
            question.type = body['type']
            question.correct_answer = body['correct_answer']
            question.updated_date = dt.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
            db.session.commit()
            return {'message': "success"}, 200
        except InternalServerError:
            db.session.rollback()
            raise BadRequest(errors['InternalServerError']['message'])


class UploadFiles(Resource):

    @jwt_required
    def get(self):
        files_data = FileUpload.query.all()
        output = file_schemas.dump(files_data)
        return output

    @jwt_required
    #@ns_course.doc({'uploadfile':'formdata'})
    @ns_course.expect(files)
    def post(self):
        """
        Save the uploaded file
        :param course_id: integer
        :param day: integer
        :return:
        """
        try:
            user_id = get_jwt_identity()
            if not User.query.get(user_id):
                raise BadRequest(f"User with id {user_id} not exist's")
            args = files.parse_args()
            course_id = args.get('course_id')
            day = args.get('day')
            course = Courses.query.get(course_id)
            if not course:
                return {'message':'Course not found'}, 404
            days = Days.query.filter_by(course_id=course_id, day=day).first()
            if not days:
                return {'message':'Day not found'}, 404
            if not 'uploadfile' in request.files:
                pass
            file = request.files['uploadfile']
            if file.filename == '':
                pass
            if not file and not allowed_file(file.filename):
                return {'message':"choose file of correct extension"}, 400
            filename = secure_filename(file.filename)
            file.save(os.path.join(config.UPLOAD_FOLDER,filename))
            object_name = filename +  '_day_' + str(days.day) + '_course_' + course.name + '.' +\
                          filename.rsplit('.',1)[1]
            upload_file(
                file_name=os.path.join(config.UPLOAD_FOLDER,filename),
                bucket=config.AWS_BUCKET,
                object_name=object_name,
                content_type=file.content_type
            )
            #presigned_url = create_presigned_url(bucket_name=config.AWS_BUCKET,object_name=object_name)
            f = FileUpload(file_name=object_name,course_id=course_id,day_id=days.id,day=day)
            db.session.add(f)
            db.session.commit()
            return {'message':'success'}, 200
        except InternalServerError as e:
            return {'message':str(e)}, 400

class UpdateFile(Resource):

    @jwt_required
    def delete(self,id):
        """
        Remove file
        :param id: file_id
        :return:
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise BadRequest(f"User with id {user_id} not exist's")
            file_ = FileUpload.query.get(id)
            if not file_:
                return {'message':"File not found!!"}, 404
            db.session.delete(file_)
            db.session.commit()
            return {'message':'success'}, 200
        except InternalServerError as e:
            return {'message': str(e)}

