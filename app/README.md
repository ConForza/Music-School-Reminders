# Music School Certificate Automation

This project automates the application of prepaid lesson certificates to unpaid lessons using the Acuity Scheduling API, and produces structured daily reports for teaching staff.

It is designed as the backend core of a future Discord / web application used by a music school to manage:

- Block lesson payments (certificates)
- Unpaid lessons
- Automatic certificate application
- Daily staff summaries

---

## 🧩 Architecture

The system is organised into clear layers:

### Models
- `Student`
- `Lesson`
- `Certificate`
- `Payment`
- `Staff`

### Services
- `AcuityService` – API boundary for appointments & certificates  
- `CertificateService` – core orchestration logic  
- `ReportService` – generates structured daily summaries  

### Reports
- `StaffDailyReport`
- `StudentDailyReport`

### Database schema (SQLite)

users
- authentication and authorisation
- linked to staff and audit logs

staff
- teaching and admin staff
- linked to users (1–1)

audit_logs
- records all command executions
- linked to users when available
- status is 'ok' or 'error'
- errors is JSON of error messages
- args and routing are JSON blobs

---

## ⚙️ Core Flow

1.  Fetch students and unpaid lessons from Acuity  
2.  Fetch certificates per student  
3.  Sort unpaid lessons (oldest first)  
4.  Select certificates by:
    - Earliest expiration  
    - Valid lesson type  
    - Sufficient remaining minutes  
5.  Apply certificates via API  
6.  Record success, failure, and unmatched lessons  
7.  Produce per-staff daily summaries
8.  Create certificates, generate invoices, delete lessons via API 
9.  All API calls live in AcuityService 
10. Persistence layer using SQLite for audit logging

---

## 📊 Example Output
================ DAILY STAFF SUMMARY ================

Staff: Teacher Name

Student: API Failure (api@example.com)
  ✔ Lesson 302 → CERT-020 (remaining 120 mins)
  ⚠ Lesson 301 → API FAILED using CERT-020

---

## 🧪 Testing

Currently uses stubbed API responses in `main.py` to simulate:

- Successful application  
- No valid certificates  
- API failures  

Pytest integration is planned for a later stage.

---

## 🚀 Future Work

Planned extensions:

- Integration with Discord bot commands (WMFBot)
- Real Acuity API connection
- Web interface (React + Python backend)
- Staff authentication
- Automated daily scheduled runs

---

## 👤 Author

Built as part of a portfolio project focusing on:
- Clean architecture  
- Service-oriented design  
- Real-world API workflows  
- Robust failure handling  