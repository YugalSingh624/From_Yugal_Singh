from flask import Flask, request, jsonify
import requests
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
EMAIL_SENDER = 'yugalsingh426@gmail.com'
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Use Gmail App Password

def generate_answer(question):
    data = {
        "contents": [{
            "parts": [{"text": question}]
        }]
    }
    response = requests.post(GEMINI_URL, json=data)
    return response.json()['candidates'][0]['content']['parts'][0]['text']

def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    email = data.get('email')
    question = data.get('question')

    if not email or not question:
        return jsonify({'error': 'Invalid input'}), 400

    answer = generate_answer(question)
    send_email(email, "Reply for your question", answer)
    return jsonify({"status": "Email sent"}), 200

if __name__ == '__main__':
    app.run(debug=False)