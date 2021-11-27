# Ekatra-Backend

## Usage

Uses flask and python

For `SWAGGER UI` I used `flask-restx`.

The requirements for using this project are 

```text
APScheduler==3.6.3 --> for scheduling deliveries
Flask==1.1.2 --> Main framework
Flask-Bcrypt==0.7.1 --> generating and checking password
Flask-Cors==3.0.9 --> Enabling the CORS policy
Flask-JWT-Extended==3.24.1 --> For JWT tokens
Flask-Mail==0.9.1 --> For sending Emails
flask-restx==0.2.0 --> SWAGGER UI
Flask-SQLAlchemy==2.4.4 --> For database URI
gunicorn==20.0.4 --> For deploying in heroku
psycopg2==2.8.5 --> Supported for POSTGRESql
python-dotenv==0.14.0 --> Loading .env & .flaskenv files
pytz==2020.1 --> Converting timezones
twilio==6.45.1 --> For SMS and Whatsapp messages
```

You can install all the modules above shown using `pip`.

To open the swagger ui, go to the url shown below

**`https://ekatra-backend.herokuapp.com/`**

The above url redirects to `SWAGGER UI` of `EKATRA-BACKEND`

**All responses will have in the form of**

```json
{
  "message": "Description of what happened for eg:- success"
}
```

For Authorization header in `SWAGGER UI` I have built the authorizations in my `app.py`:

```python
authorizations = {
    'Authorization': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}
``` 

Here `Authorization` is the `name` of that particular Authorization of type `apikey` which will be located in `header`.

After you can check `modules_and_libraries.py` file where I have imported all the modules, 
including `flask and flask restx`

This is how I have initialized my app in `app.py` file

```text
# Initialize app
app = Flask(__name__)

# Enable the CORS policy
CORS(app=app)
cors = CORS(app, resources={
    r"/*":{
        "origins":"*"
    }
})

# Initializing the API
api = Api(app, version='2.0', title='ekatra-backend', description='UserDetails',authorizations=authorizations,
          security='Authorization', errors=errors, prefix='/api')

# Here Authorization is that which is defined above and I have given the type of security as the name of the 
# authorization as menctioned above
```

Before going further Let's check how the API's I have designed and what all the stuff I have done.

## Authentication and Authorization & forgot/reset password

**For Authentication and authorization I used the `JWT tokens` using `flask-jwt-extended` module.**

### Registration of User (Signup)

**Defination**  ` POST /auth/signup` 

**Arguments**

- `name:` User name
- `email:` Email of user should be unique
- `contact:` contact number of user
- `password:` user password

**Json format**

```json
{
  "name": "name",
  "email": "email@gmail.com",
  "contact": "9999999999",
  "password": "password"
}
```

In `auth.py` in `resources` folder

```text
class Signup(Resource):
    @ns_auth.expect(signup)
    def post(self):
        body = request.get_json() # get body in response
        if body is None:
            raise SchemaValidationError
        user_name = body.get('name')
        user_email = body.get('email')
        user_contact = body.get('contact')
        user_password = body.get('password')
        if User.query.filter_by(email=user_email).first(): 
            # First to checks that user with that email is present in database 
            # If the user is exists, then it gives you EmailAlreadyExistsError
            raise EmailAlreadyExistsError  
        # If user not present it creates a new user with email, API creates the new user.
        user = User(name=user_name, email=user_email, contact=user_contact, password=user_password, is_admin=False)
        user.hash_password()
        db.session.add(user)
        user.created_date = dt.datetime.now()
        db.session.commit()
        return {'message':"Success", 'id':str(user.id)}, 200
```

**Responses**
- `200 OK` on success
- `400 BAD REQUEST` if any fields are missing

### Login 

**Defination**  ` POST /auth/login` 

**Arguments**

- `email:` Email of the user
- `password:` User should enter correct password 

**Jsonformat** 

```json
{
  "email": "email@gmail.com",
  "password": "password"
}
```

In `auth.py` in `resources` folder.

```text
class Login(Resource):
    @ns_auth.expect(login)
    def post(self):
        body = request.get_json()
        if body is None:
            raise SchemaValidationError
        email = body.get('email')
        password = body.get('password')
        user = User.query.filter_by(email=body.get('email')).first()
        # first checks the user is present in database. If not present 
        # Gives you user not exists error
        if not user:
            raise UserNotExistsError
        # If user is present,  check the password in body with password stored in database
        # If the password not matched, gives you Badrequest error
        if not user.check_password(password=password):
            raise BadRequest('Either email or password is incorrect')
        # If the password matches with password in database, we have to create token
        # using create access token with identity as `user.id` and return to response body.
        id = user.id
        expires = dt.timedelta(days=config.EXPIRY_END_DAYS)
        access_token = create_access_token(identity=str(id), expires_delta=expires)
        user.token = access_token
        db.session.commit()
            return {'message': 'success', 'token':access_token}, 200
```

**Responses**
- `200 OK` on success
- `400 BAD REQUEST` if any fields are missing or if the password is incorrect

### Forgot password

**Defination**  ` POST /auth/forgot` 

**Arguments**

- `email:` Email of the user

**Jsonformat**

```json
{
  "email": "email@gmail.com"
}
```

**Responses**
- `200 OK` on success
- `400 BAD REQUEST` if any fields are missing
- `404 NOT FOUND` if the email is not found in database

**Response body**

```json
{
  "message": "success",
  "token": "<token generated for reset password>"
}
``` 
for `200 OK`

###Reset password
**Defination**  ` POST /auth/reset<token>` 

**Arguments**

- `new-password: ` Enter the new password here
- `confirm-password: ` retype the same password

**JsonFormat**

```json
{
  "new-password": "password",
  "conform-password": "retype the password"
}
```

**Responses**
- `200 OK` on success
- `400 BAD REQUEST` if password and confirm-password fields not matched

**Response body**

for `200 OK`
```json
{
  "message": "password reset success",
  "token": "<token generated for reset password>"
}
``` 

## Course related API's

### Create course

**Defination** `POST /course/` `#Headers -H Authorization:Bearer <JWTtoken>`

**Arguments**

- `name: `Course name
- `author: `Author of the course
- `description: `Description of the course
- `days: `List of the days in course Here questions may be `None` if that day has no particular questions.

for `days` fields, the Arguments are shown below.
- `day: ` The day number for the course.
- `text: `The content of that particular day
- `questions: `List of the questions for the particular day, Here questions may be `None` if that day has no particular questions.

for `questions` fields, the Arguments are shown below

- `question: `The question for that day in that particular course
- `type: `The type of the question
- `correct_answer: `correct answer for that question.

**Below shown is basic model for creating course.**

```json
{
  "name": "coursename", 
  "author": "courseauthor",
  "description": "description",
  "days": [
      {
         "day": "day num (readonly)",
         "text": "day-content",
         "questions": [
            {
              "question": "question",
              "type": "question type",
              "correct-answer": "correct-answer"
            }       
         ]
      }
   ]
}
```
In the `day` field `(readonly)` means no need to add content to that field while creating the course.

**Responses**
- `200 OK` on success
- `400 BAD REQUEST` If any field is missing

**Response body**

for `200 OK`
```json
{
  "message": "success"
}
``` 

### Retrieve course

**Defination** `GET /course/` `#Headers -H Authorization:Bearer <JWTtoken>`

**Response**

- `200 OK` on success

```json
[
   {
      "id": 1,
      "name": "Python", 
      "author": "Ekatra",
      "description": "description",
      "days": [
          {
             "day": 1,
             "text": "Introduction",
             "questions": []
          },
          {
             "day": 2,
             "text": "print hello world",
             "questions": [
                {
                  "question": "What is print statement?",
                  "type": "Q/A",
                  "correct-answer": "Python statement displays the variable or any character."
                }       
             ]
          }
      ]
   },
   {
      "id": 2,
      "name": "Javascript", 
      "author": "Ekatra",
      "description": "description",
      "days": [
          {
             "day": 1,
             "text": "Introduction",
             "questions": []
          },
          {
             "day": 2,
             "text": "print hello world",
             "questions": [
                {
                  "question": "What is print statement?",
                  "type": "Q/A",
                  "correct-answer": "Python statement displays the variable or any character."
                }       
             ]
          }
      ]
   }
]
```

- `404 NOT FOUND` If courses is not found in database

```json
{
  "message": "Courses not found!!"
}
``` 

### Get course

**Defination** `GET /course/<int:id>` `#Headers -H Authorization:Bearer <JWTtoken>`

**Responses**

- `200 OK` on success

```json
{
   "id": 1,
   "name": "Python", 
   "author": "Ekatra",
   "description": "description",
   "days": [
      {
         "day": 1,
         "text": "Introduction",
         "questions": []
      },
      {
         "day": 2,
         "text": "print hello world",
         "questions": [
            {
              "question": "What is print statement?",
              "type": "Q/A",
              "correct-answer": "Python statement displays the variable or any character."
            }       
         ]
      }
   ]
}
```

- `404 NOT FOUND` If the course of `id` not found in database.

```json
{
  "message": "Course Not found!!"
}
```

### Update Course

**Definitation** `PUT /course/<int:id>` `#Headers -H Authorization:Bearer <JWTtoken>`

You can add days and questions for the course with `id`.

**Arguments**

- `days: `List of the days in course Here questions may be `None` if that day has no particular questions.

for `days` fields, the Arguments are shown below.
- `day: ` The day number for the course.
- `text: `The content of that particular day
- `questions: `List of the questions for the particular day, Here questions may be `None` if that day has no particular questions.

for `questions` fields, the Arguments are shown below

- `question: `The question for that day in that particular course
- `type: `The type of the question
- `correct_answer: `correct answer for that question.

**Below shown is basic model for Update Course**

```json
{
  "days": [
    {
      "day": "day num (readonly)",
      "text": "string",
      "questions": [
        {
          "question": "string",
          "type": "string",
          "correct_answer": "string"
        }
      ]
    }
  ]
}
```

**Responses**

- `200 OK` on success

```json
{
  "message": "success"
}
```

- `404 NOT FOUND` If the course is not found in database

```json
{
  "message": "Course not found!!"
}
```

### Deleting Course

**Definitation** `DELETE /course/<int:id>` `#Headers -H Authorization:Bearer <JWTtoken>`

**Responses**

- `200 OK` on success

```json
{
  "message": "success"
}
```

- `404 NOT FOUND` If the course is not found in database.
```json
{
  "message": "Course Not found"
}
```

### Deleting Day

**Definitation** `DELETE /course/<int:c_id>/<int:day>` `#Headers -H Authorization:Bearer <JWTtoken>`

Here,
- `c_id` means `course id`.
- `day` means `day number`.

**Responses**

- `200 OK` on success

```json
{
  "message": "success"
}
```

- `404 NOT FOUND` for both if course or day not found in database.

*-* If course not found
```json
{
  "message": "Course not found!!"
}
```
*-* else Day is not found in course with `c_id`.
```json
{
  "message": "Day not found!!"
}
```

### Updating Day

**Definition `PUT /course/<int:c_id>/<int:day>` `#Headers -H Authorization:Bearer <JWTtoken>`

Here,
- `c_id` means `course id`.
- `day` means `day number`.

**Arguments**

- `day: ` The day number for the course.
- `text: `The content of that particular day
- `questions: `List of the questions for the particular day, Here questions may be `None` if that day has no particular questions.

for `questions` fields, the Arguments are shown below

- `question: `The question for that day in that particular course
- `type: `The type of the question
- `correct_answer: `correct answer for that question.

**Below shown is basic model for Updating Day**

```json
{
  "day": "day num (readonly)",
  "text": "string",
  "questions": [
    {
      "question": "string",
      "type": "string",
      "correct_answer": "string"
    }
  ]
}
```

**Responses**

- `200 OK` on success

```json
{
  "message": "success"
}
```

- `404 NOT FOUND` for both if course or day not found in database.

*-* If course not found
```json
{
  "message": "Course not found!!"
}
```
*-* else Day is not found in course with `c_id`.
```json
{
  "message": "Day not found!!"
}
```

### Deleting the question

**Definition** `DELETE /course/<int:c_id>/<int:day>/<int:q_id>` `#Headers -H Authorization:Bearer <JWTtoken>`

Here,
- `c_id` means `course id`.
- `day` means `day number`.
- `q_id` means `question id`.

**Responses**

- `200 OK` on success

```json
{
  "message": "success"
}
```

- `404 NOT FOUND` for both if course or day not found in database.

*-* If course not found
```json
{
  "message": "Course not found!!"
}
```
*-* else Day is not found in course with `c_id`.
```json
{
  "message": "Day not found!!"
}
```

*-* If question of `q_id` not found.

```json
{
  "message": "Question not found!!"
}
```

### Updating Question

**Definition** `PUT /course/<int:c_id>/<int:day>/<int:q_id>` `#Headers -H Authorization:Bearer <JWTtoken>`

**Arguments**

- `question: `The question for that day in that particular course
- `type: `The type of the question
- `correct_answer: `correct answer for that question.

**Below shown is basic model for Updating Question**


```json
{
  "question": "string",
  "type": "string",
  "correct_answer": "string"
}
```

**Responses**

- `200 OK` on success

```json
{
  "message": "success"
}
```

- `404 NOT FOUND` for both if course or day not found in database.

*-* If course not found
```json
{
  "message": "Course not found!!"
}
```
*-* else Day is not found in course with `c_id`.
```json
{
  "message": "Day not found!!"
}
```

*-* If question of `q_id` not found.

```json
{
  "message": "Question not found!!"
}
```

## Groups related API's

### Create Group

**Definition** `POST /group/` `#Headers -H Authorization:Bearer <JWTtoken>`

**Arguments**

- `name: `Name of the group
- `description: `group description
- `students: `List of all the students in group

for `students` field in group Arguments are:
- `name: `student's name
- `number: `student contact number with it's country code
- `channel: `student's subscribed any channel. channel may be `sms` or `whatsapp`.
- `timezone: `student's residing timezone
- `country_code: `(Optional) student's mobile country code.

**Below shown is the json format for creating group**

```json
{
  "name": "string",
  "description": "string",
  "students": [
    {
      "name": "name",
      "number": "+91999999999",
      "channel": "channelname",
      "is_subscribed": true,
      "timezone": "UTC",
      "country_code": "+1"
    }
  ]
}
```

**Responses**

- `200 OK` on success

```json
{
  "message": "success"
}
```

- `400 BAD REQUEST` If any field is missing

```json
{
  "message": "Some field is missing!!"
}
```

### Retrieve groups

**Definition** `GET /group/` `#Headers -H Authorization:Bearer <JWTtoken>`

**Responses**

- `200 OK` on success

```json
[
    {
      "id": 1,
      "name": "Group1",
      "description": "group1",
      "students": [
        {
          "name": "Tejas",
          "number": "+919380169981",
          "channel": "whatsapp",
          "is_subscribed": true,
          "timezone": "Asia/Kolkata",
          "country_code": "+91"
        },
        {
          "name": "Amit",
          "number": "+919113029491",
          "channel": "sms",
          "is_subscribed": true,
          "timezone": "Asia/Kolkata",
          "country_code": "+91"
        }
      ]
    },
    {
      "id": 2,
      "name": "Group2",
      "description": "group2",
      "students": [
        {
          "name": "Tejas",
          "number": "+919380169981",
          "channel": "whatsapp",
          "is_subscribed": true,
          "timezone": "Asia/Kolkata",
          "country_code": "+91"
        },
        {
          "name": "Amit",
          "number": "+919113029491",
          "channel": "sms",
          "is_subscribed": true,
          "timezone": "Asia/Kolkata",
          "country_code": "+91"
        },
        {
          "name": "Sreevastav",
          "number": "+916360157821",
          "channel": "sms",
          "is_subscribed": true,
          "timezone": "Asia/Kolkata",
          "country_code": "+91"
        }
      ]
    }
]
```

- `404 NOT FOUND` If group is not found

```json
{
  "message": "Groups not found!!"
}
```


### Get group

**Definition** `GET /group/<int:id>` `#Headers -H Authorization:Bearer <JWTtoken>`

Here
- `id: `is group id

**Responses**

- `200 OK` on success

```json
{
  "id": 1,
  "name": "Group1",
  "description": "group1",
  "students": [
    {
      "name": "Tejas",
      "number": "+919380169981",
      "channel": "whatsapp",
      "is_subscribed": true,
      "timezone": "Asia/Kolkata",
      "country_code": "+91"
    },
    {
      "name": "Amit",
      "number": "+919113029491",
      "channel": "sms",
      "is_subscribed": true,
      "timezone": "Asia/Kolkata",
      "country_code": "+91"
    }
  ]
}
```

- `404 NOT FOUND` If group not found in database

```json
{
  "message": "Group not found!!"
}
```

### Update group

**Definition** `PUT /group/<int:id>` `#Headers -H Authorization:Bearer <JWTtoken>`

Here 
- `id: `is group id

The input json format for updating group is same as the creation of group

**Responses**

- `200 OK` on success

```json
{
  "message": "success"
}
```

- `404 NOT FOUND` If the group is not found in database

```json
{
  "message": "Group of id not found"
}
```

### Deleting 

**Definition** `DELETE /group/<int:id>` `#Headers -H Authorization:Bearer <JWTtoken>`

Here
- `id: `is group id

**Responses**

- `200 OK` on success

```json
{
  "message": "success"
}
```

- `404 NOT FOUND` If the group is not found in database

```json
{
  "message": "Group of id not found"
}
```

### Removing student in group

**Definition `DELETE /group/<int:g_id>/<int:s_id>` `#Headers -H Authorization:Bearer <JWTtoken>`

Here
- `g_id: `is group id
- `s_id: `is student id

**Responses**

- `200 OK` on success

```json
{
  "message": "success"
}
```

- `404 NOT FOUND` If the group is not found in database

```json
{
  "message": "Group of id not found"
}
```

- `404 NOT FOUND` If the sstudent is not found in database

```json
{
  "message": "Student not found"
}
```

### Updating student details

**Definition `DELETE /group/<int:g_id>/<int:s_id>` `#Headers -H Authorization:Bearer <JWTtoken>`

Here
- `g_id: `is group id
- `s_id: `is student id

**Arguments**

- `name: `student's name
- `number: `student contact number with it's country code
- `channel: `student's subscribed any channel. channel may be `sms` or `whatsapp`.
- `timezone: `student's residing timezone
- `country_code: `(Optional) student's mobile country code.

**Below shown is the json format for Updating student details**

**Responses**

- `200 OK` on success

```json
{
  "message": "success"
}
```

- `404 NOT FOUND` If the group is not found in database

```json
{
  "message": "Group of id not found"
}
```

- `404 NOT FOUND` If the sstudent is not found in database

```json
{
  "message": "Student not found"
}
```


## Delivery Scheduling API's

### Creating delivery

**Definition** `POST /delivery/group/<int:g_id>/<int:c_id>` `#Headers -H Authorization:Bearer <JWTtoken>`

Here
- `g_id: `is group id
- `c_id: `is course id

**Arguments**

- `schedule_at: `schedules the course at particular date and at particular time

**Below shown is json format input for Creating delivery schedule.**

```json
{
  "schedule_at": "YYYY-MM-DD HH:MM:SS"
}
```
 Here `YYYY-MM-DD` in `schedule_at` field represents format for date
 For example, `YYYY-MM-DD --> 2020-11-01`
 
 And `HH:MM:SS` in `schedule_at` field represents the time in 24 hours format
 For example, `HH:MM:SS --> 16:15:00`
 
 So, we can consider the example for `schedule_at` field as `YYYY-MM-DD HH:MM:SS --> 2020-11-01 16:15:00`.
 
 **Responses**
 
 - `200 OK` on success

```json
{
  "message": "success"
}
```

Here after creating the delivery, the status of the delivery will be `SCHEDULED` by default.
You can `PAUSE` `RESUME` and `STOP` the deliveries using the API's which will be shown below


### PAUSE, RESUME and STOP delivery

For PAUSE RESUME & STOP delivery the Definition will remains same

**Definition** `PUT /delivery/<int:id>` `#Headers -H Authorization:Bearer <JWTtoken>`

Here
- `id: `is delivery id

`PAUSE `pauses the delivery scheduled `status: PAUSED`
`RESUME `resumes the delivery schedule `status: SCHEDULED`
`STOP `terminates the scheduling delivery `status: STOPPED`

**Responses**

 - `200 OK` on success

```json
{
  "message": "success"
}
```

### Retrieve Deliveries

**Definition** `GET /retrieve-deliveries` `#Headers -H Authorization:Bearer <JWTtoken>`

**Responses**

- `200 OK` on success

```json
[
    {
      "id": 1,
      "group_id": 3,
      "group_name": "group3",
      "course_id": 1,
      "course_name": "Python",
      "day_id": 2,
      "added_by": 1,
      "status": "SCHEDULED",
      "scheduled_time": "2020-11-01 16:40:00"
    },
    {
      "id": 2,
      "group_id": 1,
      "group_name": "group1",
      "course_id": 3,
      "course_name": "Javascript",
      "day_id": 2,
      "added_by": 1,
      "status": "PAUSED",
      "scheduled_time": "2020-11-01 16:40:00"
    },
    {
      "id": 1,
      "group_id": 10,
      "group_name": "group10",
      "course_id": 1,
      "course_name": "Python",
      "day_id": 2,
      "added_by": 1,
      "status": "STOPED",
      "scheduled_time": "2020-11-01 16:40:00"
    }
]
```

