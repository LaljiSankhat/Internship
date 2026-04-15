import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
SPREADSHEET_NAME = "Monthly Attendance Records"
EMPLOYEE_NAME = "Lalji"
CREDENTIAL_FILE = "credentials.json"

# -----------------------------
# GOOGLE AUTH
# -----------------------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_FILE, scope)
client = gspread.authorize(creds)

# -----------------------------
# OPEN SPREADSHEET
# -----------------------------
spreadsheet = client.open(SPREADSHEET_NAME)

# -----------------------------
# GET CURRENT DATE
# -----------------------------
now = datetime.now()

short_month = now.strftime("%b %Y")   # Mar 2026
full_month = now.strftime("%B %Y")    # March 2026

# -----------------------------
# FIND CORRECT WORKSHEET
# -----------------------------
try:
    sheet = spreadsheet.worksheet(short_month)
except:
    try:
        sheet = spreadsheet.worksheet(full_month)
    except:
        print("❌ Month sheet not found.")
        print("Available sheets:")
        for ws in spreadsheet.worksheets():
            print("-", ws.title)
        exit()

# -----------------------------
# FIND YOUR NAME ROW
# -----------------------------
try:
    cell = sheet.find(EMPLOYEE_NAME)
    row = cell.row
except:
    print("❌ Name not found in sheet.")
    exit()

# -----------------------------
# GET TODAY COLUMN
# -----------------------------
day = now.day
col = day + 2   

# -----------------------------
# CHECK EXISTING VALUE
# -----------------------------
value = sheet.cell(row, col).value

if value is None or value == "" or value.lower() == "a":
    sheet.update_cell(row, col, "P")
    print(f"✅ Attendance marked for {EMPLOYEE_NAME} on {now.strftime('%d %b %Y')}")
else:
    print("ℹ️ Attendance already marked:", value)
