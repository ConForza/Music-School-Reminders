# Music School Certificate Automation

This project is a Discord-based automation tool for managing a music school’s lesson administration.

It integrates with the Acuity Scheduling API to:

- Apply lesson certificates automatically
- Generate staff invoices
- Create lesson blocks
- Delete lessons in bulk
- Audit command usage
- Run daily staff reports

All commands support preview mode to prevent accidental state changes.

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
- `AcuityService` – boundary layer for external API calls (appointments, certificates)
- `CommandService` – entry point for commands; handles validation, access control, and audit logging
- `CommandExecutor` – orchestrates domain services once a command is validated
- `CertificateService` – certificate selection and application logic
- `InvoiceService` – invoice calculation and aggregation logic
- `AppointmentService` – deletion and appointment management logic
- `ReportService` – presentation formatting (Discord output only)

### Reports
- `StaffDailyReport`
- `StudentDailyReport`

---

### Database schema (SQLite)

users
- authentication and authorisation
- linked to staff and audit logs

staff
- teaching and admin staff
- linked to users (1–1)

instruments
- instruments
- lesson and appointment codes

prices
- pricing based on lesson type and duration
- staff lesson cuts (amounts)

audit_logs
- records all command executions
- linked to users when available
- status is 'ok' or 'error'
- errors is JSON of error messages
- args and routing are JSON blobs

---

## ⚙️ Core Command Lifecycle

1. Discord slash command received
2. CommandService validates arguments and permissions
3. CommandExecutor orchestrates the relevant domain service
4. Domain service performs business logic
5. AcuityService handles all external API communication
6. Results returned as CommandResult
7. ReportService formats Discord output
8. AuditLogger records execution in SQLite

---

## 🏗️ High-Level Architecture

Discord
   ↓
CommandService (validation & access control)
   ↓
CommandExecutor (orchestration)
   ↓
Domain Services (Invoice, Certificate, Appointment)
   ↓
AcuityService (external API)
   ↓
SQLite (audit logging)

---

## 📊 Example Output
================ DAILY STAFF SUMMARY ================

Staff: Teacher Name

Student: API Failure (api@example.com)
  ✔ Lesson 302 → CERT-020 (remaining 120 mins)
  ⚠ Lesson 301 → API FAILED using CERT-020

---

## 🧪 Testing

- Business logic is designed to be testable via service-layer isolation.
- External API calls are contained within `AcuityService`, allowing domain services to be tested independently using mocked responses.
- Expanded Pytest coverage is planned as the next development phase.

---

## 🔒 Access Control

Commands are protected via role-based rules:

- `admin_only`
- `staff_or_admin`
- `staff_self_or_admin`

The system validates that:
- Staff members cannot operate on other staff records
- Non-admin users cannot access administrative commands

---

## 👤 Author

Built as part of a portfolio project focusing on:
- Clean architecture  
- Service-oriented design  
- Real-world API workflows  
- Robust failure handling

---

## 🧑‍💻 Technical Highlights

- Service-layer architecture
- Command pattern implementation
- Role-based access control
- SQLite persistence layer
- External API integration with error handling
- Preview-safe destructive operations
- Monospace invoice rendering optimized for Discord mobile
- Structured audit logging