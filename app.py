from flask import Flask, render_template, redirect, url_for, request, session, jsonify, flash, current_app, send_from_directory, send_file
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask_mail import Mail, Message
import os
import datetime
from dotenv import load_dotenv
import io

app = Flask(__name__)

# --- Configuration ---
# Secret Key: Essential for session management. Use environment variable in production.
app.secret_key = os.environ.get("SECRET_KEY", "#Fines@67_Fallback")  # Replace with a strong secret key

# MongoDB Configuration: Use environment variable in production.

load_dotenv()  # Load environment variables from .env file
# Flask-Mail Configuration: Use environment variables in production!
app.secret_key = os.environ.get("SECRET_KEY", "#Fines@67_Fallback")  # Replace with a strong secret key
app.config["MONGO_URI"] = "mongodb://localhost:27017/finesdb" # Important: Include DB name in URI!

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = ('Campus Fine Track', os.environ.get('MAIL_DEFAULT_SENDER'))
# Add a setting to disable email sending for testing/dev if needed
app.config['MAIL_SUPPRESS_SEND'] = os.environ.get('MAIL_SUPPRESS_SEND', 'false').lower() == 'true'

# --- Initialize Extensions ---
mongo = PyMongo(app)  # Initialize Flask-PyMongo
app.config['MAIL_INSTANCE'] = Mail(app)  # Store mail instance in app config


# --- Blueprints ---
# Import *after* app and config are defined
# Blueprints can now use 'mongo' and 'mail' via the 'current_app' proxy
from admin import admin_bp
from student import student_bp

app.register_blueprint(admin_bp)
app.register_blueprint(student_bp)


# --- Routes ---
@app.route("/")
def index():
    # print(mongo)  # Debugging: Check if mongo.db is initialized correctly
    # # Access the database via Flask-PyMongo
    # if not mongo.db:  # Check if mongo.db is None (connection failed)
    #     flash('Error: Database connection failed. Please contact the administrator.', '0')
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


# Centralized route for fine amount lookup
@app.route('/get_fine_amount/<category>')
def get_fine_amount(category):
    try:
        fine_category_doc = mongo.db.fine_categories.find_one({'type': category})
        if fine_category_doc:
            return jsonify({'amount': fine_category_doc.get('amount')})  # Use .get for safety
        else:
            return jsonify({'amount': None})
    except Exception as e:
        print(f"Error in get_fine_amount for category '{category}': {e}")
        return jsonify({'amount': None, 'error': 'Server error fetching fine amount'}), 500


@app.route('/screenshot/<screenshot_id>')
def get_screenshot(screenshot_id):
    try:
        screenshot = mongo.db.screenshots.find_one({'_id': ObjectId(screenshot_id)})
        if screenshot:
            return send_file(
                io.BytesIO(screenshot['data']),
                mimetype=screenshot['content_type'],
                as_attachment=False
            )
        return 'Screenshot not found', 404
    except Exception as e:
        print(f"Error serving screenshot {screenshot_id}: {e}")
        return 'Error serving screenshot', 500


# --- Utility / Error Handling ---
@app.errorhandler(404)
def page_not_found(e):
    print(f"Page Not Found: {e}")
    flash(e, '0')
    # return render_template('404.html'), 404  # Consider creating a 404.html template
    return redirect(url_for('index'))


@app.errorhandler(500)
def internal_server_error(e):
    print(f"Server Error: {e}")  # Log the error
    flash('An internal server error occurred. Please try again later.', '0')
    # You might want a specific 500.html template
    return render_template('index.html'), 500  # Redirect to index or a dedicated error page


# --- Main Execution ---
if __name__ == '__main__':
    users = list(mongo.db.admin.find())
    if not users:
        print("\n",end="\t\t\t")
        user = {
            "username": "admin",
            "password": generate_password_hash("admin"),
            "role": "admin"
        }
        try:
            mongo.db.admin.insert_one(user)  # Changed to "admin"
            print("default admin added successfully!\n\t\t\t\tUsername: admin\n\t\t\t\tPassword: admin")
        except Exception as e:
            print(f"Error adding admin: {e}")
        print()
    else:
        pass
    # app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
    app.run(debug=True)
    # app.run(debug=True,port=8000)