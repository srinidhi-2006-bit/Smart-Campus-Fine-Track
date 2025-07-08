# input_file_1.py (student.py) - Modified
from flask import Blueprint, render_template, redirect, url_for, request, session, jsonify, flash, current_app
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
import datetime
import json
import os
from dotenv import load_dotenv
import re

student_bp = Blueprint('student', __name__, url_prefix='/student')
load_dotenv()
client = MongoClient(os.environ.get('MONGO_URI'))
db = client.finesdb

@student_bp.route('/search', methods=['POST'])
def student_search():
    student_id = request.form.get('student_id', '').strip()
    if not student_id:
        flash('Please enter a student ID', '0')
        return redirect(url_for('index'))
    
    try:
        # Checking for existance of student
        student = db.students.find_one({'id': student_id})
        if not student:
            flash('Invalid student ID. Please try again.', '0')
            return redirect(url_for('index'))
        else:
            return redirect(url_for('student.get_student_fines', student_id_str=student_id))
        
    except (OperationFailure, ServerSelectionTimeoutError) as e:
        print(f"Database error during student search: {e}")
        flash('Database connection error. Please try again later.', '0')
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Unexpected error during student search: {e}")
        flash('An unexpected error occurred. Please try again.', '0')
        return redirect(url_for('index'))

@student_bp.route('/<string:student_id_str>/fines', methods=['GET'])
def get_student_fines(student_id_str):
    if not student_id_str or not student_id_str.strip():
        flash('Invalid student ID.', '0')
        return redirect(url_for('index'))

    if db is None:
        flash('Database connection error.', '0')
        return redirect(url_for('index'))

    student_name = "Unknown"
    fines = []
    try:
        # Find student by the string ID (roll number)
        student = db.students.find_one({'id': student_id_str})

        if student:
            student_name = student.get('name', 'N/A')
            query = {'student_id_str': student_id_str}
            fines = list(db.fines.find(query).sort('due_date', 1))

            # Convert ObjectId to string for template compatibility
            for fine in fines:
                fine['_id'] = str(fine['_id'])
        else:
            flash(f'Student ID {student_id_str} not found.', '0')
            return redirect(url_for('index'))

    except (OperationFailure, ServerSelectionTimeoutError) as e:
        print(f"Database error fetching fines for student {student_id_str}: {e}")
        flash('Database connection error. Please try again later.', '0')
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Unexpected error fetching fines for student {student_id_str}: {e}")
        flash('An unexpected error occurred. Please try again.', '0')
        return redirect(url_for('index'))
    print(student_id_str)
    return render_template('student_fines.html',
                         fines=fines,
                         student_name=student_name,
                         student_id_str=student_id_str)


# Removed the '/<string:student_id>/pay' GET route for show_payment_form
# Payment form is now integrated into student_fines.html pop-up


@student_bp.route('/<string:student_id_str>/pay', methods=['POST'])
def process_payment(student_id_str):
    # Early validation of student_id_str
    if not student_id_str or not student_id_str.strip():
        return jsonify({'error': 'Invalid student ID'}), 400

    if db is None:
        return jsonify({'error': 'Database connection error'}), 500

    transaction_id = request.form.get('transaction_id', '').strip()
    selected_fine_ids_json = request.form.get('selected_fine_ids')
    screenshot = request.files.get('screenshots')

    # --- Validation ---
    if not transaction_id:
        return jsonify({'error': 'Transaction ID is required'}), 400

    if not selected_fine_ids_json:
        return jsonify({'error': 'No fines selected for payment'}), 400

    if not screenshot:
        return jsonify({'error': 'Payment screenshot is required'}), 400

    try:
        selected_fine_ids_str = json.loads(selected_fine_ids_json)
        if not isinstance(selected_fine_ids_str, list) or not selected_fine_ids_str:
            return jsonify({'error': 'Selected fines data is not a valid list'}), 400
        # Convert string IDs to ObjectIds
        object_ids_to_pay = [ObjectId(fine_id) for fine_id in selected_fine_ids_str]

    except (json.JSONDecodeError, ValueError, InvalidId) as e:
        print(f"Error processing payment data for {student_id_str}: {e}")
        return jsonify({'error': 'Invalid data submitted for selected fines'}), 400

    # --- Process Payment Submission ---
    try:
        # Finding the student's MongoDB _id
        student = db.students.find_one({'id': student_id_str}, {'_id': 1})
        if not student:
            return jsonify({'error': f'Student {student_id_str} not found'}), 404
        student_db_id = student['_id']

        # Verifing that selected fines belong to the student and are 'pending'
        fines_to_pay = list(db.fines.find({
            '_id': {'$in': object_ids_to_pay},
            'student_id': student_db_id,
            'status': 'pending'
        }))

        if len(fines_to_pay) != len(object_ids_to_pay):
            return jsonify({'error': 'Some selected fines could not be processed'}), 400

        if not fines_to_pay:
            return jsonify({'error': 'No valid pending fines found for payment'}), 400

        # Storing the screenshot in MongoDB
        screenshot_data = screenshot.read()
        screenshot_id = db.screenshots.insert_one({
            'data': screenshot_data,
            'content_type': screenshot.content_type,
            'filename': screenshot.filename,
            'upload_date': datetime.datetime.now()
        }).inserted_id

        # Updating the fine status and store transaction ID and screenshot reference
        update_result = db.fines.update_many(
            {'_id': {'$in': object_ids_to_pay},
             'student_id': student_db_id,
             'status': 'pending'},
            {'$set': {
                'status': 'pending_approval',
                'transaction_id': transaction_id,
                'screenshot_id': screenshot_id,
                'last_updated': datetime.datetime.now()
            }}
        )

        if update_result.modified_count > 0:
            # Creating a record in the 'transactions' collection
            total_amount = sum(fine.get('amount', 0) for fine in fines_to_pay)
            db.transactions.insert_one({
                'transaction_id': transaction_id,
                'student_db_id': student_db_id,
                'student_id_str': student_id_str,
                'fine_ids': object_ids_to_pay,
                'amount': total_amount,
                'screenshot_id': screenshot_id,
                'status': 'pending_approval',
                'created_at': datetime.datetime.now()
            })
            
            return jsonify({
                'success': True,
                'message': f'Payment submitted for {update_result.modified_count} fines. Awaiting admin approval.',
                'redirect': url_for('student.get_student_fines', student_id_str=student_id_str)
            }), 200
        else:
            return jsonify({'error': 'No fines were updated'}), 400

    except Exception as e:
        print(f"Error processing payment: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500