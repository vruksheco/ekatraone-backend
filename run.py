"""
The main app where all the routes are initiated here and runs the flask app
"""

from resources.auth import *
from resources.reset import *
from resources.userdetails import *
from resources.course import *
from resources.groups import *
from resources.delivery import *
from resources.dashboard_api import *
from resources.responding_whatsapp import *

ns_auth.add_resource(Signup, '/signup')
ns_auth.add_resource(Login, '/login')
ns_auth.add_resource(Forgot, '/forgot')
ns_auth.add_resource(Reset, '/reset/<token>')
ns_user.add_resource(Details, '/details')
ns_user.add_resource(UpdateDetails, '/details/<int:id>')
ns_course.add_resource(CourseDetails, '/')
ns_course.add_resource(UpdatingCourse, '/<int:id>')
ns_course.add_resource(OperationDays, '/<int:c_id>/<int:day>')
ns_course.add_resource(OperationQuestions, '/<int:c_id>/<int:day>/<q_id>')
ns_course.add_resource(UploadFiles,'/upload_file/')
ns_course.add_resource(UpdateFile,'/update_file/<int:id>')
ns_user_group.add_resource(AddGroups, '/')
ns_user_group.add_resource(UpdateGroups, '/<int:id>')
ns_user_group.add_resource(OperationStudents, '/<int:g_id>/<int:s_id>/')
ns_delivery.add_resource(CreateDelivary, '/group/<int:g_id>/<int:c_id>/')
ns_delivery.add_resource(GetDelivery, '/retrieve-delivery')
ns_delivery.add_resource(OperationDelivery, '/<int:id>/delete_delivery')
ns_delivery.add_resource(PauseDelivery, '/<int:id>/pause_delivery')
ns_delivery.add_resource(StopDelivery, '/<int:id>/stop_delivery')
ns_delivery.add_resource(ReScheduleDelivery, '/<int:id>/schedule_delivery')
ns_dashboard.add_resource(DashboardAPI, '/dashboard')
ns_dashboard.add_resource(GraphData, '/data')
ns_whatsapp.add_resource(WhatsappHistory, '/whatsapp_history/<number>')

@app.cli.command('resetdb')
def reset_db():
    """
    reset the database here
    :return:
    """
    db.drop_all()
    db.create_all()
    print("DB resetted successfully")
    return "DB resetted"

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=80)
