from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import smtplib, os, random, time
from email.mime.text import MIMEText
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Serve your frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def root():
    return FileResponse("frontend/index.html")

# Allow your frontend to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with your frontend URL for security
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for verification codes
codes = {}  # {email: (code, expiry)}

FROM = os.environ.get("EMAIL_FROM")
PASSWORD = os.environ.get("EMAIL_APP_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

class EmailBody(BaseModel):
    email: str

class VerifyBody(BaseModel):
    email: str
    code: str

@app.post("/send-code")
def send_code(data: EmailBody):
    if not FROM or not PASSWORD:
        raise HTTPException(status_code=500, detail="Server email credentials not configured")

    code = f"{random.randint(0,999999):06d}"
    expiry = time.time() + 300  # 5 min expiry
    codes[data.email] = (code, expiry)

    msg = MIMEText(f"Your verification code is {code}\nExpires in 5 minutes.")
    msg["Subject"] = "QR Prank Verification Code"
    msg["From"] = FROM
    msg["To"] = data.email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
            s.starttls()
            s.login(FROM, PASSWORD)
            s.sendmail(FROM, [data.email], msg.as_string())
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(status_code=500, detail="SMTP authentication failed")

    return {"ok": True}

@app.post("/verify-code")
def verify_code(data: VerifyBody):
    entry = codes.get(data.email)
    if not entry:
        raise HTTPException(status_code=400, detail="No code sent")
    code, expiry = entry
    if time.time() > expiry:
        raise HTTPException(status_code=400, detail="Code expired")
    if data.code != code:
        raise HTTPException(status_code=400, detail="Incorrect code")
    return {"ok": True}
