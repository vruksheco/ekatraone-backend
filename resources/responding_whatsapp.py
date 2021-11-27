from database.schemas_database import *

# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client


# Your Account Sid and Auth Token from twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = config.ACCOUNT_SID
auth_token = config.AUTH_TOKEN
client = Client(account_sid, auth_token)


class WhatsappHistory(Resource):
    @jwt_required
    def get(self,number):
        """
        Get the whatsapp history
        :param number:
        :return:
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user:
                return {'message':'User not exists'}
            messages = client.messages.list(
                date_sent_after=dt.datetime(2020,12,30,0,0,0),
                to='whatsapp:'+str(number),
                from_='whatsapp:+12546553377',
                limit=100
            )
            output = []
            for record in messages:
                output.append({
                    "SID": record.sid,
                    "Media": str(record.media),
                    "body":record.body,
                    "from":record.from_,
                    "to":record.to,
                    "date_created":str(record.date_created),
                    "date_sent":str(record.date_sent),
                    "date_updated": str(record.date_updated),
                    "status":record.status
                })
        except InternalServerError as e:
            return {'message':str(e)}, 400
        return output