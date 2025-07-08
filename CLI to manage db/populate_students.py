import csv
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import sys
from datetime import datetime

# Branch code mapping
BRANCH_CODES = {
    '01': 'CE',  # Civil Engineering
    '02': 'EEE', # Electrical and Electronics Engineering
    '03': 'ME',  # Mechanical Engineering
    '04': 'ECE', # Electronics and Communication Engineering
    '05': 'CSE', # Computer Science and Engineering
    '10': 'EIE', # Electronics and Instrumentation Engineering
    '32': 'CS & BS', # Computer Science and Business Systems
    '62': 'CSE(CS)', # Computer Science and Engineering (Cyber Security)
    '66': 'CSE(AIML)', # Computer Science and Engineering (AI & ML)
    '67': 'CSE(DS)', # Computer Science and Engineering (Data Science)
    '72': 'AID', # Artificial Intelligence and Data Science
    '73': 'AIML'  # Artificial Intelligence and Machine Learning
}

def get_branch_name(student_id):
    """Extract branch code from student ID and return branch name."""
    try:
        branch_code = student_id[6:8]  # Extract branch code (7th and 8th characters)
        return BRANCH_CODES.get(branch_code, 'Unknown')
    except:
        return 'Unknown'

def get_year_from_id(student_id):
    """Extract year from student ID."""
    try:
        return '20' + student_id[:2]  # Convert YY to YYYY format
    except:
        return 'Unknown'

def validate_student_id(student_id):
    """Validate the format of student ID.
    Format: YYB81ABRXX where:
    YY is admission year (2 digits, e.g., 22)
    B81A is the constant part
    BR is branch code (2 digits)
    XX is roll number (2 characters, can be digits or letters)
    """
    if not isinstance(student_id, str):
        return False

    # Check length
    if len(student_id) != 10:
        print(f"Invalid ID length: {student_id} (should be 10 digits)")
        return False

    try:
        # Extract components
        year = int(student_id[:2])      # First 2 digits (YY)
        constant_part = student_id[2:6]  # Next 4 digits (B81A)
        branch_code = student_id[6:8]    # Next 2 digits (BR)
        roll_number = student_id[8:]     # Last 2 characters (XX)

        # Validate year
        current_year = datetime.now().year % 100  # Get last 2 digits of current year
        if not (0 <= year <= current_year):
            print(f"Invalid year in ID: {year} (should be between 00 and {current_year})")
            return False

        # Validate constant part
        if constant_part != 'B81A':
            print(f"Invalid constant part in ID: {constant_part} (should be B81A)")
            return False

        # Validate branch code
        if branch_code not in BRANCH_CODES:
            print(f"Invalid branch code in ID: {branch_code} (valid codes: {', '.join(BRANCH_CODES.keys())})")
            return False

        # Validate roll number (now accepts both digits and letters)
        if len(roll_number) != 2:
            print(f"Invalid roll number length in ID: {roll_number} (should be 2 characters)")
            return False

        return True

    except ValueError as e:
        print(f"Invalid ID format: {student_id} - {str(e)}")
        return False

def main():
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB connection string
    # mongo_uri = os.environ.get('MONGO_URI')
    mongo_uri = "mongodb://localhost:27017/"
    if not mongo_uri:
        print("Error: MONGO_URI not found in environment variables")
        sys.exit(1)

    # Connect to MongoDB
    try:
        client = MongoClient(mongo_uri)
        db = client.finesdb
        print("Connected to MongoDB successfully")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        sys.exit(1)

    # Check if CSV file exists
    if not os.path.exists('students.csv'):
        print("Error: students.csv not found in current directory")
        sys.exit(1)

    try:
        # Initialize counters
        total_records = 0
        inserted_count = 0
        updated_count = 0
        error_count = 0
        
        # Read CSV file
        with open('students.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            # Validate headers
            headers = [header.strip().lower() for header in csv_reader.fieldnames]
            required_columns = ['id', 'name', 'section']
            
            missing_columns = [col for col in required_columns if col not in headers]
            if missing_columns:
                print(f"Error: Missing required columns in CSV: {missing_columns}")
                sys.exit(1)

            print("\nProcessing records...")
            
            # Process each record
            for row in csv_reader:
                total_records += 1
                try:
                    # Clean data
                    student_id = row['id'].strip()
                    email = f"{student_id}@cvr.ac.in"
                    
                    student_data = {
                        'id': student_id,
                        'name': row['name'].strip(),
                        'branch': get_branch_name(student_id),
                        'section': row['section'].strip(),
                        'email': row.get('email', email).strip(),
                        'last_updated': datetime.now()
                    }

                    # Validate student ID
                    if not validate_student_id(student_data['id']):
                        print(f"Error: Invalid student ID format for {student_data['id']}")
                        error_count += 1
                        continue

                    # Try to update existing record, insert if not exists
                    result = db.students.update_one(
                        {'id': student_data['id']},
                        {'$set': student_data},
                        upsert=True
                    )

                    if result.matched_count > 0:
                        updated_count += 1
                        print(f"Updated student: {student_id}")
                    elif result.upserted_id:
                        inserted_count += 1
                        print(f"Inserted new student: {student_id}")

                except Exception as e:
                    print(f"Error processing record: {e}")
                    error_count += 1

        # Print summary
        print("\nImport Summary:")
        print(f"Total records processed: {total_records}")
        print(f"New records inserted: {inserted_count}")
        print(f"Existing records updated: {updated_count}")
        print(f"Errors encountered: {error_count}")

    except Exception as e:
        print(f"Error processing CSV file: {e}")
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    main()
