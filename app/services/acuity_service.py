from logging import exception

from app.models.student import Student
from app.models.lesson import Lesson
from app.models.payment import Payment
from app.models.certificate import Certificate
from app.config import ACUITY_USER_NAME
from app.config import ACUITY_API_KEY
from app.config import ACUITY_BASE_URL

import requests

_students_by_email = {}
headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }


def fetch_appointments_for_calendar(calendar_id, date_from, date_to):
    try:
        parameters = {
                "minDate": date_from,
                "maxDate": date_to,
                "calendarID": calendar_id,
                "direction": "ASC",
            }

        response = requests.get(
                url=f"{ACUITY_BASE_URL}/appointments",
                auth=(ACUITY_USER_NAME, ACUITY_API_KEY),
                params=parameters,
                headers=headers,
            )

        response.raise_for_status()

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

def fetch_students_for_staff(staff, date_from, date_to):
    _students_by_email.clear()
    success, data_or_error = fetch_appointments_for_calendar(staff.calendar_id, date_from, date_to)

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

def create_certificates_for_student(cert_code, student_email, quantity, preview: bool = False):
    if preview:
        print(f"[PREVIEW] Would create {quantity} certificate/s for {student_email} (product_ID: {cert_code})")
        return True, None

    parameters = {
        "productID": cert_code,
        "email": student_email.lower()
    }

    try:
        for _ in range(int(quantity)):
            response = requests.post(
                url=f"{ACUITY_BASE_URL}/certificates",
                auth=(ACUITY_USER_NAME, ACUITY_API_KEY),
                json=parameters,
                headers=headers
            )

            response.raise_for_status()
    except Exception as e:
        print(f"[ACUITY ERROR] create_certificate_for_student({student_email}): {e}")
        return False, str(e)

    return True, None

def apply_certificate_to_lesson(order_id, lesson_id, preview):
    if preview:
        print(f"[PREVIEW] Would apply certificate {order_id} to lesson {lesson_id}")
        return True, None

    try:
        parameters = {
            "certificate": order_id,
        }

        response = requests.put(url=f"{ACUITY_BASE_URL}/appointments/{lesson_id}?admin=true", auth=(ACUITY_USER_NAME, ACUITY_API_KEY),
                             json=parameters, headers=headers)

        response.raise_for_status()

        return True, None
    except requests.exceptions.RequestException as e:
        print(f"[ACUITY ERROR] apply_certificate_to_lesson({order_id}, {lesson_id}): {e}")
        return False, str(e)

def delete_appointment(appointment_id, preview):
    if preview:
        print(f"[PREVIEW] Would delete lesson {appointment_id}")
        return True, None

    try:
        parameters = {
            "noEmail": "true",
            "admin": "true"
        }

        response = requests.put(
            url=f"{ACUITY_BASE_URL}/appointments/{appointment_id}/cancel",
            auth=(ACUITY_USER_NAME, ACUITY_API_KEY),
            params=parameters,
            headers=headers
        )

        response.raise_for_status()
        return True, None

    except requests.exceptions.RequestException as e:
        print(f"[ACUITY ERROR] delete appointment({appointment_id}): {e}")
        return False, str(e)



def is_valid_email(email: str) -> bool:
    email = (email or "").strip().lower()
    if not email:
        return False

    parameters = {
        "search": email
    }

    try:
        response = requests.get(
            url=ACUITY_BASE_URL + "/clients",
            auth=(ACUITY_USER_NAME, ACUITY_API_KEY),
            params=parameters,
            headers=headers
        )
        response.raise_for_status()

        for result in response.json() or []:
            client_email = (result.get("email") or "").strip().lower()
            if client_email == email:
                return True

        return False

    except requests.exceptions.RequestException as e:
        print(f"[ACUITY ERROR] is_valid_email({email}): {e}")
        return False
