const API = "https://qr-prank-web.onrender.com"; // Update with your Render URL

const sendBtn = document.getElementById("send");
const checkBtn = document.getElementById("check");
const emailInput = document.getElementById("email");
const codeInput = document.getElementById("code");
const verifyDiv = document.getElementById("verify");
const statusDiv = document.getElementById("status");

sendBtn.onclick = async () => {
  const email = emailInput.value.trim();
  if (!email) {
    statusDiv.textContent = "Please enter an email!";
    return;
  }

  try {
    const res = await fetch(`${API}/send-code`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ email })
    });

    if (res.ok) {
      statusDiv.textContent = "Verification code sent! Check your email.";
      verifyDiv.style.display = "block";
    } else {
      const err = await res.json();
      statusDiv.textContent = `Error: ${err.detail}`;
    }
  } catch (e) {
    statusDiv.textContent = `Network error: ${e.message}`;
  }
};

checkBtn.onclick = async () => {
  const email = emailInput.value.trim();
  const code = codeInput.value.trim();
  if (!code) {
    statusDiv.textContent = "Please enter the code!";
    return;
  }

  try {
    const res = await fetch(`${API}/verify-code`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ email, code })
    });

    if (res.ok) {
      statusDiv.textContent = "Email verified! Starting download...";
      // Redirect to actual download or prank file
      window.location.href = "/static/assets/prank.zip"; // example
    } else {
      const err = await res.json();
      statusDiv.textContent = `Verification failed: ${err.detail}`;
    }
  } catch (e) {
    statusDiv.textContent = `Network error: ${e.message}`;
  }
};
