# Imports: api requests package, datetime, json for parsing data, os for env variables
import requests
from datetime import datetime, timedelta
import json
import os

# API and Discord tokens
API_URL = "https://acuityscheduling.com/api/v1/"
DISCORD_API = os.environ.get("DISCORD_API")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
USER_NAME = os.environ.get("USER_NAME")
API_KEY = os.environ.get("API_KEY")

# Headers for API verification
headers = {
    "accept": "application/json",
    "content-type": "application/json"
}

today_date = datetime.now().strftime("%B %d, %Y")


# API response as function
def response(request, parameters):
    response = requests.get(
        url=API_URL + request,
        auth=(USER_NAME, API_KEY),
        params=parameters,
        headers=headers
    )
    return response


# Function to get all lessons for the specified dates for the specified member of staff
def get_appointments(from_date, to_date, client, staff):
    appointments = []
    parameters = {
        "minDate": from_date,
        "maxDate": to_date,
        "calendarID": staff["calendar"]
    }

    if client:
        parameters["email"] = client

    data = response("appointments", parameters)

    results = data.json()
    # Store results in appointments array
    for result in results:
        appointments.append({
            "id": result["id"],
            "first name": result["firstName"],
            "surname": result["lastName"],
            "email": result["email"],
            "paid": result["paid"],
            "certificate applied": result["certificate"],
            "date": result["date"],
            "type": result["type"],
            "category": result["category"],
            "datetime": result["datetime"]
        })

    return appointments


# Function to check for valid payment certificates for the current client
def check_certificates(appointment):
    valid_certificates = []

    parameters = {
        "email": appointment["email"],
    }

    data = response("certificates", parameters)

    for certificate in data.json():
        if certificate["remainingMinutes"]:
            print(certificate)
            if appointment['category'].split()[0] in certificate["name"]:
                if datetime.strptime(certificate["expiration"], "%Y-%m-%d") >= datetime.now():
                    valid_certificates.append(certificate)
            elif "1 Hour" in certificate["name"]:
                if datetime.strptime(certificate["expiration"], "%Y-%m-%d") >= datetime.now():
                    valid_certificates.append(certificate)

    # Sort certificates in date order, oldest first, for later application
    sorted_certificates = sorted(valid_certificates, key=lambda d: datetime.strptime(d["expiration"], "%Y-%m-%d"))
    for certificate in sorted_certificates:
        if not certificate["email"]:
            order = response(f"orders/{certificate['orderID']}", None).json()
            certificate["email"] = order["email"]

    return sorted_certificates


# Function to check out unpaid lessons on the Acuity calendar using an array of valid certificates
def check_out_lessons(unpaid_lessons, certificates):
    cert_30 = []
    cert_60 = []
    unpaid_30 = []
    unpaid_60 = []

    for certificate in certificates:
        if "30" in certificate["name"]:
            cert_30.append(certificate)
        else:
            cert_60.append(certificate)

    for lesson in unpaid_lessons:
        if "30" in lesson["type"]:
            unpaid_30.append(lesson)
        else:
            unpaid_60.append(lesson)

    counter = 0
    for certificate in cert_30:
        remaining_minutes = int(certificate["remainingMinutes"])
        while remaining_minutes > 0 and counter < len(unpaid_30):
            lesson = unpaid_30[counter]
            lesson_id = lesson["id"]
            parameters = {
                "certificate": certificate["certificate"],
            }
            requests.put(url=f"{API_URL}appointments/{lesson_id}?admin=true", auth=(USER_NAME, API_KEY),
                         json=parameters, headers=headers)
            remaining_minutes -= 30
            counter += 1

    counter = 0
    for certificate in cert_60:
        remaining_minutes = int(certificate["remainingMinutes"])
        while remaining_minutes > 0 and counter < len(unpaid_60):
            lesson = unpaid_60[counter]
            lesson_id = lesson["id"]
            parameters = {
                "certificate": certificate["certificate"],
            }
            requests.put(url=f"{API_URL}appointments/{lesson_id}?admin=true", auth=(USER_NAME, API_KEY),
                         json=parameters, headers=headers)
            remaining_minutes -= 60
            counter += 1


# Function to calculate unpaid lessons for the given students
def calculate_unpaid_lessons(appointment, staff, exempt_students):
    unpaid_lessons = []
    date_from = datetime.now() - timedelta(days=90)
    for lesson in get_appointments(
            from_date=date_from, to_date=today_date, client=appointment["email"], staff=staff):
        if lesson["paid"] == 'no':
            if not lesson["email"] in exempt_students:
                unpaid_lessons.append(lesson)
    sorted_list = sorted(unpaid_lessons, key=lambda d: d["datetime"])
    appointment["unpaid lessons"] = [
        (datetime.strptime(lesson["datetime"].split("T")[0], "%Y-%m-%d")).strftime("%d %b %Y") for lesson in
        sorted_list]

    return sorted_list


# Function to update the list of students to pay
def update_students_to_pay(appointment):
    if students_to_pay:
        if appointment["first name"] not in str(students_to_pay) and appointment["surname"] not in str(students_to_pay):
            students_to_pay.append(appointment)
    elif appointment["unpaid lessons"]:
        students_to_pay.append(appointment)


# Function to create a discord message, iterating over every member of staff in staff_details.json, listing unpaid lessons
def discord_message(clients, staff):
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bot {DISCORD_TOKEN}"
    }

    message = """
**Students who need to pay today**:
"""
    for client in clients[::-1]:
        message += f"""
**{client['first name']} {client['surname']}**
**Email**: {client['email']}
**Unpaid lessons**: {len(client['unpaid lessons'])}
**Dates**: {", ".join(map(str, client['unpaid lessons']))}
"""

    message += "*"

    parameters = {
        "content": f"<@{staff['discord']}> {message}",
        "allowed_mentions": {"users": [f"{staff['discord']}"]}
    }
    # requests.post(url=DISCORD_API, json=parameters, headers=header)
    print(message)


with open("staff_details.json", mode="r") as file:
    staff_details = json.load(file)

with open("exempt_students.txt", mode="r") as file:
    exempt_students = [line[:-1] for line in file.readlines()]

for staff_member in staff_details:
    students_to_pay = []
    for appointment in get_appointments(
            from_date=today_date, to_date=today_date, client=None, staff=staff_member):
        certificates = check_certificates(appointment)
        lessons_to_check = calculate_unpaid_lessons(appointment, staff_member, exempt_students)
        check_out_lessons(lessons_to_check, certificates)
        calculate_unpaid_lessons(appointment, staff_member, exempt_students)
        if appointment["unpaid lessons"]:
            update_students_to_pay(appointment)

    if students_to_pay:
        discord_message(clients=students_to_pay, staff=staff_member)
