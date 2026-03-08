import os

ACUITY_API_KEY = os.getenv("ACUITY_API_KEY")
ACUITY_USER_NAME = os.getenv("ACUITY_USER_NAME")
ACUITY_BASE_URL = "https://acuityscheduling.com/api/v1"
INVOICE_CHANNEL_ID = int(os.getenv("INVOICE_CHANNEL_ID", 0))
DAILY_REPORT_CHANNEL_ID = int(os.getenv("DAILY_REPORT_CHANNEL_ID"))

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_API_URL = os.getenv("DISCORD_API_URL")
TEST_TOKEN = os.getenv("TEST_TOKEN")
