"""
API for Dashboard pages
"""

from database.definations import *
from matplotlib import pyplot as plt
from io import BytesIO, StringIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


class DashboardAPI(Resource):
    @jwt_required
    def get(self):
        """
        :return: total number of courses students and subscribed students
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                raise UserNotExistsError
            courses = Courses.query.filter_by(added_by=user_id).all()
            groups = Groups.query.filter_by(added_by=user_id).all()
            out1 = [c.created_date if c.updated_date is None else c.updated_date for c in courses]
            out2 = [c.created_date if c.updated_date is None else c.updated_date for c in groups]
            out3 = [s.created_date if s.updated_date is None else s.updated_date for group in groups for s in \
                    group.students]
            if out1 == [] and out2 == [] and out3 == []:
                output, status = {
                    "Total_no_of_courses": 0,
                    "Last_updated_course": None,
                    "Total_no_of_users": 0,
                    "Last_updated_student": None,
                    "Total_groups": 0,
                    "Last_updated_group":None
                }, 200
            elif out2 == [] and out3 == []:
                output, status =  {
                    "Total_no_of_courses": len(courses),
                    "Last_updated_course": out1[-1].strftime("%d-%m-%Y %I:%M %p"),
                    "Total_no_of_users": 0,
                    "Last_updated_student": None,
                    "Total_groups": 0,
                    "Last_updated_group":None
                }, 200
            elif out1 == [] and out2 == []:
                output, status = {
                    "Total_no_of_courses": 0,
                    "Last_updated_course": None,
                    "Total_no_of_users": len(out3),
                    "Last_updated_student": out3[-1].strftime("%d-%m-%Y %I:%M %p"),
                    "Total_groups": 0,
                    "Last_updated_group":None
                }, 200
            elif out1 == [] and out3 == []:
                output, status = {
                    "Total_no_of_courses": 0,
                    "Last_updated_course": None,
                    "Total_no_of_users": 0,
                    "Last_updated_student": None,
                    "Total_groups": len(groups),
                    "Last_updated_group":out2[-1].strftime("%d-%m-%Y %I:%M %p")
                }, 200
            elif out1 == []:
                output, status = {
                    "Total_no_of_courses": 0,
                    "Last_updated_course": None,
                    "Total_no_of_users": len(out3),
                    "Last_updated_student": out3[-1].strftime("%d-%m-%Y %I:%M %p"),
                    "Total_groups": len(groups),
                    "Last_updated_group": out2[-1].strftime("%d-%m-%Y %I:%M %p")
                }, 200
            elif out2 == []:
                output, status = {
                    "Total_no_of_courses": len(courses),
                    "Last_updated_course": out1[-1].strftime("%d-%m-%Y %I:%M %p"),
                    "Total_no_of_users": len(out3),
                    "Last_updated_student": out3[-1].strftime("%d-%m-%Y %I:%M %p"),
                    "Total_groups": 0,
                    "Last_updated_group":None
                }, 200
            elif out3 == []:
                output, status = {
                    "Total_no_of_courses": len(courses),
                    "Last_updated_course": out1[-1].strftime("%d-%m-%Y %I:%M %p"),
                    "Total_no_of_users": 0,
                    "Last_updated_student": None,
                    "Total_groups": len(groups),
                    "Last_updated_group":out2[-1].strftime("%d-%m-%Y %I:%M %p")
                }, 200
            else:
                output, status = {
                        "Total_no_of_courses": len(courses),
                        "Last_updated_course": out1[-1].strftime("%d-%m-%Y %I:%M %p"),
                        "Total_no_of_users": len(out3),
                        "Last_updated_student": out3[-1].strftime("%d-%m-%Y %I:%M %p"),
                        "Total_groups": len(groups),
                        "Last_updated_group":out2[-1].strftime("%d-%m-%Y %I:%M %p")
                    }, 200
            return output, status
        except UserNotExistsError:
            raise BadRequest(f"User with {user_id} not exists")
        except InternalServerError:
            raise BadRequest(errors['InternalServerError']['message'])


class GraphData(Resource):
    @jwt_required
    def get(self):
        """
        gives list of courses and total users created in that particular time
        :return:
        """
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            raise UserNotExistsError
        courses = Courses.query.filter_by(added_by=user_id).all()
        if not courses:
            raise BadRequest('Courses not found!!')
        #months_list = config.monthsss
        lt = [0]*12
        data = 0
        for course in courses:
            s = course.created_date
            sy = s.strftime('%Y')
            if sy != dt.datetime.now().strftime('%Y'):
                if sy < dt.datetime.now().strftime('%Y'):
                    continue
            else:
                sm = s.strftime('%m')
                data += 1
                lt[int(sm)-1] = data
        groups = Groups.query.filter_by(added_by=user_id).all()
        if not groups:
            raise BadRequest("Groups not found!!")
        gt = [0]*12
        beta = 0
        for group in groups:
            for student in group.students:
                s = student.created_date
                sy = s.strftime('%Y')
                if sy != dt.datetime.now().strftime('%Y'):
                    if sy < dt.datetime.now().strftime('%Y'):
                        continue
                else:
                    sm = s.strftime('%m')
                    beta += 1
                    gt[int(sm)-1] = beta
        print(lt , gt)
        fig = Figure()
        months = ['Jan','Feb','Mar','April','May','Jun','July','Aug','Sept','Oct','Nov','Dec']
        plt.figure(1)
        plt.plot(lt,months)
        plt.ylabel("Y label")
        plt.xlabel("X label")
        plt.title("x and y")
        canvas = FigureCanvas(plt.figure(1))
        output = BytesIO()
        canvas.print_png(output)
        response = make_response(output.getvalue())
        response.mimitype = 'image/png'
        return response
