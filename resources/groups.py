"""
About groups
"""

from database.schemas_database import *

class AddGroups(Resource):
    @jwt_required
    def get(self):
        """
        Retrieve all groups added by user
        :return: details of all groups added by user
        """
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            raise BadRequest(f"User with id {user_id} not exist's")
        groups = Groups.query.filter_by(added_by=user.id).order_by(Groups.id).all()
        if not groups:
            return {'message':"no groups"},404
        output = group_schemas.dump(groups)
        return {'groups': output}, 200

    @jwt_required
    @ns_user_group.expect(detail_groups)
    def post(self):
        """
        Creating a new user group
        :return: success when user creates new group
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(id=user_id).first()
            if not user:
                raise UserNotExistsError
            body = request.get_json()
            if not body:
                raise SchemaValidationError
            group = Groups.query.filter_by(name=body['name'],description=body['description'],added_by=user_id).first()
            if group:
                # add students
                output = []
                students = body['students']
                for student in students:
                    name = student['name']
                    number = student['number']
                    channel = student['channel']
                    is_subscribed = student['is_subscribed']
                    student_timezone = 'Asia/Kolkata'
                    country_code = student['country_code']
                    stud = Students(name=name, channel=channel, group_id=group.id, is_subscribed=is_subscribed)
                    stud.number = str(country_code) + str(number)
                    stud.created_date = dt.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
                    stud.timezone = student_timezone
                    stud.country_code = country_code
                    output.append(stud)
                db.session.add_all(output)
                db.session.commit()
                return {'message':'Students added'},200

            new_group = Groups(name=body['name'], description=body['description'], added_by=user_id)
            db.session.add(new_group)
            new_group.created_date = dt.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
            db.session.commit()
            # add students
            output = []
            students = body['students']
            for student in students:
                name = student['name']
                number = student['number']
                channel = student['channel']
                is_subscribed = student['is_subscribed']
                student_timezone = 'Asia/Kolkata'
                country_code = student['country_code']
                stud = Students(name=name,channel=channel,group_id=new_group.id, is_subscribed=is_subscribed)
                stud.number = str(country_code) + str(number)
                stud.created_date = dt.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
                stud.timezone = student_timezone
                stud.country_code = country_code
                output.append(stud)
            db.session.add_all(output)
            db.session.commit()
            return {'message':'Success','id':new_group.id},200
        except SchemaValidationError:
            raise BadRequest('Fields not filled')
        except UserNotExistsError:
            raise BadRequest('User with id {} not exists'.format(user_id))
        except NoAuthorizationError:
            raise UnauthorizedError
        except WrongTokenError:
            raise BadTokenError
        except UnauthorizedError:
            raise BadRequest('Token is missing')
        except BadTokenError:
            raise BadRequest('Token is invalid')
        except TypeError:
            e = errors['SchemaValidationError']['message']
            raise BadRequest(e)

class UpdateGroups(Resource):
    @jwt_required
    def get(self,id):
        """
        Retrieve one group
        :param id: group id
        :return: details of the group of id "id"
                   else raises an error if group of id not found
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(id=user_id).first()
            if not user:
                raise UserNotExistsError
            group = Groups.query.filter_by(id=id, added_by=user_id).first()
            if not group or group.is_deleted == True:
                return {'message':'Group not found'},404
            output = group_schema.dump(group)
            return output
        except UserNotExistsError:
            raise BadRequest('User with id {} not exists'.format(user_id))
        except NoAuthorizationError:
            raise UnauthorizedError
        except WrongTokenError:
            raise BadTokenError
        except UnauthorizedError:
            raise BadRequest('Token is missing')
        except BadTokenError:
            raise BadRequest('Token is invalid')

    @jwt_required
    def delete(self,id):
        """
        Delete Group
        :param id: group id
        :return: success when group is deleted else
                    raises an 404 error if group of id not found
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(id=user_id).first()
            if not user:
                raise UserNotExistsError
            group = Groups.query.filter_by(id=id,added_by=user_id).first()
            if not group:
                return {'message':'Group not found'},404
            delivery_paused = Delivary.query.filter_by(group_id=id, status='PAUSED').all()
            delivery_scheduled = Delivary.query.filter_by(group_id=id, status='SCHEDULED').all()
            if delivery_paused or delivery_scheduled:
                return {'message': f"The group '{group.name}' cannot be deleted as it is scheduled"}, 400
            students = group.students
            for student in students:
                db.session.delete(student)
                db.session.commit()
            db.session.delete(group)
            db.session.commit()
            return {'message':'Deleted successfully'},200
        except UserNotExistsError:
            raise BadRequest('User with id {} not exists'.format(user_id))
        except NoAuthorizationError:
            raise UnauthorizedError
        except WrongTokenError:
            raise BadTokenError
        except UnauthorizedError:
            raise BadRequest('Token is missing')
        except BadTokenError:
            raise BadRequest('Token is invalid')


    @jwt_required
    @ns_user_group.expect(detail_groups)
    def put(self,id):
        """
        Update the group
        :param id: group id
        :return: success when group updated successfully
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(id=user_id).first()
            if not user:
                raise UserNotExistsError
            group = Groups.query.filter_by(id=id,added_by=user_id).first()
            if not group:
                return {'message':'Group not found'},404
            delivery_paused = Delivary.query.filter_by(group_id=id, status='PAUSED').all()
            delivery_scheduled = Delivary.query.filter_by(group_id=id, status='SCHEDULED').all()
            if delivery_paused or delivery_scheduled:
                return {'message': f"The group '{group.name}' cannot be deleted as it is scheduled"}, 400
            body = request.get_json()
            if body is None:
                raise SchemaValidationError
            group.name = body.get('name')
            group.description = body.get('description')
            group.updated_date = dt.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
            students = body['students']
            output = []
            for student in students:
                name = student['name']
                number = student['number']
                channel = student['channel']
                is_subscribed = student['is_subscribed']
                student_timezone = 'Asia/Kolkata'
                country_code = student['country_code']
                students = Students(name=name,group_id=group.id, is_subscribed=is_subscribed)
                students.number = str(country_code) + str(number)
                students.timezone = student_timezone
                students.country_code = country_code
                students.channel = channel
                students.created_date = dt.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
                output.append(students)
            db.session.add_all(output)
            db.session.commit()
            return {'message':'Updated successfully'},200
        except SchemaValidationError:
            raise BadRequest('Fields not filled')
        except UserNotExistsError:
            raise BadRequest('User with id {} not exists'.format(user_id))
        except NoAuthorizationError:
            raise UnauthorizedError
        except WrongTokenError:
            raise BadTokenError
        except UnauthorizedError:
            raise BadRequest('Token is missing')
        except BadTokenError:
            raise BadRequest('Token is invalid')
        except TypeError:
            e = errors['SchemaValidationError']['message']
            raise BadRequest(e)



class OperationStudents(Resource):
    @jwt_required
    @ns_user_group.expect(students)
    def put(self,g_id,s_id):
        """
        Update the student in group
        :param g_id: group id
        :param s_id: student id
        :return: success if student is updated
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(id=user_id).first()
            if not user:
                raise UserNotExistsError
            group = Groups.query.filter_by(id=g_id,added_by=user_id).first()
            if not group:
                raise BadRequest(f'Group with id {g_id} not found')
            student = Students.query.filter_by(id=s_id,group_id=g_id).first()
            if not student:
                raise BadRequest(f'Student with id {s_id} not found')
            delivery_paused = Delivary.query.filter_by(group_id=g_id, status='PAUSED').all()
            delivery_scheduled = Delivary.query.filter_by(group_id=g_id, status='SCHEDULED').all()
            if delivery_paused or delivery_scheduled:
                return {'message': f"The group '{group.name}' cannot be deleted as it is scheduled"}, 400
            body = request.get_json()
            if not body or body is None or body == {}:
                raise SchemaValidationError
            student.name = body['name']
            student.number = body['number']
            student.channel = body['channel']
            student.is_subscribed = body['is_subscribed']
            student.timezone = 'Asia/Kolkata'
            student.country_code = body['country_code']
            student.updated_date = dt.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
            student.channel.updated_date = dt.datetime.now(tz=pytz.timezone('Asia/Kolkata'))
            db.session.commit()
            return {'message':"Student updated"},200
        except UserNotExistsError:
            raise BadRequest(f'User with id {user_id} not exists')
        except SchemaValidationError:
            raise BadRequest('Fields not filled')

    @jwt_required
    def delete(self,g_id,s_id):
        """
        Removing student in group
        :param g_id: group id
        :param s_id: student id
        :return: success if user deletes the student
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise BadRequest(f"User with id {user_id} not exist's")
            group = Groups.query.filter_by(id=g_id,added_by=user_id).first()
            if not group:
                raise BadRequest(f"Group with id {g_id} not found")
            student = Students.query.filter_by(id=s_id,group_id=g_id).first()
            if not student:
                raise BadRequest(f"Student with {s_id} not found")
            delivery_paused = Delivary.query.filter_by(group_id=g_id, status='PAUSED').all()
            delivery_scheduled = Delivary.query.filter_by(group_id=g_id, status='SCHEDULED').all()
            if delivery_paused or delivery_scheduled:
                return {'message': f"The group '{group.name}' cannot be deleted as it is scheduled"}, 400
            db.session.delete(student)
            db.session.commit()
            return {'message':"success"},200
        except InternalServerError as e:
            return {'message': str(e)}, 400


