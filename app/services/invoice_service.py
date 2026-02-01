from app.services.command_service import CommandResult

class InvoiceService:

    def generate_invoice(self, staff_id: str, date_from, date_to, source, preview: bool = False):
        routing = {
            "target": "admin"
        }

        return CommandResult(
            type_="GENERATE_INVOICE",
            content={
                "date_from": date_from,
                "date_to": date_to,
                "staff_id": staff_id
            },
            errors=None,
            routing=routing,
            source=source
        )

    def check_unpaid(self, staff_id: str, date_from = None, date_to = None):
        pass