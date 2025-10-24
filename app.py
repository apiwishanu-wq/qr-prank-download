from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import random
import smtplib
import os

app = FastAPI()

# Serve your frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# In-memory storage for verification codes (simple version)
verification_codes = {}

# Environment variables for email
EMAIL_FROM = os.environ.get("EMAIL_FROM")
EMAIL_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD")


def send_email(to_email: str, code: str):
    """Send verification code via Gmail SMTP."""
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
        subject = "Your QR Prank Verification Code"
        body = f"Hello! Your verification code is: {code}"
        message = f"Subject: {subject}\n\n{body}"
        smtp.sendmail(EMAIL_FROM, to_email, message)


@app.post("/send-code")
async def send_code(email: str = Form(...)):
    code = str(random.randint(100000, 999999))  # 6-digit code
    verification_codes[email] = code
    try:
        send_email(email, code)
        return JSONResponse({"status": "ok", "message": "Verification code sent!"})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})


@app.post("/verify-code")
async def verify_code(email: str = Form(...), code: str = Form(...)):
    correct_code = verification_codes.get(email)
    if correct_code and correct_code == code:
        return JSONResponse({"status": "ok", "message": "Code verified!"})
    return JSONResponse({"status": "error", "message": "Invalid code."})
