from app.models.student import Student
from app.models.lesson import Lesson
from app.models.payment import Payment

from app.config import ACUITY_USER_NAME
from app.config import ACUITY_API_KEY
from app.config import ACUITY_BASE_URL

import requests
import datetime as dt

_students_by_email = {}


def fetch_appointments_for_calendar(calendar_id):
    today_date = (dt.datetime.now() + + dt.timedelta(days=1)).strftime("%B %d, %Y")
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

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

def fetch_students_for_staff(staff):
    appointments = fetch_appointments_for_calendar(staff.calendar_id)

    for result in appointments:
        lesson_from_api(result)

    return list(_students_by_email.values())
