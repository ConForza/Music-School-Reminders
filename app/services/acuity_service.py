from app.models.student import Student
from app.models.lesson import Lesson
from app.models.payment import Payment

from app.config import ACUITY_USER_NAME
from app.config import ACUITY_API_KEY
from app.config import ACUITY_BASE_URL

import requests
from datetime import datetime as dt

headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

_students_by_email = {}


def fetch_appointments_for_calendar(calendar_id):
    today_date = dt.now().strftime("%B %d, %Y")

    parameters = {
            "minDate": today_date,
            "maxDate": today_date,
            "calendarID": calendar_id
        }

    response = requests.get(
            url=f"{ACUITY_BASE_URL}/appointments",
            auth=(ACUITY_USER_NAME, ACUITY_API_KEY),
            params=parameters,
            headers=headers
        )

    return response.json()


def lesson_from_api(result):
    email = result["email"]

    if email not in _students_by_email:
        _students_by_email[email] = Student(
            email=email,
            first_name=result["firstName"],
            surname=result["lastName"],
        )

    student = _students_by_email[email]

    payment = Payment(
        is_paid=result["paid"]
    )

    lesson = Lesson(
        id_=result["id"],
        date=result["datetime"],
        type_=result["type"],
        category=result["category"],
        duration=result["duration"],
        payment=payment
    )

    student.lessons.append(lesson)

    return lesson

results = fetch_appointments_for_calendar("1802796")
for result in results:
    lesson_from_api(result)

print(_students_by_email['hug.jenny22@gmail.com'].lessons)


