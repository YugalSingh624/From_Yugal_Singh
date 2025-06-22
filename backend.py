from flask import Flask, request, jsonify
import requests
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)

# ENV variables from Render dashboard
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

def generate_answer(question):
    data = {
        "contents": [
            {
                "parts": [{"text": question}]
            }
        ]
    }
    try:
        response = requests.post(GEMINI_URL, json=data)
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Error from Gemini: {str(e)}"

def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
    except Exception as e:
        print(f"Email sending failed: {e}")
        raise

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    email = data.get("email")
    question = data.get("question")

    if not email or not question:
        return jsonify({"error": "Missing email or question"}), 400

    try:
        answer = generate_answer(question)
        send_email(email, "Reply for your question", answer)
        return jsonify({"status": "success", "message": "Email sent"}), 200
    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500

# Make sure to use Render-assigned PORT
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)