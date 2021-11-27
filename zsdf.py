from services.sms_service import send_group_message, send_whatsapp_message
from services.s3_services import create_presigned_url
from database.schemas_database import *

students = Students.query.all()

course = Courses.query.get(1)
days = course.days[1]

send_group_message(students, days, days.day, course.name, days.text, days.questions)

#p1 = create_presigned_url(bucket_name=config.AWS_BUCKET,object_name="black.jpg_day_2_course_coursename.jpg")
#p2 = create_presigned_url(bucket_name=config.AWS_BUCKET, object_name="Screenshot_30.png_day_2_course_coursename.png")

#presigned_url = [p1,p2]

#print(presigned_url)

#send_whatsapp_message(body="This is medis messages",
 #                     number="+919380169981",
  #                    presigned_url=presigned_url)

