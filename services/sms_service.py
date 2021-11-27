"""
Send sms
"""
import config
from twilio.rest import Client
from modules_and_libraries import *
import urllib
import urllib.request
import urllib.parse
from database.definations import message_temp
from database.models import FileUpload
from services.s3_services import create_presigned_url, upload_file

account_sid = config.ACCOUNT_SID
auth_token = config.AUTH_TOKEN
messaging_service_sid = config.MESSAGING_SERVICE_SID
# number = '+12546553377'
# whatsapp_number = 'whatsapp:+12546553377'

client = Client(account_sid, auth_token)

# def send_sms(message,mobile,presigned_url=None):
#     """
#     Send sms
#     :param mobile: mobile number
#     :param message: body
#     :param country_code: country code eg:- +91 for India and +1 for USA
#     :return:
#     """
#     authkey = '317521AVt6zyGHU5f96b38cP1'
#     route = '4'
#     sender = 'VRUKSH'
#     mobiles = mobile + str(presigned_url)
#     # Prepare you post parameters
#     values = {
#         'authkey': authkey,
#         'mobiles': mobiles,
#         'message': message,
#         'sender': sender,
#         'route': route,
#         #'country': country_code
#     }
#     url = "http://api.msg91.com/api/sendhttp.php"  # API URL
#     postdata = urllib.parse.urlencode(values)  # URL encoding the data here.
#     postdata = postdata.encode('utf-8')
#     req = urllib.request.Request(url, postdata)
#     response = urllib.request.urlopen(req)
#     # output = response.read()  # Get Response
#     print(response)

# def send_whatsapp_message(body, number, presigned_url=None):
#     """
#     Send Whatsapp Message
#     :param body: Text Body
#     :param number: to desired whatsapp number eg:'whatsapp:+919939939393' (in string)
#     :return: success when message is sent
#     """
#     try:
#         if presigned_url is None:
#             media_url = []
#         else:
#             media_url = presigned_url
#         message = client.messages.create(
#             media_url=media_url,
#             from_=whatsapp_number,
#             body=body,
#             to='whatsapp:' + number)
#         print(message.sid)
#         print(body)
#         print("to -->" + str(number))
#         print('whatsapp')
#         print(dt.datetime.now())
#     except TwilioException as e:
#         print(e)
#     except TwilioRestException as e:
#         print(e)

def send_sms(number, message):
    client.messages.create(
        body=message,
        messaging_service_sid=os.environ.get('MESSAGING_SERVICE_SID'),
        to=number
    )
    return 'Done!' 

def send_whatsapp_message(number, message):
    client.messages.create(
        body = "Welcome to Vruksh!",
        from_=os.environ.get('from_whatsapp_number'),
        to='whatsapp:'+number
    )
    return 'Done!'

def send_group_message(students,days,day,c_name,topic,questions,presigned_url=None):
    details = [{"name": student.name,"number": student.number,"channel": student.channel} for student in students]
    days_detail = {'id':days.id,'day':days.day,'files':days.files}
    day_files = days_detail['files']
    if day_files:
        presigned_url = []
        for d in day_files:
            ff = FileUpload.query.filter_by(id=d.id).first()
            object_name = ff.file_name
            presigned_url.append(create_presigned_url(bucket_name=config.AWS_BUCKET,object_name=object_name))
    for dd in details:
        message = message_temp(name=dd['name'], day=day, course=c_name, text=topic, questions=questions)
        if str(dd['channel']).lower() == 'whatsapp':
            send_whatsapp_message(message, dd['number'],presigned_url)
        else:
            send_sms(message, dd['number'],presigned_url)

def send_group_last_message(message, students):
    for student in students:
        if str(student.channel).lower() == 'whatsapp':
            send_whatsapp_message(body=message, number=student.number)
        else:
            send_sms(message=message, mobile=student.number)

def send_group_first_message(message, students):
    for student in students:
        if str(student.channel).lower() == 'whatsapp':
            send_whatsapp_message(body=message, number=student.number)
        else:
            send_sms(message=message, mobile=student.number)


