import sqlite3
import document_functions
from datetime import datetime
import json


#---------------------------------Create Table--------------------------------------------------#

#---Create Admin Logins
def add_admin_login():
    with sqlite3.connect('admin.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS logins(
            position TEXT,
            password TEXT,
            is_locked INTEGER DEFAULT 0
        )
        ''')
        conn.commit()

#----------------current fees table
def current_fees():
    with sqlite3.connect('fees.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS current_fees(
            term NUMBER,
            amount REAL
        )
        ''')
        conn.commit()

#===Create manager logins table
def add_manager_login():
    with sqlite3.connect('manager.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS logins(
            username TEXT,
            password TEXT
        )
        ''')
        conn.commit()

def add_manager(username, password):
    with sqlite3.connect('manager.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logins (
               username,
               password
                ) VALUES (?, ?)
            ''', (username, password))
        conn.commit()


#---Create Admin Details ----------
def add_admin_data():
    with sqlite3.connect('admin.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_admin(
            admin_id TEXT PRIMARY KEY,
            position TEXT,
            f_name TEXT,
            m_name TEXT,
            l_name TEXT,
            gender NUMBER,
            age NUMBER
        )
        ''')
        conn.commit()


#create table students

def init_student_add_name():
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS students(
             admission_no TEXT PRIMARY KEY,
             first_name TEXT,
             middle_name TEXT,
             last_name TEXT,
             gender TEXT,
             AGE INTEGER
        )
        ''')
        conn.commit()


#create rest table that contains the rest of the student data
def init_student_add_level():
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rest(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admission_no TEXT,
            Grade TEXT,
            FOREIGN KEY (admission_no) REFERENCES students (admission_no)
        )
        ''')
        conn.commit()


#Add subjects per student
subject = ['Mathematics', 'Biology', 'Chemistry', 'Physics', 'Geography', 'Business',
           'English', 'Kiswahili', 'CRE', 'French']


#Add Logins Table
def init_logins():
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS logins(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admission_no TEXT,
            password TEXT,
            is_locked INTEGER DEFAULT 0,
            FOREIGN KEY (admission_no) REFERENCES students (admission_no)
        )
        ''')
        conn.commit()


#-------------------------------Get Details From The DataBase-----------------------------------#
#get First name
def get_first_name(admission_no):
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT first_name
            FROM students
            WHERE admission_no = ?
        ''', (admission_no,))

        result = cursor.fetchone()
    if result:
        return result[0]  # Return the first name
    else:
        return None


def get_first_name_t(username):
    with sqlite3.connect('admin.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT f_name
            FROM admin_data
            WHERE position = ?
        ''', (username,))

        result = cursor.fetchone()
    if result:
        return result[0]  # Return the first name
    else:
        return None


def get_middle_name(admission_no):
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT middle_name
            FROM students
            WHERE admission_no = ?
        ''', (admission_no,))

        result = cursor.fetchone()
    if result:
        return result[0]  # Return the middle name
    else:
        return None


def get_last_name(admission_no):
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT last_name
            FROM students
            WHERE admission_no = ?
        ''', (admission_no,))

        result = cursor.fetchone()
    if result:
        return result[0]  # Return the last name
    else:
        return None
def get_admission_date_st(admission_no):
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT admission_date
            FROM rest
            WHERE admission_no = ?
        ''', (admission_no,))

        result = cursor.fetchone()
    if result:
        return result[0]  # Return the last name
    else:
        return None

def get_grade_st(admission_no):
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT grade
            FROM rest
            WHERE admission_no = ?
        ''', (admission_no,))

        result = cursor.fetchone()
    if result:
        return result[0]  # Return the last name
    else:
        return None


def get_last_name_t(username):
    with sqlite3.connect('admin.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT l_name
            FROM admin_data
            WHERE position = ?
        ''', (username,))

        result = cursor.fetchone()
    if result:
        return result[0]  # Return the last name
    else:
        return None

def get_email(admission_no):
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT email
            FROM students
            WHERE admission_no = ?
        ''',(admission_no,))
        result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

def get_email_t(username):
    with sqlite3.connect('admin.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT email
            FROM teachers
            WHERE username = ?
        ''',(username,))
        result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

def get_phone(admission_no):
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT phone_number
            FROM rest
            WHERE admission_no = ?
        ''',(admission_no,))
        result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

def get_phone_t(username):
    with sqlite3.connect('admin.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT phone
            FROM teachers
            WHERE username = ?
        ''',(username,))
        result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

def get_gender(admission_no):
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT gender
            FROM students
            WHERE admission_no = ?
        ''',(admission_no,))
        result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

def get_gender_t(username):
    with sqlite3.connect('admin.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT gender
            FROM admin_data
            WHERE position = ?
        ''',(username,))
        result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None


def get_join_date_t(username):
    with sqlite3.connect('admin.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT date
            FROM teachers
            WHERE username = ?
        ''',(username,))
        result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None


import sqlite3
import base64

def get_profile(admission_no: str) -> str:
    try:
        conn = sqlite3.connect('student.db')
        cursor = conn.cursor()
        cursor.execute("SELECT profile_pic FROM students WHERE admission_no = ?", (admission_no,))
        result = cursor.fetchone()

        if result and result[0]:
            # Convert binary data to base64
            base64_image = base64.b64encode(result[0]).decode('utf-8')
            return f"data:image/png;base64,{base64_image}"
        else:
            print("No image found for the given admission number.")
            return None

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()

def get_aprofile(username: str) -> str:
    try:
        conn = sqlite3.connect('manager.db')
        cursor = conn.cursor()
        cursor.execute("""
        SELECT m.profile_picture
        FROM manager AS m
        INNER JOIN logins AS l ON m.manager_id = l.manager_id
        WHERE l.username = ?
        """, (username,))

        result = cursor.fetchone()

        if result and result[0]:
            # Convert binary data to base64
            base64_image = base64.b64encode(result[0]).decode('utf-8')
            return f"data:image/png;base64,{base64_image}"
        else:
            print("No image found for the given admission number.")
            return None

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()
def get_qr_pic_st(admission_no: str) -> str:
    try:
        conn = sqlite3.connect('student.db')
        cursor = conn.cursor()
        cursor.execute("SELECT qrcode_st FROM students WHERE admission_no = ?", (admission_no,))
        result = cursor.fetchone()

        if result and result[0]:
            # Convert binary data to base64
            base64_image = base64.b64encode(result[0]).decode('utf-8')
            return f"data:image/png;base64,{base64_image}"
        else:
            print("No qrcode found for the given admission number.")
            return None

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()

#=====================Teachers profile picture
def get_profile_t(username: str) -> str:
    try:
        conn = sqlite3.connect('admin.db')
        cursor = conn.cursor()
        cursor.execute("SELECT profile_picture FROM admin_data WHERE position = ?", (username,))
        result = cursor.fetchone()

        if result and result[0]:
            # Convert binary data to base64
            base64_image = base64.b64encode(result[0]).decode('utf-8')
            return f"data:image/png;base64,{base64_image}"
        else:
            print("No image found for the given admission number.")
            return None

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()





#---------Get
# def view_students():
#     # Connect to the SQLite database
#     conn = sqlite3.connect('student.db')
#     cursor = conn.cursor()

#     # Fetch all students
#     cursor.execute('''SELECT students.admission_no, students.first_name, students.last_name, rest.Grade
#         FROM students
#         JOIN rest
#         ON students.admission_no = rest.admission_no
#         ORDER BY rest.Grade DESC''')
#     students = cursor.fetchall()
#     processed_students = [
#         (document_functions.replace_slash_with_dot(student[0]), student[1].capitalize(), student[2].capitalize(),student[3])
#         for student in students
#     ]
#     # Close the connection
#     conn.close()
#     return processed_students
def view_students(grade_list):
    # Connect to the SQLite database
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()

    # Define the list of grades to filter


    # Create a query with placeholders for dynamic filtering
    query = '''SELECT students.admission_no, students.first_name, students.last_name, rest.Grade
               FROM students
               JOIN rest ON students.admission_no = rest.admission_no
               WHERE rest.Grade IN ({})
               ORDER BY rest.Grade DESC'''.format(','.join(['?'] * len(grade_list)))

    # Execute the query with the grade_list values
    cursor.execute(query, grade_list)
    students = cursor.fetchall()

    # Process student data
    processed_students = [
        (document_functions.replace_slash_with_dot(student[0]), student[1].capitalize(), student[2].capitalize(), student[3])
        for student in students
    ]

    # Close the connection
    conn.close()
    return processed_students



#-----------Get Students and Their Marks

def get_students_and_subjects():
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()

        # Query to select first_name, last_name, and all subjects for each student
        query = '''
        SELECT s.first_name, s.last_name, sub.*
        FROM students s
        INNER JOIN marks sub ON s.admission_no = sub.admission_no
        ORDER BY sub.average
        '''

        cursor.execute(query)
        result = cursor.fetchall()

    return result


#-------------------------------Put Data To Database-------------------------------------------#
#Enter data To Students table
def add_someone(admission_no, f_name, m_name, l_name, gender, age, email):
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO students (
            admission_no,
            first_name,
            middle_name,
            last_name,
            gender,
            AGE,
            email
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (admission_no, f_name, m_name, l_name, gender, age, email))
        conn.commit()


#-----Add details to logins table Admin
def add_admin_login1(position, password):
    with sqlite3.connect('admin.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO logins(position,password
        )VALUES (?,?)
        ''', (position, password))
        conn.commit()


#-------------add full admin details
def add_admin_data1(position, f_name, m_name, l_name, gender, age):
    with sqlite3.connect('admin.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO admin_data(
            position,
             f_name,
             m_name,
             l_name,
             gender,
             age
                ) VALUES (?, ?,?,?,?,?)
            ''', (position.capitalize(), f_name.capitalize(), m_name.capitalize(), l_name.capitalize(), gender.capitalize(), age))
        conn.commit()


def add_login(admission_no, password):
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logins (
            admission_no,
            password
                ) VALUES (?, ?)
            ''', (admission_no, password))
        conn.commit()


#add details rest table Contains the Class of the student
def add_level(admission_no, grade, phone, admission_date):
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO rest(
            admission_no,
            Grade,
            phone_number,
            admission_date
                ) VALUES (?, ?, ?, ?)
            ''', (admission_no, grade, phone, admission_date))
        conn.commit()


#=================insert Marks of Each Student

# def insert_marks(year,time,exam_type,admission_no, marks_list):
#     if len(marks_list) != len(subject):
#         raise ValueError("Marks list length must match the number of subjects.")

#     with sqlite3.connect('student.db') as conn:
#         cursor = conn.cursor()

#         # Build the SQL query dynamically based on the subjects
#         query =  f'''
#             UPDATE Examinations
#             SET {', '.join([f"{subj} = ?" for subj in subject])}
#             WHERE admission_no = ? AND year = ? AND term = ? AND type = ?
#         '''

#         # Execute the update; if no row was updated, insert a new one (upsert behavior)
#         cursor.execute(query, (*marks_list, admission_no, year, time, exam_type))
#         if cursor.rowcount == 0:
#             # Build insert statement: admission_no, year, term, type, <subjects...>
#             cols = 'admission_no, year, term, type, ' + ', '.join(subject)
#             placeholders = ','.join(['?'] * (4 + len(subject)))
#             insert_query = f"INSERT INTO Examinations ({cols}) VALUES ({placeholders})"
#             cursor.execute(insert_query, (admission_no, year, time, exam_type, *marks_list))

#         conn.commit()

import json

# def insert_marks(year, term, exam_type, admission_no, marks):
#     conn = sqlite3.connect("student.db")
#     cursor = conn.cursor()

#     # Optional: prevent duplicates
#     cursor.execute("""
#         DELETE FROM marks
#         WHERE admission_no=? AND year=? AND term=? AND exam_type=?
#     """, (admission_no, year, term, exam_type))

#     cursor.execute("""
#         INSERT INTO marks (year, term, exam_type, admission_no, marks_json)
#         VALUES (?, ?, ?, ?, ?)
#     """, (
#         year,
#         term,
#         exam_type,
#         admission_no,
#         json.dumps(marks)
#     ))

#     conn.commit()
#     conn.close()
def insert_marks(admission_no, year, term, exam_type, marks, average):
    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Optional: delete previous marks for the same student/exam
    cursor.execute("""
        DELETE FROM marks
        WHERE admission_no=? AND year=? AND term=? AND exam_type=?
    """, (admission_no, year, term, exam_type))

    # Insert new marks
    cursor.execute("""
        INSERT INTO marks (admission_no, year, term, exam_type, marks_json, average)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        admission_no,
        year,
        term,
        exam_type,
        json.dumps(marks),
        average
    ))

    conn.commit()
    conn.close()

def insert_time(admission_no, year, term, exam_type):
    """Initialize or ensure a marks record exists for a student's exam"""
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        # Check if a record already exists
        cursor.execute('''
            SELECT id FROM marks 
            WHERE admission_no = ? AND year = ? AND term = ? AND exam_type = ?
        ''', (admission_no, year, term, exam_type))
        
        existing = cursor.fetchone()
        if not existing:
            # Initialize with empty marks JSON
            cursor.execute('''
                INSERT INTO marks (admission_no, year, term, exam_type, marks_json)
                VALUES (?, ?, ?, ?, ?)
            ''', (admission_no, year, term, exam_type, json.dumps({})))
            conn.commit()

#remove data from the database


def remove_student_login(admission_no):
    # Connect to the SQLite database
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()

        # Define the SQL query with a parameter placeholder
        query = '''
            DELETE FROM logins WHERE admission_no = ?
        '''

        # Execute the query with the admission number as the parameter
        cursor.execute(query, (admission_no,))

        # Commit the transaction to make sure the deletion is saved
        conn.commit()


def remove_student_details(admission_no):
    """
    Removes a student login record from the 'logins' table in the database
    based on the given admission number.

    Parameters:
        admission_no (str): The admission number of the student whose login record should be removed.
    """
    # Connect to the SQLite database
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()

        # Define the SQL query with a parameter placeholder
        query = '''
            DELETE FROM students WHERE admission_no = ?
        '''

        # Execute the query with the admission number as the parameter
        cursor.execute(query, (admission_no,))

        # Commit the transaction to make sure the deletion is saved
        conn.commit()


def remove_student_subjects(admission_no):
    """
    Removes a student login record from the 'logins' table in the database
    based on the given admission number.

    Parameters:
        admission_no (str): The admission number of the student whose login record should be removed.
    """
    # Connect to the SQLite database
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()

        # Define the SQL query with a parameter placeholder
        query = '''
            DELETE FROM subjects WHERE admission_no = ?
        '''

        # Execute the query with the admission number as the parameter
        cursor.execute(query, (admission_no,))

        # Commit the transaction to make sure the deletion is saved
        conn.commit()

def del_teacher_details(username):

    # Connect to the SQLite database
    with sqlite3.connect('admin.db') as conn:
        cursor = conn.cursor()

        # Define the SQL query with a parameter placeholder
        query = '''
            DELETE FROM admin_data WHERE position = ?
        '''

        # Execute the query with the admission number as the parameter
        cursor.execute(query, (username,))

        # Commit the transaction to make sure the deletion is saved
        conn.commit()
def del_teacher(username):

    # Connect to the SQLite database
    with sqlite3.connect('admin.db') as conn:
        cursor = conn.cursor()

        # Define the SQL query with a parameter placeholder
        query = '''
            DELETE FROM teachers WHERE username = ?
        '''

        # Execute the query with the admission number as the parameter
        cursor.execute(query, (username,))

        # Commit the transaction to make sure the deletion is saved
        conn.commit()

def del_teacher_logins(username):

    # Connect to the SQLite database
    with sqlite3.connect('admin.db') as conn:
        cursor = conn.cursor()

        # Define the SQL query with a parameter placeholder
        query = '''
            DELETE FROM logins WHERE position = ?
        '''

        # Execute the query with the admission number as the parameter
        cursor.execute(query, (username,))

        # Commit the transaction to make sure the deletion is saved
        conn.commit()

#------------Delete all Teacher data --------------------
def delete_teacher(username):
    del_teacher_details(username)
    del_teacher_logins(username)
    del_teacher(username)


#--------------Remove all data from a student----------------------------
def delete_student(admission_no):
    remove_student_details(admission_no)
    remove_student_subjects(admission_no)
    remove_student_login(admission_no)


#==============================Exams Table=================================================#

def init_exams_table():
    # Examinations table has been replaced with marks table
    pass


#===================Student Fees Table
def fee_table():
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fees_student(
            admission_no TEXT,
            pay REAL,
            payday DATETIME,
            balance REAL,
            FOREIGN KEY (admission_no) REFERENCES students (admission_no)
        )
        ''')
        conn.commit()


def default_fee():
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fees(
            term NUMBER,
            amount REAL
        )
        ''')
        conn.commit()

def set_fee(admission_no,pay,payday,balance):
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO fees_student (
            admission_no,
            pay,
            payday,
            balance
                ) VALUES (?, ?, ?, ?)
            ''', (admission_no, pay,payday,balance))
        conn.commit()


#==============Non Compliant Students
def add_non_compliant_students():
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS non_compliant(
            admission_no TEXT,
            send_date TIMESTAMP,
            return_date TIMESTAMP,
            duration TEXT,
            reason TEXT,
            status TEXT,
            FOREIGN KEY (admission_no) REFERENCES students (admission_no)
        )
        ''')
        conn.commit()

def insert_non_compliant_students(admission_no, send_date,return_date,duration,reason,status):
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
                INSERT INTO non_compliant(
                    admission_no ,
                    send_date,
                    return_date,
                    duration,
                    reason,
                    status


                )  VALUES (?, ?, ?, ?,?,?)
            ''', (admission_no, send_date,return_date,duration,reason.capitalize(),status))
        conn.commit()


#=============View All Non Compliant Students
def non_compliant_students():
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT students.admission_no, students.first_name, students.last_name, non_compliant.reason,non_compliant.duration,non_compliant.send_date,non_compliant.return_date,non_compliant.status
            FROM students
            INNER JOIN non_compliant ON students.admission_no = non_compliant.admission_no
        ''')
        result = cursor.fetchall()
        # Process the result to replace slashes with dots
        processed_results = [
            (document_functions.replace_slash_with_dot(res[0]), res[1].capitalize(), res[2].capitalize(), res[3].capitalize(), res[4], res[5], res[6], res[7])
            for res in result
        ]
        # Close the connection
        return processed_results

def add_ill_students():
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ill_students(
            admission_no TEXT,
            sick TEXT,
            description TEXT
        )
        ''')
        conn.commit()

def put_ill_students(admission_no,sick,description):
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        if sick:
            cursor.execute('''
            INSERT INTO ill_students(
                admission_no,sick,description
            )VALUES (?, ?, ?)
            ''', (admission_no,sick.capitalize(),description.capitalize()))
            conn.commit()

def get_ill_students():
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT students.admission_no, students.first_name, students.last_name, ill_students.sick, ill_students.description
        FROM students
        INNER JOIN ill_students ON students.admission_no = ill_students.admission_no
        ''')
        result = cursor.fetchall()
        # Process the result to replace slashes with dots
        processed_results = [
            (document_functions.replace_slash_with_dot(res[0]), res[1].capitalize(), res[2].capitalize(), res[3].capitalize(), res[4])
            for res in result
        ]
        # Close the connection
        return processed_results
#======================Manager Database=======================
def add_Manager_details():
    with sqlite3.connect('manager.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS manager(
            manager_id TEXT PRIMARY KEY,
            f_name TEXT,
            m_name TEXT,
            l_name TEXT,
            position TEXT
        )
        ''')
        conn.commit()

#====================
def get_students_with_balance():
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute("ATTACH DATABASE 'fees.db' AS feesdb")

        # Query to fetch students with balance > 0
        query = """
            SELECT s.admission_no, s.first_name, s.middle_name, s.last_name, f.remaining_balance
            FROM students s
            JOIN feesdb.students f ON s.admission_no = f.admission_number
            WHERE f.remaining_balance > 0
            ORDER BY f.remaining_balance DESC
        """

        cursor.execute(query)
        students_with_balance = cursor.fetchall()
        return students_with_balance

# check if admission exists
def student_exist(admission_no):
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE admission_no = ?", (admission_no,))
        existing_student = cursor.fetchone()
        return existing_student

# check if Student's email exist
def student_email_exists(email):
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE email = ?",(email,))
        existing_email = cursor.fetchone()
        return existing_email

#============average Table
def average_table():
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS average(
            admission_no TEXT,
            average REAL,
            FOREIGN KEY (admission_no) REFERENCES students (admission_no)
        )
        ''')
        conn.commit()

def add_column_average():
    # Examinations table has been replaced with marks table
    # Average is now calculated from marks_json in marks table
    pass

def get_all_students_exams():
    """Get all students with their exam marks from the marks table"""
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT students.admission_no, students.first_name
            FROM students
            JOIN marks ON students.admission_no = marks.admission_no
            ORDER BY students.first_name
        ''')
        result = cursor.fetchall()
    
    return result



def set_average(admission_no, term, year, exam_type):
    """Calculate and store the average for a student's exam marks"""
    conn = sqlite3.connect("student.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT marks_json FROM marks
        WHERE admission_no=? AND term=? AND year=? AND exam_type=?
    """, (admission_no, term, year, exam_type))

    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    
    try:
        marks = json.loads(row[0])
        if not marks:
            conn.close()
            return None
        
        average = round(sum(marks.values()) / len(marks), 2)
        
        # Update the average in the marks table if it has an average column
        # For now, we'll just return the average since we need to check the table schema
        conn.close()
        return average
    except (json.JSONDecodeError, ValueError):
        conn.close()
        return None



def get_students_marks_filtered(year, term, exam_type, grade):
    """
    Get students in a specific grade who have marks recorded for a given year, term, and exam type.
    Returns: List of tuples (admission_no, first_name, average) sorted by average descending
    """
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        # Get students in the specified grade that have marks for this exam
        cursor.execute('''
            SELECT students.admission_no, students.first_name, marks.marks_json
            FROM students
            JOIN marks ON students.admission_no = marks.admission_no
            JOIN rest ON students.admission_no = rest.admission_no
            WHERE marks.year = ? AND marks.term = ? AND marks.exam_type = ? AND rest.grade = ?
            ORDER BY students.first_name
        ''', (year, term, exam_type, grade))
        results = cursor.fetchall()
    
    # Calculate averages and prepare final results
    final_results = []
    for admission_no, first_name, marks_json in results:
        try:
            marks = json.loads(marks_json)
            if marks:
                average = round(sum(marks.values()) / len(marks), 2)
            else:
                average = 0
        except (json.JSONDecodeError, ValueError):
            average = 0
        
        final_results.append((admission_no, first_name, average))
    
    # Sort by average descending
    final_results.sort(key=lambda x: x[2], reverse=True)
    
    return final_results


def setup_database():
    conn = sqlite3.connect('fees.db')
    cursor = conn.cursor()

    # Create students table (if it doesn't exist)

    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS students (
            admission_number TEXT PRIMARY KEY,
            total_paid REAL DEFAULT 0,
            remaining_balance REAL DEFAULT {document_functions.current_fee()}
        )
    ''')

    # Create payment history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admission_number TEXT,
            amount_paid REAL,
            remaining_balance REAL,
            date_time TEXT,
            FOREIGN KEY (admission_number) REFERENCES students(admission_number)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fees (
            admission_no TEXT,
            total_fee REAL,
            paid_amount REAL DEFAULT 0,
            balance_amount REAL DEFAULT 0,
            last_payment_date TEXT,
            FOREIGN KEY (admission_no) REFERENCES students(admission_no)
        )
    ''')



    conn.commit()
    conn.close()

#==============Fee Processing
def current_fee():
    with sqlite3.connect('fees.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
         SELECT term, amount FROM current_fee
        )
        ''')
        data = cursor.fetchone()
        return data

#======================================================================
def fee_data():
    with sqlite3.connect('fees.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM fee
        ''')
        fee_details = cursor.fetchall()
    return fee_details
#====================================================================
def get_admission_number(first_name, last_name):
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT admission_no FROM students
        WHERE first_name = ?
        AND last_name = ?
        ''',(first_name.upper(), last_name.upper()))
        admission_number = cursor.fetchone()[0]
    return admission_number
#==================GET ADMISSION DATE
def get_admission_date(admission_no):
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT admission_date
        FROM rest
        WHERE admission_no = ?
        ''',(admission_no,))
        admission_date = cursor.fetchone()[0]
    return admission_date
#===============GET EXAM TYPE
def get_exam_type(admission_no):
    """Get list of exam types for a student from the marks table"""
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT exam_type
            FROM marks
            WHERE admission_no = ?
        ''', (admission_no,))
        exam_list = cursor.fetchall()
    
    return [exam[0] for exam in exam_list] if exam_list else []


def teachers():
    conn = sqlite3.connect('admin.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            phone TEXT,
            grade TEXT,
            subject TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def teachers_email():
    with sqlite3.connect('admin.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT email FROM teachers
        ''')
        result = cursor.fetchall()
        return result

def students_email():
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT email FROM students
        ''')
        result = cursor.fetchall()
        return result






def add_all_tables():
    current_fees()
    add_admin_login()
    add_admin_data()
    init_logins()
    init_student_add_level()
    init_student_add_name()
    init_exams_table()
    fee_table()
    default_fee()
    add_ill_students()
    add_Manager_details()
    add_admin_data()
    add_non_compliant_students()
    setup_database()
    teachers()
    # Import and initialize subject enrollment table
    try:
        import enroll_subjects
        enroll_subjects.init_student_subject_enrollment_table()
        migrate_subject_enrollment_table()
    except Exception as e:
        print(f"Warning: Could not initialize subject enrollment table: {e}")
    
    # Initialize attendance table
    try:
        init_attendance_table()
    except Exception as e:
        print(f"Warning: Could not initialize attendance table: {e}")

def migrate_subject_enrollment_table():
    """Migrate subject_subject_enrollment table to include year column if needed"""
    try:
        with sqlite3.connect('student.db') as conn:
            cursor = conn.cursor()
            # Check if year column exists
            cursor.execute("PRAGMA table_info(student_subject_enrollment)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'year' not in columns:
                # Column doesn't exist, we need to migrate
                # Create a new table with the year column
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS student_subject_enrollment_new(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admission_no TEXT,
                    subject TEXT,
                    year TEXT,
                    enrollment_date DATETIME,
                    status TEXT DEFAULT 'active',
                    FOREIGN KEY (admission_no) REFERENCES students (admission_no),
                    UNIQUE(admission_no, subject, year)
                )
                ''')
                
                # Copy existing data, assuming all old records are for current year
                current_year = str(datetime.now().year)
                cursor.execute('''
                INSERT INTO student_subject_enrollment_new (id, admission_no, subject, year, enrollment_date, status)
                SELECT id, admission_no, subject, ?, enrollment_date, status
                FROM student_subject_enrollment
                ''', (current_year,))
                
                # Drop old table and rename new one
                cursor.execute('DROP TABLE student_subject_enrollment')
                cursor.execute('ALTER TABLE student_subject_enrollment_new RENAME TO student_subject_enrollment')
                conn.commit()
    except Exception as e:
        print(f"Warning: Could not migrate subject enrollment table: {e}")
#===============Get Emails for each person  as per db_name, tableName, colName

def get_emails(db_name, tableName, colName):
    try:
        # Connect to the database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Execute query to fetch all emails
        cursor.execute(f"SELECT {colName} FROM {tableName}")
        emails = [row[0] for row in cursor.fetchall()]

        # Close the connection
        conn.close()

        return emails
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []




#======get student password as per email
def get_password_s(db_name, email):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Query to fetch the password for the given username
        cursor.execute('''SELECT logins.password
        FROM logins
        JOIN students ON logins.admission_no = students.admission_no
        WHERE students.email = ?''', (email,))
        result = cursor.fetchone()

        # Close the connection
        conn.close()

        # Return the password if found, otherwise return None
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


#=======================Get password as per manager
def get_password_m(db_name, email):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Query to fetch the password for the given username
        cursor.execute('''SELECT logins.password
        FROM logins
        JOIN manager ON logins.username = manager.position
        WHERE manager.email = ?''', (email,))

        result = cursor.fetchone()

        # Close the connection
        conn.close()

        # Return the password if found, otherwise return None
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

#===========================Get password from registered teachers
def get_password_t(db_name, email):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Query to fetch the password for the given username
        cursor.execute('''SELECT logins.password
        FROM logins
        JOIN teachers ON logins.position = teachers.username
        WHERE teachers.email = ?''', (email,))
        result = cursor.fetchone()

        # Close the connection
        conn.close()
        # Return the password if found, otherwise return None
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None


# ======================== ATTENDANCE MANAGEMENT ========================

def init_attendance_table():
    """Create attendance table for tracking student attendance"""
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admission_no TEXT,
            date TEXT,
            time_in TEXT,
            time_out TEXT,
            status TEXT DEFAULT 'present',
            marked_by TEXT,
            marked_out_by TEXT,
            FOREIGN KEY (admission_no) REFERENCES students (admission_no),
            UNIQUE(admission_no, date)
        )
        ''')
        conn.commit()
        
        # Add time_out and marked_out_by columns if they don't exist (for existing databases)
        try:
            cursor.execute('ALTER TABLE attendance ADD COLUMN time_out TEXT')
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass
        
        try:
            cursor.execute('ALTER TABLE attendance ADD COLUMN marked_out_by TEXT')
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists
            pass


def mark_student_attendance(admission_no, date, time_in, marked_by):
    """Mark a student as present"""
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO attendance (admission_no, date, time_in, status, marked_by)
            VALUES (?, ?, ?, 'present', ?)
            ''', (admission_no, date, time_in, marked_by))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error marking attendance: {e}")
            return False


def get_attendance_record(admission_no, date):
    """Get attendance record for a student on a specific date"""
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT id, status, time_in FROM attendance
        WHERE admission_no = ? AND date = ?
        ''', (admission_no, date))
        return cursor.fetchone()


def get_student_attendance_by_date(date):
    """Get all attendance records for a specific date"""
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT s.admission_no, s.first_name, s.last_name, a.status, a.time_in
        FROM attendance a
        JOIN students s ON a.admission_no = s.admission_no
        WHERE a.date = ?
        ORDER BY a.time_in DESC
        ''', (date,))
        return cursor.fetchall()


def get_class_attendance(grade, date):
    """Get attendance for all students in a class on a specific date"""
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT s.admission_no, s.first_name, s.last_name, 
               CASE WHEN a.id IS NOT NULL THEN 'present' ELSE 'absent' END as status,
               a.time_in
        FROM students s
        INNER JOIN rest r ON s.admission_no = r.admission_no
        LEFT JOIN attendance a ON s.admission_no = a.admission_no AND a.date = ?
        WHERE r.Grade = ?
        ORDER BY s.last_name, s.first_name
        ''', (date, grade))
        return cursor.fetchall()


def get_student_attendance_history(admission_no, days=30):
    """Get attendance history for a student for the past n days"""
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT date, status, time_in, time_out, marked_by, marked_out_by FROM attendance
        WHERE admission_no = ?
        ORDER BY date DESC
        LIMIT ?
        ''', (admission_no, days))
        return cursor.fetchall()


def mark_student_checkout(admission_no, date, time_out, marked_out_by):
    """Mark a student checkout (time_out) with who marked them out"""
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
            UPDATE attendance 
            SET time_out = ?, marked_out_by = ?
            WHERE admission_no = ? AND date = ?
            ''', (time_out, marked_out_by, admission_no, date))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error marking checkout: {e}")
            return False


def get_checkout_status(admission_no, date):
    """Get checkout status for a student on a specific date"""
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT time_in, time_out, marked_out_by FROM attendance
        WHERE admission_no = ? AND date = ?
        ''', (admission_no, date))
        return cursor.fetchone()


def get_todays_checkouts(date):
    """Get all checkout records for a specific date"""
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT s.admission_no, s.first_name, s.last_name, a.time_in, a.time_out, a.marked_out_by
        FROM attendance a
        JOIN students s ON a.admission_no = s.admission_no
        WHERE a.date = ? AND a.time_out IS NOT NULL
        ORDER BY a.time_out DESC
        ''', (date,))
        return cursor.fetchall()
