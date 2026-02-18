from app.models.student import Student
from app.models.lesson import Lesson
from app.models.payment import Payment
from app.models.certificate import Certificate
from app.config import ACUITY_USER_NAME
from app.config import ACUITY_API_KEY
from app.config import ACUITY_BASE_URL

import requests
import datetime as dt

_students_by_email = {}
headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }


def fetch_appointments_for_calendar(calendar_id):
    today_date = (dt.datetime.now() + dt.timedelta(days=1)).strftime("%B %d, %Y")

    try:
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

        return True, response.json()
    except Exception as e:
        return False, str(e)


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
        is_paid_raw=result["paid"]
    )

    lesson = Lesson(
        id_=result["id"],
        date_raw=result["datetime"],
        type_=result["type"],
        category=result["category"],
        duration=result["duration"],
        payment=payment,
        appointment_type_id=result.get("appointmentTypeID"),
        certificate_code=result.get("certificate")
    )

    student.add_lesson(lesson)

    return lesson

def fetch_students_for_staff(staff):
    _students_by_email.clear()
    success, data_or_error = fetch_appointments_for_calendar(staff.calendar_id)

    if not success:
        raise RuntimeError(f"{staff.name}: {data_or_error}")

    appointments = data_or_error
    for result in appointments:
        lesson_from_api(result)

    return list(_students_by_email.values())

def certificate_from_api(result):
    certificate = Certificate(
        order_id=result["certificate"],
        certificate_name=result["name"],
        expiration_date_raw=result["expiration"],
        remaining_minutes=int(result["remainingMinutes"]),
        appointment_type_ids=[int(x) for x in (result.get("appointmentTypeIDs") or [])]
    )

    return certificate

def fetch_certificates_for_student(student):
    student.certificates.clear()

    parameters = {
        "email": student.email,
    }
    try:
        response = requests.get(
            url=f"{ACUITY_BASE_URL}/certificates",
            auth=(ACUITY_USER_NAME, ACUITY_API_KEY),
            params=parameters,
            headers=headers
        )

        response.raise_for_status()

        for result in response.json():
            student.add_certificate(certificate_from_api(result))
    except Exception as e:
        print(f"[ACUITY ERROR] fetch_certificates_for_student({student.email}): {e}")



def apply_certificate_to_lesson(order_id, lesson_id, preview=False):
    if preview:
        print(f"[PREVIEW] Would apply certificate {order_id} to lesson {lesson_id}")
        return True, 120

    try:
        print(f"[API STUB] Applying certificate {order_id} to lesson {lesson_id}")
        # parameters = {
        #     "certificate": order_id,
        # }
        #
        # response = requests.put(url=f"{ACUITY_BASE_URL}/appointments/{lesson_id}?admin=true", auth=(ACUITY_USER_NAME, ACUITY_API_KEY),
        #                      json=parameters, headers=headers)

        # if response.status_code != 200:
        #   return False f"API error: {response.status_code} {response.text}"
        #
        # remaining = response.json().get("remainingMinutes")

        remaining = 120
        return True, remaining
    except Exception as e:
        return False, str(e)

