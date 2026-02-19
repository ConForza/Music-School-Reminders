from app.persistence.sqlite.instrument_repository import InstrumentRepository

instrument_repository = InstrumentRepository()
print(instrument_repository.get_appointment_ids_for_instrument("piano"))
print(instrument_repository.get_ids_for_instrument("violin"))