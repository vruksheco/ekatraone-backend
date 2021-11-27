"""
Schedule Delivery
"""


from services.sms_service import *
from database.definations import *
import pytz

class GetDelivery(Resource):
    @jwt_required
    def get(self):
        """
        Get all the deliveries added by user
        :return: success when it returns all the deliveries
        """
        try:
            user_id = get_jwt_identity()
            if not User.query.get(user_id):
                raise UserNotExistsError
            delivary = Delivary.query.filter_by(added_by=user_id).order_by(Delivary.id).all()
            output = []
            for d in delivary:
                c_name = Courses.query.get(d.course_id)
                g_name = Groups.query.get(d.group_id)
                if c_name is None or g_name is None:
                    continue
                if str(d.status).lower() == 'stopped':
                    continue
                d_data = {}
                d_data['id'] = d.id
                d_data['group_id'] = d.group_id
                d_data['group_name'] = g_name.name
                d_data['course_id'] = d.course_id
                d_data['course_name'] = c_name.name
                d_data['day_id'] = d.day_id
                d_data['added_by'] = d.added_by
                d_data['status'] = d.status
                d_data['scheduled_time'] = str(d.scheduled_time)
                output.append(d_data)
            return {'deliveries': output}, 200
        except NoAuthorizationError:
            raise BadRequest("MISSING AUTHORIZATION HEADER")


class CreateDelivary(Resource):
    @jwt_required
    @ns_delivery.expect(delivery_field)
    def post(self, g_id, c_id):
        """
        Creating delivery
        :param g_id: group id
        :param c_id: course id
        :return: success if created
        """
        try:
            user_id = get_jwt_identity()
            if not User.query.get(user_id):
                raise UserNotExistsError
            course = Courses.query.filter_by(id=c_id, added_by=user_id).first()
            if not course:
                return {'message': 'Course Not Found!!'}, 404
            group = Groups.query.filter_by(id=g_id, added_by=user_id).first()
            if not group:
                return {'message': 'Group Not Found!!'}, 404
            body = request.get_json()
            delivery = Delivary(group_id=g_id, course_id=c_id, added_by=user_id)
            delivery.scheduled_time = dt.datetime.strptime(body['schedule_at'], r"%Y-%m-%d %H:%M")\
                .astimezone(tz=pytz.timezone('Asia/Kolkata'))
            delivery.status = 'SCHEDULED'
            delivery.created_date = dt.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
            db.session.add(delivery)
            db.session.commit()
            d = delivery.scheduled_time
            first_message = f"""Welcome to {course.name}. Let's start learning!"""
            last_message = f"""Thanks for enrolling this course"""
            students = group.students
            for student in students:
                if(student.channel=='Sms'):
                    send_sms(student.number, first_message)
                else:
                    send_whatsapp_message(student.number, first_message)
            # schedule the first message
            # first_message_id = str(delivery.id) + '-' + str(g_id) + '-' + str(c_id) + '-' + 'first_message'
            # scheduler.add_job(func=send_group_first_message, args=[first_message, students],
            #                   id=first_message_id,
            #                   trigger='date',
            #                   next_run_time=delivery.created_date + dt.timedelta(minutes=2),jobstore='db')
            # for days in course.days:
            #     message_id = str(delivery.id) + '-' + str(g_id) + '-' + str(c_id) + '-Day '+ str(days.day)
            #     next_run_time = d + dt.timedelta(days=days.day+1)
            #     print(next_run_time)
            #     scheduler.add_job(func=send_group_message,
            #                       id=message_id,
            #                       trigger='date',
            #                       next_run_time=next_run_time,
            #                       jobstore='db',
            #                       args=[students, days, days.day, course.name, days.text, days.questions])
            # schedule last message
            # last_message_id = str(delivery.id) + '-' + str(g_id) + '-' + str(c_id) + '-' + 'last_message'
            # scheduler.add_job(func=send_group_last_message, args=[last_message, students],
            #                   id=last_message_id,
            #                   trigger='date',
            #                   next_run_time=d + dt.timedelta(days=len(course.days)+2), jobstore='db')
            return {'message': "Success"}, 200
        except InternalServerError:
            db.session.rollback()
            raise BadRequest(errors['InternalServerError']['message'])


class OperationDelivery(Resource):
    @jwt_required
    def delete(self, id):
        """
        Deleting the delivery
        :param id: delivery id
        :return: success when delivery is deleted
        """
        try:
            user_id = get_jwt_identity()
            if user_id is None:
                raise UnauthorizedError
            elif not User.query.get(user_id):
                raise UserNotExistsError
            delivery = Delivary.query.filter_by(id=id, added_by=user_id).first()
            if not delivery:
                return {'message': 'Delivery not scheduled'}, 400
            db.session.delete(delivery)
            db.session.commit()
            return {'message': "success"}, 200
        except InternalServerError:
            raise BadRequest(errors['InternalServerError'])
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exist's")
        except UnauthorizedError:
            raise BadRequest('Token is missing')


class PauseDelivery(Resource):
    @jwt_required
    def put(self, id):
        """
        Pause the delivery
        :param id: delivery id
        :return: success when delivery status is PAUSED
        """
        try:
            user_id = get_jwt_identity()
            if not User.query.get(user_id):
                raise UserNotExistsError
            delivery = Delivary.query.filter_by(id=id, added_by=user_id).first()
            if not delivery:
                raise BadRequest('Delivery not found!!')
            delivery.status = 'PAUSED'
            delivery.updated_date = dt.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
            db.session.commit()
            course = Courses.query.get(delivery.course_id)
            group = Groups.query.get(delivery.group_id)
            ggg = ['first_message', 'last_message']
            for s in ggg:
                try:
                    job_id = str(delivery.id) + '-' + str(group.id) + '-' + str(course.id) + '-' + str(s)
                    scheduler.pause_job(job_id=job_id, jobstore='db')
                except JobLookupError:
                    continue
            for days in course.days:
                try:
                    job_id = str(delivery.id) + '-' + str(group.id) + '-' + str(course.id) + '-Day ' + str(days.day)
                    scheduler.pause_job(job_id=job_id,jobstore='db')
                except JobLookupError:
                    continue
            return {'message': 'success'}, 200
        except InternalServerError:
            db.session.rollback()
            raise BadRequest(errors['InternalServerError']['message'])
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exists")
        except JobLookupError:
            raise BadRequest(f'No job by the id of {job_id} was found')


class StopDelivery(Resource):
    @jwt_required
    def put(self, id):
        """
        Stop the delivery
        :param id: delivery id
        :return: success when delivery status is STOPPED
        """
        try:
            user_id = get_jwt_identity()
            if not User.query.get(user_id):
                raise UserNotExistsError
            delivery = Delivary.query.filter_by(id=id, added_by=user_id).first()
            if not delivery:
                raise BadRequest('Delivery not found!!')
            course = Courses.query.get(delivery.course_id)
            group = Groups.query.get(delivery.group_id)
            delivery.status = 'STOPPED'
            delivery.updated_date = dt.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
            db.session.commit()
            ggg = ['first_message', 'last_message']
            for s in ggg:
                try:
                    job_id = str(delivery.id) + '-' + str(group.id) + '-' + str(course.id) + '-' + str(s)
                    scheduler.remove_job(job_id=job_id, jobstore='db')
                except JobLookupError:
                    continue
            for days in course.days:
                try:
                    job_id = str(delivery.id) + '-' + str(group.id) + '-' + str(course.id) + '-Day ' + str(days.day)
                    scheduler.remove_job(job_id=job_id, jobstore='db')
                except JobLookupError:
                    continue
            return {'message': 'success'}, 200
        except InternalServerError:
            db.session.rollback()
            raise BadRequest(errors['InternalServerError']['message'])
        except JobLookupError:
            raise BadRequest(f'No job by the id of {job_id} was found')


class ReScheduleDelivery(Resource):
    @jwt_required
    def put(self, id):
        """
        Resume the delivery
        :param id: delivery id
        :return: success when the delivery is resume (status:-SCHEDULED)
        """
        try:
            user_id = get_jwt_identity()
            if not User.query.get(user_id):
                raise UserNotExistsError
            delivery = Delivary.query.filter_by(id=id, added_by=user_id).first()
            if not delivery:
                raise BadRequest('Delivery not found!!')
            course = Courses.query.get(delivery.course_id)
            if not course:
                raise BadRequest('Course not found!!')
            group = Groups.query.get(delivery.group_id)
            if not group:
                raise BadRequest('Group not found!!')
            if delivery.status != 'SCHEDULED':
                delivery.status = 'SCHEDULED'
                delivery.updated_date = dt.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
                db.session.commit()
                ggg = ['first_message','last_message']
                for s in ggg:
                    try:
                        job_id = str(delivery.id) + '-' + str(group.id) + '-' + str(course.id) + '-' + str(s)
                        scheduler.resume_job(job_id=job_id, jobstore='db')
                        scheduler.modify_job(job_id=job_id, jobstore='db',
                                             next_run_time=dt.datetime.now(tz=pytz.timezone('Asia/Kolkata'))\
                                                           +dt.timedelta(minutes=5))
                    except JobLookupError:
                        continue
                for days in course.days:
                    try:
                        job_id = str(delivery.id) + '-' + str(group.id) + '-' + str(course.id) + '-Day ' + str(days.day)
                        scheduler.resume_job(job_id=job_id, jobstore='db')
                        scheduler.modify_job(job_id=job_id, jobstore='db',
                                             next_run_time=dt.datetime.now(tz=pytz.timezone('Asia/Kolkata'))+\
                                                           dt.timedelta(minutes=5,days=days.day))
                    except JobLookupError:
                        continue
            else:
                return {'message': "Success"}, 200
            return {'message': 'success'}, 200
        except UserNotExistsError:
            raise BadRequest(f"User with id {user_id} not exist's")
        except InternalServerError:
            db.session.rollback()
            raise BadRequest(errors['InternalServerError']['message'])
