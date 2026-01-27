from app.services.command_service import CommandService
from app.services.command_renderer import CommandRenderer

print("\n===== RUN DAILY (PREVIEW MODE) =====\n")

command_service = CommandService()
renderer = CommandRenderer()

# Run the command
result = command_service.run_all_staff(preview=True)

# Render into response
response = renderer.render(result)

print("\n===== COMMAND RESPONSE =====\n")

for msg in response.messages:
    print(f"TO: {msg['to']}")
    print("TYPE:", msg["type"])
    print("BODY:")
    print(msg["body"])
    print("-" * 60)

if response.errors:
    print("\nErrors:")
    for err in response.errors:
        print(" -", err)