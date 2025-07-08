# Campus Fine Tracking System
Smart College Fine Management System

A Flask-based web application for managing and tracking campus fines. This system provides separate interfaces for administrators and students to handle fine submissions, approvals, and management.

## Features

- **Admin Interface**
  - Manage fine submissions
  - Approve/reject fines
  - View and track fine history
  - Manage fine categories and amounts

- **Student Interface**
  - Submit new fines
  - Upload screenshots of UPI payment transaction
  - Track fine status
  - View fine history

- **Email Notifications**
  - Automated email notifications for fine status updates
  - Configurable email settings

## Prerequisites

- Python 3.x
- MongoDB
- SMTP server for email functionality

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Sai-Deekshith-06/Campus-Fine-Track.git
cd Campus-Fine-Track
```

2. use the provided shell script:
```bash
./run.sh
```
or (3-5)

3. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:
Create a `.flaskenv` file in the root directory with the following variables:
```
MAIL_SERVER=your_smtp_server
MAIL_PORT=587
MAIL_USE_SSL=True
MAIL_USE_TLS=False 
MAIL_USERNAME=your_email
MAIL_PASSWORD=your_app_password_of_gmail
MAIL_DEFAULT_SENDER=your_email
MONGO_URI=mongodb://localhost:27017/                           
_MONGO_URI=mongodb://localhost:27017/finesdb
```

## Running the Application

1. Ensure MongoDB is running on your system

2. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Default Admin Credentials

- Username: admin
- Password: admin

**Important**: Change these credentials after first login for security purposes.

## Project Structure

```
fines/
├── admin.py          # Admin blueprint and routes
├── app.py            # Main application file
├── student.py        # Student blueprint and routes
├── requirements.txt  # Project dependencies
├── run.sh            # Startup script
├── .flaskenv         # Flask environment configuration
├── static/           # Static files (images)
├── templates/        # HTML templates
├── CLI to manage db/manage_db              # Command Line Interface to manage users, fine categories and students
└── CLI to manage db/populate_students.py   # To add students details into the database from students.csv
```

## Technologies Used

- Flask - Web framework
- MongoDB - Database
- Flask-PyMongo - MongoDB integration
- Flask-Mail - Email functionality
- Python-dotenv - Environment variable management

## Security Notes

- The application uses secure password hashing
- Session management with secret key
- Environment variables for sensitive data
- MongoDB connection security

FUTURE SCOPE
-	Payment gateway integration
-	Mobile application support
-	AI-powered fine reason prediction models
-	Imposing/creating Multiple fines by uploading a spreadsheet
-	Chatbot Support