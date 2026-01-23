# Music School Automation Engine

Backend automation system for managing lesson payments, certificates, and staff workflows
for a music school using the Acuity Scheduling API and Discord bot integration.

---

## Certificate Application Engine

Implements business logic for automatically applying prepaid lesson certificates
to unpaid lessons, prioritising:

- Oldest unpaid lessons first
- Earliest-expiring certificates first
- Lesson duration matching (30 / 60 mins)

Includes:
- Domain models (Student, Lesson, Certificate, Payment)
- Service layer (CertificateService, AcuityService stub)
- Structured reconciliation results for future Discord integration

---

## Architecture

- `models/` — Core domain entities (Student, Lesson, Certificate, Payment)
- `services/` — Business logic and external API orchestration
- `main.py` — Test harness for local validation

Designed with:
- Clear separation of concerns  
- Testable service layer  
- Future integration with Discord slash commands and web UI  

---

## Status

In active development as part of a staged refactor of an existing production Discord bot