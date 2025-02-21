import os
from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message

app = Flask(__name__)

# Email Configuration (Use environment variables for security)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True  # Using TLS for port 587
app.config['MAIL_USE_SSL'] = False  # Ensure SSL is disabled for port 587
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # Set in environment variables
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # Set in environment variables
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

mail = Mail(app)

outpass_requests = []  # List to store outpass requests

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        student_name = request.form.get('studentName')
        roll_number = request.form.get('rollNumber')
        student_mobile = request.form.get('studentMobile')
        parent_mobile = request.form.get('parentMobile')
        reason = request.form.get('reason')

        request_index = len(outpass_requests)
        approve_link = url_for('approve_request', request_index=request_index, _external=True)
        reject_link = url_for('reject_request', request_index=request_index, _external=True)

        outpass_requests.append({
            'student_name': student_name,
            'roll_number': roll_number,
            'student_mobile': student_mobile,
            'parent_mobile': parent_mobile,
            'reason': reason,
            'status': 'Pending',
            'approve_link': approve_link,
            'reject_link': reject_link
        })  # <-- Fix: Closing curly brace added

        send_approval_email(student_name, roll_number, student_mobile, parent_mobile, reason, request_index)
        
        return redirect(url_for('status'))
    
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return render_template('index.html', error_message=error_message)

@app.route('/status')
def status():
    return render_template('status.html', outpass_requests=outpass_requests)

@app.route('/approve/<int:request_index>')
def approve_request(request_index):
    try:
        if 0 <= request_index < len(outpass_requests):
            outpass_requests[request_index]['status'] = 'Approved'
            return redirect(url_for('status'))
        else:
            return 'Invalid request index.'
        
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
@app.route('/reject/<int:request_index>')
def reject_request(request_index):
    try:
        if 0 <= request_index < len(outpass_requests):
            outpass_requests[request_index]['status'] = 'Rejected'
            return redirect(url_for('status'))
        else:
            return 'Invalid request index.'
    
    except Exception as e:
        return f"An error occurred: {str(e)}"

def send_approval_email(student_name, roll_number, student_mobile, parent_mobile, reason, request_index):
    try:
        subject = f'Outpass Request - {student_name}'
        approve_link = url_for('approve_request', request_index=request_index, _external=True)
        reject_link = url_for('reject_request', request_index=request_index, _external=True)

        body = (
            f"Student Name: {student_name}\n"
            f"Roll Number: {roll_number}\n"
            f"Student Mobile: {student_mobile}\n"
            f"Parent's Mobile: {parent_mobile}\n"
            f"Reason: {reason}\n\n"
            f"Click the following links to approve or reject the request:\n\n"
            f"Approve: {approve_link}\n"
            f"Reject: {reject_link}"
        )

        msg = Message(subject=subject, recipients=[os.environ.get('MAIL_USERNAME')])  # Fix: Ensure recipients is a list
        msg.body = body
        mail.send(msg)

    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
