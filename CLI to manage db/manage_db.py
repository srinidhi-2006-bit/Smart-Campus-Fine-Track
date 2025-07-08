from pymongo import MongoClient
from werkzeug.security import generate_password_hash
import os

# MongoDB connection details
MONGO_URI = "mongodb://localhost:27017/"  # Replace if needed
DB_NAME = "finesdb"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def add_user():
    """Adds a new user (admin or super_admin)."""

    username = input("Enter username: ")
    password = input("Enter password: ")
    hashed_password = generate_password_hash(password)
    role = input("Enter role (admin/super_admin): ")

    user = {
        "username": username,
        "password": hashed_password,
        "role": role
    }

    try:
        db.admin.insert_one(user)  # Changed to "admin"
        print("User added successfully!")
    except Exception as e:
        print(f"Error adding user: {e}")

def view_users():
    """Displays all users."""

    users = list(db.admin.find())  # Changed to "admin"
    if users:
        for user in users:
            print(f"Username: {user['username']}, Role: {user['role']}")
    else:
        print("No users found.")

def remove_user():
    """Removes a user."""

    username = input("Enter username to remove: ")
    try:
        result = db.admin.delete_one({"username": username})  # Changed to "admin"
        if result.deleted_count:
            print("User removed successfully!")
        else:
            print("User not found.")
    except Exception as e:
        print(f"Error removing user: {e}")

def add_fine_category():
    """Adds a new fine category."""

    category_type = input("Enter category type (e.g., 'Library', 'Hostel'): ")
    amount = float(input("Enter fine amount: "))

    category = {
        "type": category_type,
        "amount": amount
    }

    try:
        db.fine_categories.insert_one(category)
        print("Fine category added successfully!")
    except Exception as e:
        print(f"Error adding fine category: {e}")

def view_fine_categories():
    """Displays all fine categories."""

    categories = list(db.fine_categories.find())
    if categories:
        for category in categories:
            print(f"Type: {category['type']}, Amount: {category['amount']}")
    else:
        print("No fine categories found.")

def remove_fine_category():
    """Removes a fine category."""

    category_type = input("Enter category type to remove: ")
    try:
        result = db.fine_categories.delete_one({"type": category_type})
        if result.deleted_count:
            print("Fine category removed successfully!")
        else:
            print("Fine category not found.")
    except Exception as e:
        print(f"Error removing fine category: {e}")

def add_student():
    """Adds a new student."""

    id = input("Enter student id: ")
    name = input("Enter student name: ")
    email = input("Enter student email: ")

    student = {
        "id": id,
        "name": name,
        "email": email
    }

    try:
        db.students.insert_one(student)
        print("Student added successfully!")
    except Exception as e:
        print(f"Error adding student: {e}")

def view_students():
    """Displays all students."""

    students = list(db.students.find())
    if students:
        for student in students:
            print(f"id: {student['id']}, Name: {student['name']}, Email: {student['email']}")
    else:
        print("No students found.")

def remove_student():
    """Removes a student."""

    id = input("Enter student id to remove: ")
    try:
        result = db.students.delete_one({"id": id})
        if result.deleted_count:
            print("Student removed successfully!")
        else:
            print("Student not found.")
    except Exception as e:
        print(f"Error removing student: {e}")

def main_menu():
    """Displays the main menu and handles user input."""

    while True:
        os.system('cls')
        print("\n--- Management Tool ---")
        print("1. Manage Users")
        print("2. Manage Fine Categories")
        print("3. Manage Students")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            manage_users_menu()
        elif choice == "2":
            manage_fine_categories_menu()
        elif choice == "3":
            manage_students_menu()
        elif choice == "4":
            return
        else:
            print("Invalid choice. Please try again.")
        input()

def manage_users_menu():
    """Menu for managing users."""

    while True:
        os.system('cls')
        print("\n--- Manage Users ---")
        print("1. Add User")
        print("2. View Users")
        print("3. Remove User")
        print("4. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_user()
        elif choice == "2":
            view_users()
        elif choice == "3":
            remove_user()
        elif choice == "4":
            return
        else:
            print("Invalid choice. Please try again.")
        input()

def manage_fine_categories_menu():
    """Menu for managing fine categories."""

    while True:
        os.system('cls')
        print("\n--- Manage Fine Categories ---")
        print("1. Add Fine Category")
        print("2. View Fine Categories")
        print("3. Remove Fine Category")
        print("4. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_fine_category()
        elif choice == "2":
            view_fine_categories()
        elif choice == "3":
            remove_fine_category()
        elif choice == "4":
            return
        else:
            print("Invalid choice. Please try again.")
        input()

def manage_students_menu():
    """Menu for managing students."""

    while True:
        os.system('cls')
        print("\n--- Manage Students ---")
        print("1. Add Student")
        print("2. View Students")
        print("3. Remove Student")
        print("4. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            add_student()
        elif choice == "2":
            view_students()
        elif choice == "3":
            remove_student()
        elif choice == "4":
            return
        else:
            print("Invalid choice. Please try again.")
        input()

if __name__ == "__main__":
    main_menu()