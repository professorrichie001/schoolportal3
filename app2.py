
import requests
import profile1
import send_mail1
from requests.auth import HTTPBasicAuth
import base64
import webbrowser
import qrcode3
import qr_scanner
from flask import Flask, render_template, request, redirect,jsonify, flash, url_for, send_from_directory, session, send_file
from werkzeug.utils import secure_filename
import sqlite3, os, database, document_functions, json,requests
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
import logging
import time
import graph2
import pp_compressor

app = Flask(__name__)

app.secret_key = 'My_Secret_Key'

TOTAL_FEES = 2000

# Assignment upload configuration
PROTECTED_ASSIGNMENTS_FOLDER = os.path.join(os.getcwd(), 'protected_assignments')
ALLOWED_ASSIGNMENT_EXTENSIONS = {'.pdf', '.docx', '.doc', '.pptx', '.ppt', '.txt', '.zip', '.rar'}

def allowed_assignment_file(filename):
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_ASSIGNMENT_EXTENSIONS

def ensure_manager_schema(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logins(
            username TEXT,
            password TEXT,
            manager_id TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS manager(
            manager_id TEXT PRIMARY KEY,
            f_name TEXT,
            m_name TEXT,
            l_name TEXT,
            position TEXT,
            email TEXT,
            phone_number TEXT,
            profile_picture BLOB
        )
    ''')

    cursor.execute("PRAGMA table_info(logins)")
    login_cols = {row[1] for row in cursor.fetchall()}
    if "manager_id" not in login_cols:
        cursor.execute("ALTER TABLE logins ADD COLUMN manager_id TEXT")

    cursor.execute("PRAGMA table_info(manager)")
    manager_cols = {row[1] for row in cursor.fetchall()}
    if "email" not in manager_cols:
        cursor.execute("ALTER TABLE manager ADD COLUMN email TEXT")
    if "phone_number" not in manager_cols:
        cursor.execute("ALTER TABLE manager ADD COLUMN phone_number TEXT")
    if "profile_picture" not in manager_cols:
        cursor.execute("ALTER TABLE manager ADD COLUMN profile_picture BLOB")
    if "position" not in manager_cols:
        cursor.execute("ALTER TABLE manager ADD COLUMN position TEXT")

def ensure_student_logins_schema(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logins(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admission_no TEXT,
            password TEXT,
            FOREIGN KEY (admission_no) REFERENCES students (admission_no)
        )
    ''')
    cursor.execute("PRAGMA table_info(logins)")
    login_cols = {row[1] for row in cursor.fetchall()}
    if "is_locked" not in login_cols:
        cursor.execute("ALTER TABLE logins ADD COLUMN is_locked INTEGER DEFAULT 0")

def ensure_admin_logins_schema(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logins(
            position TEXT,
            password TEXT
        )
    ''')
    cursor.execute("PRAGMA table_info(logins)")
    login_cols = {row[1] for row in cursor.fetchall()}
    if "is_locked" not in login_cols:
        cursor.execute("ALTER TABLE logins ADD COLUMN is_locked INTEGER DEFAULT 0")

def manager_signup_required():
    with sqlite3.connect('manager.db') as conn:
        ensure_manager_schema(conn)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM logins')
        count = cursor.fetchone()[0]
    return count == 0

@app.route('/', methods=['GET', 'POST'])
def login():
    if manager_signup_required():
        return redirect(url_for('manager_signup'))

    if request.method == 'POST':

        admission_no = request.form['admission_no']
        password = request.form['password']

        with sqlite3.connect('student.db') as conn:
            ensure_student_logins_schema(conn)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT password, COALESCE(is_locked, 0)
                FROM logins
                WHERE admission_no = ?
            ''', (admission_no,))

            row = cursor.fetchone()
            if row:
                stored_password, is_locked = row[0], row[1]
                if is_locked == 1:
                    return render_template('login.html', error="Your portal is locked. Please contact administration.")
                if stored_password == password:
                    session['admission_no'] = admission_no
                    return redirect(url_for('home'))

        with sqlite3.connect('manager.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT COUNT(*)
            FROM logins
            WHERE username = ? AND password = ?

            ''', (admission_no, password))
            count = cursor.fetchone()[0]
            if count > 0:
                session['username'] = admission_no
                return redirect(url_for('manager_dashboard'))
            else:
                with sqlite3.connect('admin.db') as conn:
                    ensure_admin_logins_schema(conn)
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT password, COALESCE(is_locked, 0)
                        FROM logins
                        WHERE position = ?
                    ''', (admission_no,))
                    row = cursor.fetchone()
                    if row:
                        stored_password, is_locked = row[0], row[1]
                        if is_locked == 1:
                            return render_template('login.html', error="Your portal is locked. Please contact administration.")
                        if stored_password == password:
                            session['userName'] = admission_no
                            return redirect(url_for('admin_dashboard'))

        return render_template('login.html', error="Invalid admission number or password")
    return render_template('login.html')

@app.route('/manager_signup', methods=['GET', 'POST'])
def manager_signup():

    if request.method == 'GET' and not manager_signup_required():
        return redirect(url_for('login'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        f_name = request.form.get('f_name', '')
        m_name = request.form.get('m_name', '')
        l_name = request.form.get('l_name', '')
        position = request.form.get('position', '')
        email = request.form.get('email', '')
        phone_number = request.form.get('phone_number', '')
        password = request.form.get('password', '')
        
        print(f"Received manager signup data: username={username}, f_name={f_name}, m_name={m_name}, l_name={l_name}, position={position}, email={email}, phone_number={phone_number}")

        confirm_password = request.form.get('confirm_password', '')

        if not username or not password:
            error = "Username and password are required."
        elif password != confirm_password:
            error = "Passwords do not match."
        else:
            try:
                with sqlite3.connect('manager.db') as conn:
                    ensure_manager_schema(conn)
                    cursor = conn.cursor()

                    # Insert manager details
                    cursor.execute("""
                        INSERT INTO manager (
                            manager_id, f_name, m_name, l_name,
                            position, email, phone_number
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (username, f_name, m_name, l_name, position, email, phone_number))

                    # Insert login credentials
                    cursor.execute("""
                        INSERT INTO logins (username, password, manager_id)
                        VALUES (?, ?, ?)
                    """, (username, password, username))

                    conn.commit()
                    sender_email = "richardkeith233@gmail.com"
                    sender_password = "mnoj wsox aumw tkrs"
                    subject = "Account created successfully"

                    body = f"Your password is: {password} and your username is: {username}. Please log in and change it."
                    print(f"Sending email to {email}")
                    send_mail1.forgot_m_pass(sender_email,sender_password, email, subject, body)
            # Send email


                return redirect(url_for('login'))

            except sqlite3.IntegrityError:
                # Handles duplicate manager_id / username
                error = "A manager account already exists or this username is taken."

            except Exception as e:
                print("Database error:", e)
                error = "An unexpected error occurred. Please try again."

    return render_template('manager_signup.html', error=error)


#====================profile
@app.route('/home')
def home():
    admission_no = session.get('admission_no')
    admission_number = session.get('admission_no')
    dates, amounts, remaining_balance = graph2.profile(admission_number)
    return render_template('home.html', name=database.get_first_name(admission_no),sname=database.get_last_name(admission_no),email=database.get_email(admission_no),phone = database.get_phone(admission_no), gender= database.get_gender(admission_no),profile_pic = database.get_profile(admission_no),
                           greeting=document_functions.greet_based_on_time(), admission_no=document_functions.replace_slash_with_dot(admission_no),dates=dates, amounts=amounts,remaining_balance=remaining_balance,admission_number= admission_number,\
                           admission_date = database.get_admission_date(admission_number))


#============Teachers_dashboard_test
@app.route('/teachers_dashboard')
def teachers_dashboard():
    return render_template('teachers_dashboard.html')






#=============Update student Qr
@app.route('/updateQrSt')
def student_qr():
    admission_no = session.get('admission_no')
    fname=database.get_first_name(admission_no)
    lname=database.get_last_name(admission_no)
    dob = database.get_admission_date_st(admission_no)
    grade = database.get_grade_st(admission_no)
    qrcode3.generate_qr_st(fname, lname, dob, admission_no, grade)
    profile_pic = database.get_profile(admission_no)
    qrcode_pic = database.get_qr_pic_st(admission_no)
    print("success")
    return render_template('stqrcode.html',profile_pic = profile_pic, qrcode_pic = qrcode_pic)
@app.route('/tdash')
def teacher_home():
    userName = session.get('userName')
    return render_template('thome.html',profile_pic = database.get_profile_t(userName),name = database.get_first_name_t(userName), sname=database.get_last_name_t(userName),email=database.get_email_t(userName),phone = database.get_phone_t(userName), gender= database.get_gender_t(userName), join_date = database.get_join_date_t(userName))
@app.route('/fee')
def fee():
    return render_template('fee.html')





  
@app.route('/student_scores')
def student_scores():
    # keep the incoming id (dot-encoded) for display/URL, but convert back for DB queries
    admission_no = session.get('admission_no')
    admission_no = document_functions.replace_slash_with_dot(admission_no)
    """Render exam trend for a given student (used by the class listing)."""
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()

    # Get the current year and calculate the past four years
    current_year = datetime.now().year
    years = [current_year - i for i in range(4)]

    query = '''
        SELECT year, term, marks_json
        FROM marks
        WHERE admission_no = ? AND year <= ?
        ORDER BY year, term
    '''
    cursor.execute(query, (admission_no, current_year))
    rows = cursor.fetchall()
    conn.close()
    
    # Get enrolled subjects for the current year
    enrolled_subjects = enroll_subjects.get_student_enrolled_subjects(admission_no, current_year)

    exam_scores = {str(year): [] for year in years}
    for row in rows:
        year, term, marks_json = row
        try:
            marks = json.loads(marks_json)
            # Calculate average using only enrolled subjects
            if enrolled_subjects:
                enrolled_marks = {k: v for k, v in marks.items() if k in enrolled_subjects}
                average = round(sum(enrolled_marks.values()) / len(enrolled_marks), 2) if enrolled_marks else None
            else:
                average = round(sum(marks.values()) / len(marks), 2) if marks else None
            exam_scores.setdefault(str(year), []).append(average)
        except (json.JSONDecodeError, ValueError):
            pass

    exam_scores = {year: avg for year, avg in exam_scores.items() if avg}
    exam_list = database.get_exam_type(admission_no)

    # try to get student marks if function exists
    try:
        student_marks = view_student_marks2(admission_no, enrolled_subjects)
    except Exception:
        student_marks = []
    
    return render_template('examtrend.html', base_template='admin_dashboard.html', exam_scores=exam_scores, student_id=admission_no, student_marks=student_marks, length=len(student_marks), profile_pic=database.get_profile(admission_no), exam_list=exam_list, enrolled_subjects=enrolled_subjects)

@app.route('/scores_by_class')
def scores_by_class():
    """Render `student_scores.html` with students grouped by class/grade."""
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()

    # Fetch students and their grade
    cursor.execute('''
        SELECT s.admission_no, s.first_name, s.last_name, r.Grade
        FROM students s
        LEFT JOIN rest r ON s.admission_no = r.admission_no
        ORDER BY r.Grade, s.last_name
    ''')
    rows = cursor.fetchall()

    from collections import defaultdict
    students_by_class = defaultdict(list)

    for admission_no, first, last, grade in rows:
        # fetch latest exam summary (if any)
        cursor.execute('''
            SELECT term, exam_type, marks_json, year
            FROM marks
            WHERE admission_no = ?
            ORDER BY year DESC, term DESC
            LIMIT 1
        ''', (admission_no,))
        exam = cursor.fetchone()
        term = exam[0] if exam else None
        exam_type = exam[1] if exam else None
        average = None
        year_val = exam[3] if exam and len(exam) > 3 else None
        if exam and exam[2]:
            try:
                marks = json.loads(exam[2])
                average = round(sum(marks.values()) / len(marks), 2) if marks else None
            except (json.JSONDecodeError, ValueError):
                pass

        students_by_class[grade or 'Unassigned'].append({
            'id': document_functions.replace_slash_with_dot(admission_no),
            'admission_no': admission_no,
            'name': f"{first.capitalize()} {last.capitalize()}",
            'term': term,
            'exam_type': exam_type,
            'average': average,
            'year': year_val
        })

    conn.close()

    # Sort each class by average descending (None values go last)
    for k, v in students_by_class.items():
        v.sort(key=lambda s: (s['average'] is None, -(s['average'] or 0)))

    # Convert defaultdict to regular dict for the template
    students_by_class = dict(students_by_class)

    # profile_pic for current user if available
    username = session.get('userName')
    admin = document_functions.replace_slash_with_dot(username) if username else None
    print(f"the admin is :{admin}")
    profile_pic = database.get_profile_t(admin) if admin else None

    # collect distinct filter values from marks table
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT exam_type FROM marks')
    exam_types = sorted([r[0] for r in cursor.fetchall() if r[0]])
    cursor.execute('SELECT DISTINCT term FROM marks')
    terms = sorted([r[0] for r in cursor.fetchall() if r[0]])
    cursor.execute('SELECT DISTINCT year FROM marks')
    years = sorted([r[0] for r in cursor.fetchall() if r[0]], reverse=True)
    conn.close()

    # subjects list from database module if available
    try:
        subjects = database.subject
    except Exception:
        subjects = []

    return render_template('student_scores.html', admin=admin, students_by_class=students_by_class, profile_pic=profile_pic, exam_types=exam_types, terms=terms, years=years, subjects=subjects)


@app.route('/examtrend/<student_id>')
def examtrend(student_id):
    # keep the incoming id (dot-encoded) for display/URL, but convert back for DB queries
    display_student_id = student_id
    admission_no = document_functions.replace_slash_with_slash(student_id)
    """Render exam trend for a given student (used by the class listing)."""
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()

    # Get the current year and calculate the past four years
    current_year = datetime.now().year
    years = [current_year - i for i in range(4)]

    query = '''
        SELECT year, term, marks_json
        FROM marks
        WHERE admission_no = ? AND year <= ?
        ORDER BY year, term
    '''
    cursor.execute(query, (admission_no, current_year))
    rows = cursor.fetchall()
    conn.close()

    exam_scores = {str(year): [] for year in years}
    for row in rows:
        year, term, marks_json = row
        try:
            marks = json.loads(marks_json)
            # determine enrolled subjects for averaging
            enrolled_subjects = enroll_subjects.get_student_enrolled_subjects(admission_no, current_year)
            if enrolled_subjects:
                enrolled_marks = {k: v for k, v in marks.items() if k in enrolled_subjects}
                average = round(sum(enrolled_marks.values()) / len(enrolled_marks), 2) if enrolled_marks else None
            else:
                average = round(sum(marks.values()) / len(marks), 2) if marks else None
            exam_scores.setdefault(str(year), []).append(average)
        except (json.JSONDecodeError, ValueError):
            pass

    exam_scores = {year: avg for year, avg in exam_scores.items() if avg}
    exam_list = database.get_exam_type(admission_no)

    # Get enrolled subjects for the current year and fetch structured marks
    enrolled_subjects = enroll_subjects.get_student_enrolled_subjects(admission_no, current_year)
    try:
        student_marks = view_student_marks2(admission_no, enrolled_subjects)
    except Exception:
        student_marks = []

    return render_template('examtrend.html', base_template='admin_dashboard.html', exam_scores=exam_scores, student_id=display_student_id, student_marks=student_marks, length=len(student_marks), profile_pic=database.get_profile(admission_no), exam_list=exam_list, enrolled_subjects=enrolled_subjects)

@app.route('/examtrend2/<student_id>')
def examtrend2(student_id):
    # keep the incoming id (dot-encoded) for display/URL, but convert back for DB queries
    display_student_id = student_id
    admission_no = document_functions.replace_slash_with_slash(student_id)
    """Render exam trend for a given student (used by the class listing)."""
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()

    # Get the current year and calculate the past four years
    current_year = datetime.now().year
    years = [current_year - i for i in range(4)]

    query = '''
        SELECT year, term, marks_json
        FROM marks
        WHERE admission_no = ? AND year <= ?
        ORDER BY year, term
    '''
    cursor.execute(query, (admission_no, current_year))
    rows = cursor.fetchall()
    conn.close()
    
    # Get enrolled subjects for the current year
    enrolled_subjects = enroll_subjects.get_student_enrolled_subjects(admission_no, current_year)

    exam_scores = {str(year): [] for year in years}
    for row in rows:
        year, term, marks_json = row
        try:
            marks = json.loads(marks_json)
            # Calculate average using only enrolled subjects
            if enrolled_subjects:
                enrolled_marks = {k: v for k, v in marks.items() if k in enrolled_subjects}
                average = round(sum(enrolled_marks.values()) / len(enrolled_marks), 2) if enrolled_marks else None
            else:
                average = round(sum(marks.values()) / len(marks), 2) if marks else None
            exam_scores.setdefault(str(year), []).append(average)
        except (json.JSONDecodeError, ValueError):
            pass

    exam_scores = {year: avg for year, avg in exam_scores.items() if avg}
    exam_list = database.get_exam_type(admission_no)

    # try to get student marks if function exists
    try:
        student_marks = view_student_marks2(admission_no, enrolled_subjects)
    except Exception:
        student_marks = []

    return render_template('examtrend2.html', base_template='admin_dashboard.html', exam_scores=exam_scores, student_id=display_student_id, student_marks=student_marks, length=len(student_marks), profile_pic=database.get_profile(admission_no), exam_list=exam_list, enrolled_subjects=enrolled_subjects)

@app.route('/settings')
def settings():
    admission_no = session.get('admission_no')
    profile_pic = database.get_profile(admission_no)
    return render_template('settings.html',profile_pic=profile_pic, admission_no = admission_no)

@app.route('/trainer2')
def trainer2():
    return render_template('trainer2.html')

@app.route('/logout')
def logout():
    admission_no = session.get('admission_no')
    profile_pic = database.get_profile(admission_no)
    return redirect(url_for('login'))


#_______________________________________________________________________________________
#=================================================================================#
#----------------ADMIN----------------------
# List of subjects (make sure the names match the ones in the HTML form)
subjects = ['mathematics', 'biology', 'chemistry', 'physics', 'geography', 'business', 'english', 'kiswahili', 'cre',
            'french']


@app.route('/admin_dash')
def admin_dashboard():
    admission_no = None
    return render_template("admin_dashboard.html", admission_no=admission_no)


# @app.route('/submit_marks', methods=['POST'])
# def submit_marks():
#     # Extract marks from the form and put them into a list
#     marks_list = [int(request.form[subject]) for subject in subjects if request.form.get(subject) not in (None, "")]

#     # For demonstration, let's print the marks list
#     print("Marks List:", marks_list)
#     admission_no = document_functions.replace_slash_with_slash(request.form['admission_no'])
#     exam_type = request.form['exam_type']
#     year = request.form['year']
#     term = request.form['term']
#     # You can now use marks_list for further processing, such as inserting into a database
#     database.insert_marks(year, term, exam_type, admission_no, marks_list)
#     database.set_average(admission_no,term, year, exam_type)

#     return "Marks submitted successfully!"

from flask import request
import json

# @app.route('/submit_marks', methods=['POST'])
# def submit_marks():

#     # Subjects that were actually rendered
#     submitted_subjects = request.form['subjects'].split(',')

#     marks = {}

#     for subject in submitted_subjects:
#         field = subject.lower().replace(" ", "_")
#         value = request.form.get(field)

#         if value not in (None, ""):
#             value = int(value)

#             if not 0 <= value <= 100:
#                 return "Invalid mark entered", 400

#             marks[subject] = value

#     print("Marks Dictionary:", marks)

#     admission_no = document_functions.replace_slash_with_slash(
#         request.form['admission_no']
#     )
#     exam_type = request.form['exam_type']
#     year = request.form['year']
#     term = request.form['term']

#     database.insert_marks(year, term, exam_type, admission_no, marks)
#     database.set_average(admission_no, term, year, exam_type)

    # return "Marks submitted successfully!"
@app.route('/submit_marks', methods=['POST'])
def submit_marks():
    # Subjects that were rendered
    submitted_subjects = request.form['subjects'].split(',')

    # Build marks dictionary
    marks = {}
    for subject in submitted_subjects:
        field = subject.lower().replace(" ", "_")
        value = request.form.get(field)

        if value not in (None, ""):
            value = int(value)
            if not 0 <= value <= 100:
                return f"Invalid mark for {subject}: {value}", 400
            marks[subject] = value

    if not marks:
        return "No marks submitted", 400

    # Calculate average
    average = round(sum(marks.values()) / len(marks), 2)

    # Get other form data
    admission_no = document_functions.replace_slash_with_slash(
        request.form['admission_no']
    )
    exam_type = request.form['exam_type']
    year = request.form['year']
    term = request.form['term']

    # Insert into database
    database.insert_marks(admission_no, year, term, exam_type, marks, average)

    return f"Marks submitted successfully! Average: {average}"




@app.route('/submit_selection', methods=['GET', 'POST'])
def submit_selection():
    return redirect(url_for('enter_student_marks'))


@app.route('/submit_check', methods=['POST'])
def submit_check():
    marks_list = [int(request.form[subject]) for subject in subjects]
    database.insert_marks(document_functions.replace_slash_with_slash(request.form['admission_no']), marks_list)


class_mapping1 = {
    "1": "playgroup",
    "2": "pp1",
    "3": "pp2",
    "4": "grade1",
    "5": "grade2",
    "6": "grade3",
    "7": "grade4",
    "8": "grade5",
    "9": "grade6",
    "10": "grade7",
    "11": "grade8",
    "12": "grade9",
    "13": "grade10",
    "14": "grade11",
    "15": "grade12",
}
class_mapping = {
    "1": "Play group",
    "2": "PP1",
    "3": "PP2",
    "4": "Grade 1",
    "5": "Grade 2",
    "6": "Grade 3",
    "7": "Grade 4",
    "8": "Grade 5",
    "9": "Grade 6",
    "10": "Grade 7",
    "11": "Grade 8",
    "12": "Grade 9",
    "13": "Grade 10",
    "14": "Grade 11",
    "15": "Grade 12",
}

@app.route("/type_check2")
def teacher_classes():
    teacher_id = session.get('userName')
    conn = sqlite3.connect("admin.db")
    cursor = conn.cursor()

    # Fetch the subjects column for the teacher
    cursor.execute("SELECT grade FROM teachers WHERE username = ?", (teacher_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        subject_numbers = [num.strip() for num in result[0].split(",")]
        class_options = {
            num: class_mapping[num]
            for num in subject_numbers
            if num in class_mapping
        }
    else:
        class_options = {}

    return render_template("type_check1.html", class_options=class_options, profile_pic = database.get_profile_t(teacher_id))

@app.route('/type_check')
def type_check():
    teacher_id = session.get('userName')
    conn = sqlite3.connect("admin.db")
    cursor = conn.cursor()

    # Fetch the subjects column for the teacher
    cursor.execute("SELECT grade FROM teachers WHERE username = ?", (teacher_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        subject_numbers = result[0].split(",")  # Convert "4,5,6" to ["4", "5", "6"]
        class_options = {num: class_mapping[num] for num in subject_numbers if num in class_mapping}

    else:
        class_options = {}

    return render_template("type_check.html", class_options=class_options, profile_pic = database.get_profile_t(teacher_id))



@app.route('/students', methods=['GET', 'POST'])
def view_students():
    year = int(request.form['year'])
    term = int(request.form['term'])
    exam_type = request.form['type']
    grade = request.form['class']
    data = database.get_students_marks_filtered(year, term, exam_type, class_mapping1[grade])
    print(f"the data is:{data}")
    return render_template('students_list.html', students=data, year=year, term=term, exam_type=exam_type, grade=class_mapping1[grade])


@app.route('/view_student_exam_scores/<admission_no>')
def view_student_exam_scores(admission_no):
    """View exam scores for a student"""
    admission_n = document_functions.replace_slash_with_slash(admission_no)
    year = request.args.get('year')
    term = request.args.get('term')
    exam_type = request.args.get('exam_type')
    
    # Get student name
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()
    cursor.execute('SELECT first_name FROM students WHERE admission_no = ?', (admission_n,))
    student = cursor.fetchone()
    conn.close()
    
    student_name = student[0] if student else "Unknown"
    
    # Get marks
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT marks_json FROM marks
        WHERE admission_no = ? AND year = ? AND term = ? AND exam_type = ?
    ''', (admission_n, year, term, exam_type))
    result = cursor.fetchone()
    conn.close()
    
    marks = {}
    if result:
        try:
            marks = json.loads(result[0])
        except (json.JSONDecodeError, ValueError):
            marks = {}
    
    return render_template('student_exam_scores.html', 
                          admission_no=admission_n, 
                          student_name=student_name,
                          marks=marks, 
                          year=year, 
                          term=term, 
                          exam_type=exam_type)


@app.route('/download_students_pdf')
def download_students_pdf():
    # Query params: year, term, exam_type, grade, school
    year = request.args.get('year')
    term = request.args.get('term')
    exam_type = request.args.get('exam_type')
    grade = request.args.get('grade')
    school = request.args.get('school') or 'School'

    if not (year and term and exam_type and grade):
        return redirect(url_for('type_check'))

    # Map numeric/class selector values to the DB grade value when necessary
    try:
        db_grade = class_mapping1.get(str(grade), grade)
    except Exception:
        db_grade = grade

    students = database.get_students_marks_filtered(year, term, exam_type, db_grade)

    # Build PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40)
    styles = getSampleStyleSheet()
    elems = []

    # Enhanced styles for PDF
    styles.add(ParagraphStyle(name='TitleCenter', parent=styles['Title'], alignment=1, fontSize=18, leading=22))
    styles.add(ParagraphStyle(name='SubTitleCenter', parent=styles['Normal'], alignment=1, fontSize=10, leading=12))

    title = Paragraph(f"<b><u>{school}</u></b>", styles['TitleCenter'])
    # Display-friendly grade using mapping (e.g., '7' -> 'grade4')
    display_grade = class_mapping1.get(str(grade), grade)
    subtitle = Paragraph(f"<b>Class:</b> {display_grade} &nbsp;&nbsp; <b>Year:</b> {year} &nbsp;&nbsp; <b>Term:</b> {term} &nbsp;&nbsp; <b>Exam:</b> {exam_type}", styles['SubTitleCenter'])
    elems.append(title)
    elems.append(Spacer(1, 6))
    elems.append(subtitle)
    elems.append(Spacer(1, 12))

    # Table data
    data = [['Admission No', 'Name', 'Average (%)', 'Grade']]

    def grade_from_avg(avg):
        try:
            avg = float(avg)
        except Exception:
            return ''
        if avg >= 90:
            return 'EE1'
        if avg >= 75:
            return 'EE2'
        if avg >= 58:
            return 'ME1'
        if avg >= 41:
            return 'ME2'
        if avg >= 31:
            return 'AE1'
        if avg >= 21:
            return 'AE2'
        if avg >= 11:
            return 'BE1'
        return 'BE2'

    for admission_no, first_name, average in students:
        data.append([admission_no, first_name, f"{average}", grade_from_avg(average)])

    if len(data) == 1:
        elems.append(Paragraph('No students found for the selected criteria.', styles['Normal']))
    else:
        table = Table(data, colWidths=[2.2*inch, 2.8*inch, 1.2*inch, 1.0*inch])
        tbl_style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2F5496')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 11),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
            ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('ALIGN', (1,1), (1,-1), 'LEFT'),
            ('ALIGN', (2,1), (2,-1), 'CENTER'),
        ])
        # alternating row backgrounds for body rows
        tbl_style.add('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey])
        table.setStyle(tbl_style)
        elems.append(table)

    doc.build(elems)
    buffer.seek(0)

    filename = f"{school.replace(' ','_')}_{grade}_{year}_term{term}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')



@app.route('/enter_marks/<admission_no>', methods=['GET', 'POST'])
def enter_student_marks(admission_no):
    admission_n = document_functions.replace_slash_with_slash(admission_no)
    # Get parameters from query string or form
    year = request.args.get('year') or request.form.get('year')
    term = request.args.get('term') or request.form.get('term')
    exam_type = request.args.get('type') or request.form.get('type')
    
    if year and term and exam_type:
        term = int(term) if isinstance(term, str) else term
        database.insert_time(admission_n, year, term, exam_type)
        
        # Get enrolled subjects for this student (for this year)
        enrolled_subjects = enroll_subjects.get_student_enrolled_subjects(admission_n, year)

        return render_template('enter_marks.html', admission_no=admission_n, year=year, exam_type=exam_type, term=term, enrolled_subjects=enrolled_subjects)
    
    # If parameters are missing, redirect back
    return redirect(url_for('type_check'))




@app.route('/view_students_marks')
def view_students_marks():
    teacher_id = session.get('userName')
    conn = sqlite3.connect("admin.db")
    cursor = conn.cursor()

    # Fetch the subjects column for the teacher
    cursor.execute("SELECT grade FROM teachers WHERE username = ?", (teacher_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        subject_numbers = result[0].split(",")  # Convert "4,5,6" to ["4", "5", "6"]
        grade_list = [class_mapping1[num] for num in subject_numbers if num in class_mapping1]
        print(grade_list)

    else:
        grade_list = {}
    return render_template('view_students_marks.html', students=database.view_students(grade_list),profile_pic = database.get_profile_t(teacher_id))


@app.route('/<admission_no>')
def enter_marks(admission_no):
    teacher_id = session.get('userName')
    admission_n = document_functions.replace_slash_with_slash(admission_no)
    return render_template('type_checker.html', admission_no=admission_no,
                           first_name=database.get_first_name(admission_n),profile_pic = database.get_profile_t(teacher_id))


@app.route('/exam_list')
def students_results():
    return render_template('exam_list.html', students=database.get_all_students_exams())


#-------------Upload a Memo
# Set the directories for file uploads
BOOKS_FOLDER = 'static/uploads/books/'
IMAGES_FOLDER = 'static/uploads/images/'
app.config['BOOKS_FOLDER'] = BOOKS_FOLDER
app.config['IMAGES_FOLDER'] = IMAGES_FOLDER

# Ensure the upload folders exist
os.makedirs(BOOKS_FOLDER, exist_ok=True)
os.makedirs(IMAGES_FOLDER, exist_ok=True)


@app.route('/memo')
def index():
    # List all uploaded books with their front images
    books = []
    for filename in os.listdir(app.config['BOOKS_FOLDER']):
        image_name = os.path.splitext(filename)[0] + ".jpg"  # Assuming images are uploaded as .jpg
        image_path = os.path.join(app.config['IMAGES_FOLDER'], image_name)
        books.append({
            "filename": filename,
            "image": image_name if os.path.exists(image_path) else None
        })
    return render_template('index.html', books=books)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        image = request.files.get('image')

        if file and file.filename.endswith('.pdf'):
            # Save the PDF book
            filepath = os.path.join(app.config['BOOKS_FOLDER'], file.filename)
            file.save(filepath)

            # Save the front image (if provided)
            if image and image.filename.endswith(('.jpg', '.jpeg', '.png')):
                image_name = os.path.splitext(file.filename)[0] + ".jpg"
                imagepath = os.path.join(app.config['IMAGES_FOLDER'], image_name)
                image.save(imagepath)

            return redirect(url_for('index'))

    return render_template('upload.html')
@app.route('/trainer')
def trainer():
    timer=document_functions.copyright_updater()
    username = session.get('username')
    username = document_functions.replace_slash_with_dot(username)
    profile_pic = database.get_aprofile(username)
    return render_template('trainer.html',timer=timer,profile_pic=profile_pic)

@app.route('/manager_dashboard')
def manager_dashboard():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    username = document_functions.replace_slash_with_dot(username)
    profile_pic = database.get_aprofile(username)

    total_students = 0
    locked_students = 0
    non_compliant = 0
    ill_students = 0
    attendance_today = 0
    with sqlite3.connect('student.db') as conn:
        ensure_student_logins_schema(conn)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admission_no TEXT,
                date TEXT,
                time_in TEXT,
                status TEXT,
                marked_by TEXT,
                time_out TEXT,
                marked_out_by TEXT,
                FOREIGN KEY (admission_no) REFERENCES students (admission_no)
            )
        ''')
        cursor.execute('SELECT COUNT(*) FROM students')
        total_students = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM logins WHERE COALESCE(is_locked, 0) = 1')
        locked_students = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM non_compliant')
        non_compliant = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM ill_students')
        ill_students = cursor.fetchone()[0]
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT COUNT(*) FROM attendance WHERE date = ?', (today,))
        attendance_today = cursor.fetchone()[0]

    total_teachers = 0
    locked_teachers = 0
    with sqlite3.connect('admin.db') as conn:
        ensure_admin_logins_schema(conn)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM teachers')
        total_teachers = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM logins WHERE COALESCE(is_locked, 0) = 1')
        locked_teachers = cursor.fetchone()[0]

    arrears_count = 0
    arrears_total = 0
    recent_payments_count = 0
    recent_payments_total = 0
    with sqlite3.connect('fees.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admission_number TEXT,
                amount_paid REAL,
                remaining_balance REAL,
                date_time TEXT
            )
        ''')
        cursor.execute('SELECT COUNT(*) FROM students WHERE remaining_balance > 0')
        arrears_count = cursor.fetchone()[0]
        cursor.execute('SELECT COALESCE(SUM(remaining_balance), 0) FROM students WHERE remaining_balance > 0')
        arrears_total = cursor.fetchone()[0]
        recent_cutoff = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute('SELECT COUNT(*), COALESCE(SUM(amount_paid), 0) FROM payment_history WHERE date_time >= ?', (recent_cutoff,))
        row = cursor.fetchone()
        recent_payments_count = row[0]
        recent_payments_total = row[1]

    return render_template(
        'manager_dashboard.html',
        profile_pic=profile_pic,
        total_students=total_students,
        total_teachers=total_teachers,
        arrears_count=arrears_count,
        arrears_total=arrears_total,
        non_compliant=non_compliant,
        ill_students=ill_students,
        locked_students=locked_students,
        locked_teachers=locked_teachers,
        attendance_today=attendance_today,
        recent_payments_count=recent_payments_count,
        recent_payments_total=recent_payments_total,
    )


@app.route('/manager_attendance_today_data')
def manager_attendance_today_data():
    username = session.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Not authenticated'})

    date = datetime.now().strftime('%Y-%m-%d')
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT a.admission_no, s.first_name, s.last_name, a.time_in, a.time_out, a.status
        FROM attendance a
        JOIN students s ON a.admission_no = s.admission_no
        WHERE a.date = ?
        ORDER BY a.time_in DESC
        LIMIT 10
        ''', (date,))
        records = cursor.fetchall()

    rows = [
        {
            'admission': record[0],
            'name': f"{record[1]} {record[2]}",
            'time_in': record[3],
            'time_out': record[4],
            'status': record[5],
        }
        for record in records
    ]

    return jsonify({'success': True, 'rows': rows})


@app.route('/manager_recent_payments_data')
def manager_recent_payments_data():
    username = session.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Not authenticated'})

    recent_cutoff = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    with sqlite3.connect('fees.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT admission_number, amount_paid, remaining_balance, date_time
        FROM payment_history
        WHERE date_time >= ?
        ORDER BY date_time DESC
        LIMIT 10
        ''', (recent_cutoff,))
        payment_rows = cursor.fetchall()

    name_lookup = {}
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        for row in payment_rows:
            admission_number = row[0]
            if admission_number in name_lookup:
                continue
            cursor.execute('''
            SELECT first_name, last_name
            FROM students
            WHERE admission_no = ?
            ''', (admission_number,))
            student = cursor.fetchone()
            if student:
                name_lookup[admission_number] = f"{student[0]} {student[1]}"
            else:
                name_lookup[admission_number] = 'Unknown'

    rows = [
        {
            'admission': row[0],
            'name': name_lookup.get(row[0], 'Unknown'),
            'amount': row[1],
            'remaining': row[2],
            'date_time': row[3],
        }
        for row in payment_rows
    ]

    return jsonify({'success': True, 'rows': rows})


@app.route('/manager_locked_students_data')
def manager_locked_students_data():
    username = session.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Not authenticated'})

    with sqlite3.connect('student.db') as conn:
        ensure_student_logins_schema(conn)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT s.admission_no, s.first_name, s.last_name, l.admission_no, COALESCE(l.is_locked, 0)
        FROM logins l
        JOIN students s ON l.admission_no = s.admission_no
        WHERE COALESCE(l.is_locked, 0) = 1
        ORDER BY s.last_name, s.first_name
        LIMIT 10
        ''')
        records = cursor.fetchall()

    rows = [
        {
            'admission': record[0],
            'name': f"{record[1]} {record[2]}",
            'username': record[3],
            'is_locked': record[4],
        }
        for record in records
    ]

    return jsonify({'success': True, 'rows': rows})


@app.route('/manager_locked_teachers_data')
def manager_locked_teachers_data():
    username = session.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Not authenticated'})

    with sqlite3.connect('admin.db') as conn:
        ensure_admin_logins_schema(conn)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT t.username, a.f_name, a.l_name, l.position, COALESCE(l.is_locked, 0)
        FROM logins l
        JOIN teachers t ON l.position = t.username
        JOIN admin_data a ON a.position = t.username
        WHERE COALESCE(l.is_locked, 0) = 1
        ORDER BY a.l_name, a.f_name
        LIMIT 10
        ''')
        records = cursor.fetchall()

    rows = [
        {
            'teacher_id': record[0],
            'name': f"{record[1]} {record[2]}",
            'username': record[3],
            'is_locked': record[4],
        }
        for record in records
    ]

    return jsonify({'success': True, 'rows': rows})


@app.route('/manager_toggle_student_lock', methods=['POST'])
def manager_toggle_student_lock():
    username = session.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Not authenticated'})

    data = request.get_json() or {}
    admission_no = data.get('admission_no', '').strip()
    lock_state = int(data.get('lock_state', 0))

    if not admission_no:
        return jsonify({'success': False, 'message': 'Admission number required'})

    with sqlite3.connect('student.db') as conn:
        ensure_student_logins_schema(conn)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM logins WHERE admission_no = ?", (admission_no,))
        if cursor.fetchone():
            cursor.execute("UPDATE logins SET is_locked = ? WHERE admission_no = ?", (lock_state, admission_no))
        else:
            cursor.execute("INSERT INTO logins (admission_no, password, is_locked) VALUES (?, ?, ?)",
                           (admission_no, "", lock_state))
        conn.commit()

    return jsonify({'success': True, 'lock_state': lock_state})


@app.route('/manager_toggle_teacher_lock', methods=['POST'])
def manager_toggle_teacher_lock():
    username = session.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Not authenticated'})

    data = request.get_json() or {}
    teacher_username = data.get('teacher_username', '').strip()
    lock_state = int(data.get('lock_state', 0))

    if not teacher_username:
        return jsonify({'success': False, 'message': 'Teacher username required'})

    with sqlite3.connect('admin.db') as conn:
        ensure_admin_logins_schema(conn)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM logins WHERE position = ?", (teacher_username,))
        if cursor.fetchone():
            cursor.execute("UPDATE logins SET is_locked = ? WHERE position = ?", (lock_state, teacher_username))
        else:
            cursor.execute("INSERT INTO logins (position, password, is_locked) VALUES (?, ?, ?)",
                           (teacher_username, "", lock_state))
        conn.commit()

    return jsonify({'success': True, 'lock_state': lock_state})


@app.route('/manager_payments_trend_data')
def manager_payments_trend_data():
    username = session.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Not authenticated'})

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=29)
    labels = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
    totals = {label: 0 for label in labels}

    with sqlite3.connect('fees.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admission_number TEXT,
                amount_paid REAL,
                remaining_balance REAL,
                date_time TEXT
            )
        ''')
        cursor.execute('''
        SELECT substr(date_time, 1, 10) AS day, COALESCE(SUM(amount_paid), 0)
        FROM payment_history
        WHERE day >= ?
        GROUP BY day
        ORDER BY day
        ''', (start_date.strftime('%Y-%m-%d'),))
        for day, total in cursor.fetchall():
            if day in totals:
                totals[day] = total

    data = [totals[label] for label in labels]
    return jsonify({'success': True, 'labels': labels, 'data': data})


@app.route('/manager_attendance_trend_data')
def manager_attendance_trend_data():
    username = session.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Not authenticated'})

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)
    labels = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    totals = {label: 0 for label in labels}

    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admission_no TEXT,
                date TEXT,
                time_in TEXT,
                status TEXT,
                marked_by TEXT,
                time_out TEXT,
                marked_out_by TEXT,
                FOREIGN KEY (admission_no) REFERENCES students (admission_no)
            )
        ''')
        cursor.execute('''
        SELECT date, COUNT(*)
        FROM attendance
        WHERE date >= ?
        GROUP BY date
        ORDER BY date
        ''', (start_date.strftime('%Y-%m-%d'),))
        for day, count in cursor.fetchall():
            if day in totals:
                totals[day] = count

    data = [totals[label] for label in labels]
    return jsonify({'success': True, 'labels': labels, 'data': data})


@app.route('/manager_student_lock_breakdown_data')
def manager_student_lock_breakdown_data():
    username = session.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Not authenticated'})

    locked_students = 0
    total_students = 0

    with sqlite3.connect('student.db') as conn:
        ensure_student_logins_schema(conn)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM students')
        total_students = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM logins WHERE COALESCE(is_locked, 0) = 1')
        locked_students = cursor.fetchone()[0]

    unlocked_students = max(0, total_students - locked_students)

    return jsonify({
        'success': True,
        'labels': ['Locked Students', 'Unlocked Students'],
        'data': [locked_students, unlocked_students]
    })


@app.route('/manager_teacher_lock_breakdown_data')
def manager_teacher_lock_breakdown_data():
    username = session.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Not authenticated'})

    locked_teachers = 0
    total_teachers = 0

    with sqlite3.connect('admin.db') as conn:
        ensure_admin_logins_schema(conn)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM teachers')
        total_teachers = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM logins WHERE COALESCE(is_locked, 0) = 1')
        locked_teachers = cursor.fetchone()[0]

    unlocked_teachers = max(0, total_teachers - locked_teachers)

    return jsonify({
        'success': True,
        'labels': ['Locked Teachers', 'Unlocked Teachers'],
        'data': [locked_teachers, unlocked_teachers]
    })

@app.route('/download/<filename>')
def download(filename):
    # Allow users to download the uploaded books
    return send_from_directory(app.config['BOOKS_FOLDER'], filename, as_attachment=True)


@app.route('/delete/<filename>', methods=['POST'])
def delete(filename):
    # Delete the PDF book and its front image
    book_path = os.path.join(app.config['BOOKS_FOLDER'], filename)
    image_name = os.path.splitext(filename)[0] + ".jpg"
    image_path = os.path.join(app.config['IMAGES_FOLDER'], image_name)

    if os.path.exists(book_path):
        os.remove(book_path)
    if os.path.exists(image_path):
        os.remove(image_path)

    return redirect(url_for('index'))


@app.route('/view_memo')
def view_memo():
    books = []
    for filename in os.listdir(app.config['BOOKS_FOLDER']):
        image_name = os.path.splitext(filename)[0] + ".jpg"  # Assuming images are uploaded as .jpg
        image_path = os.path.join(app.config['IMAGES_FOLDER'], image_name)
        books.append({
            "filename": filename,
            "image": image_name if os.path.exists(image_path) else None
        })
        admission_no = session.get('admission_no')
    return render_template("view_memo.html", books=books, profile_pic = database.get_profile(admission_no))



def load_user_data(username):
    if os.path.exists('user_data.json'):
        with open('user_data.json', 'r') as f:
            try:
                data = json.load(f)
                return data.get(username, {"username": username, "profile_picture": None})
            except json.JSONDecodeError:
                return {"username": username, "profile_picture": None}
    else:
        return {"username": username, "profile_picture": None}


# Save user data to a JSON file
def save_user_data(username, user_data):
    data = {}
    if os.path.exists('user_data.json'):
        with open('user_data.json', 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                pass
    data[username] = user_data
    with open('user_data.json', 'w') as f:
        json.dump(data, f)


# Route for user profile
@app.route('/manager_profile', methods=['POST'])
def manager_profile():
    username = session.get('username')
    image_file = request.files.get('profile_pic')
   # pp_compressor.compress_profile_image(image_file, f"{admission_no}.webp")

    if image_file:
        profile1.insert_image_m('manager.db', username, image_file)
        return redirect(url_for('msetting'))
    else:
        return "No image selected!", 400

@app.route('/profile', methods=['POST'])
def profile():
    admission_no = request.form.get('admission_no')
    image_file = request.files.get('profile_pic')
   # pp_compressor.compress_profile_image(image_file, f"{admission_no}.webp")

    if image_file:
        profile1.insert_image('student.db', admission_no, image_file)
        return redirect(url_for('settings'))
    else:
        return "No image selected!", 400

@app.route('/tprofile', methods=['POST','GET'])
def tprofile():
    username = request.form.get('username')
    image_file = request.files.get('profile_pic')


    if image_file:
        profile1.insert_image_t('admin.db', username, image_file)
        return redirect(url_for('tsetting'))
    else:
        return "No image selected!", 400


@app.route('/tsetting')
def tsetting():
    username = session.get('userName')
    profile_pic = database.get_profile_t(username)
    return render_template('tsetting.html',profile_pic=profile_pic, username = username)

@app.route('/msetting')
def msetting():
    username = session.get('username')
    profile_pic = database.get_aprofile(username)
    return render_template('manager_settings.html',profile_pic=profile_pic, username = username)

@app.route("/tphone_number_update", methods=['GET', 'POST'])
def tphone_number_update():
    phone = request.form['phone']
    username = session.get('userName')
    try:
        with sqlite3.connect('admin.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE teachers SET phone = ? WHERE username = ?
            ''', (phone, username))
            conn.commit()
    except sqlite3.Error as e:
        # Corrected indentation here
        print("Database error:", e)
    return redirect(url_for('tsetting'))


@app.route("/temail_update", methods=['GET', 'POST'])
def temail_update():
    email = request.form['email']
    username = session.get('userName')
    with sqlite3.connect('admin.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE teachers SET email = ? WHERE username = ?
                      ''',(email,username))
        conn.commit()
    return redirect(url_for('tsetting'))


@app.route('/compiler')
def compiler():
    return render_template('compiler.html')


@app.route('/manager')
def manager():
    return render_template('manager.html')


@app.route('/dash')
def dashb():
    admission_no = session.get('admission_no')
    # Get the profile picture from session or set a default one
    profile_picture = session.get('profile_picture', 'person1.png')
    username = request.args.get('username')
    user_data = load_user_data(username)
    admission=document_functions.replace_slash_with_dot(admission_no)
    if request.method == 'POST':
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture.filename != '':
                profile_pic_path = f'static/uploads/{username}_profile_picture.jpg'
                profile_picture.save(profile_pic_path)
                user_data['profile_picture'] = profile_pic_path
                save_user_data(username, user_data)

    return render_template('dashboard.html', profile_picture=user_data['profile_picture'],admission_no=admission)


@app.route('/student_dashboard')
def student_dashboard():
    admission_no = session.get('admission_no')
    admission=document_functions.replace_slash_with_dot(admission_no)
    profile_pic = database.get_profile(admission_no)
    return render_template('student_dashboard.html', profile_pic=profile_pic,admission_no=admission)


@app.route('/students_with_balance')
def students_with_balance():
    students = database.get_students_with_balance()
    return render_template('students_with_balance.html', students=students)


#===============Add Student
@app.route('/add_or_remove')
def add_or_remove_student():
    username = session.get('username')
    username = document_functions.replace_slash_with_dot(username)
    profile_pic = database.get_aprofile(username)
    return render_template("add_or_remove_student.html", profile_pic=profile_pic)

@app.route('/add_remove_teacher')
def a_or_r():
    username = session.get('username')
    username = document_functions.replace_slash_with_dot(username)
    profile_pic = database.get_aprofile(username)
    return render_template("add_or_remove_teacher.html",profile_pic=profile_pic)

@app.route('/add_student')
def add():
    username = session.get('username')
    username = document_functions.replace_slash_with_dot(username)
    profile_pic = database.get_aprofile(username)
    return render_template('add_student.html',profile_pic=profile_pic)


@app.route('/signup_success')
def signup_success():
    return render_template('signup_success.html')


@app.route('/submit_signup', methods=['POST'])
def submit_signup():
    first_name = request.form['first_name'].upper()
    middle_name = request.form['middle_name'].upper()
    last_name = request.form['last_name'].upper()
    age = request.form['age']
    gender = request.form['gender']
    grade = request.form['grade']
    sickness = request.form['sickness'].capitalize()
    treatment = request.form['treatment'].capitalize()
    admission_no = request.form['admission_no']
    phone = request.form['phone']
    email = request.form['email']
    existing_student = database.student_exist(admission_no)
    existing_email = database.student_email_exists(admission_no)
    if existing_student:
        # Admission number already exists
        flash("Error: A student with this admission number already exists.", "error")
        return redirect(url_for('index'))
    if existing_email:
        flash("Student with the same email exists try to login")
        return redirect(url_for('index'))

    database.add_someone(admission_no, first_name, middle_name, last_name, gender, age, email)
    database.add_level(admission_no, grade,phone,datetime.now())
    database.put_ill_students(admission_no, sickness, treatment)
    database.add_login(admission_no, last_name)
    sender_email = "richardkeith233@gmail.com"
    sender_password = "mnoj wsox aumw tkrs"  # Use App Password if 2FA is enabled
    recipient_email = email
    password2 = last_name

    subject = "Crimsons Schools"
    body = f"Welcome and feel at home your last name will be your default password: {password2}, Your admission number: {admission_no}"

    send_mail1.send_email(sender_email,recipient_email, sender_password, password2, subject, body)
    return redirect(url_for('signup_success'))

#=================Send mail



#=================Non Compliant Student
@app.route('/non_compliant_students')
def non_compliant_students():
    username = session.get('username')
    username = document_functions.replace_slash_with_dot(username)
    profile_pic = database.get_aprofile(username)
    students = database.non_compliant_students()
    return render_template('non_compliant_students.html', students=students, profile_pic=profile_pic)


#===============Ill Students
@app.route('/health_issue')
def health_issue():
    username = session.get('username')
    username = document_functions.replace_slash_with_dot(username)
    profile_pic = database.get_aprofile(username)
    students = database.get_ill_students()
    return render_template('health_issue.html', students=students, profile_pic=profile_pic)
#================Add Health issue Student==========
#================Remove Health issue Student=============
#================View all registered students=============
def all_students():
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT students.admission_no, students.first_name, students.last_name, rest.phone_number, rest.Grade
        FROM students
        JOIN rest ON students.admission_no = rest.admission_no
        ORDER BY rest.Grade ASC
        ''')
        result = cursor.fetchall()
        return result

@app.route('/all_teacher',  methods=['GET','POST'])
def all_teacher():
    with sqlite3.connect('admin.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT admin_data.position, admin_data.f_name, admin_data.l_name, teachers.grade, teachers.subject
        FROM admin_data
        JOIN teachers ON admin_data.position = teachers.username
        ORDER BY admin_data.position ASC
        ''')
        result = cursor.fetchall()
        return result


@app.route("/phone_number_update", methods=['GET', 'POST'])
def phone_number_update():
    phone = request.form['phone']
    admission_no = session.get('admission_no')
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE rest SET phone_number = ? WHERE admission_no = ?
                       ''',(phone,admission_no))
        conn.commit()
    return redirect(url_for('settings'))

@app.route("/email_update", methods=['GET', 'POST'])
def email_update():
    email = request.form['email']
    admission_no = session.get('admission_no')
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE students SET email = ? WHERE admission_no = ?
                       ''',(email,admission_no))
        conn.commit()
    return redirect(url_for('settings'))

@app.route('/registered_students')
def registered():
    username = session.get('username')
    username = document_functions.replace_slash_with_dot(username)
    profile_pic = database.get_aprofile(username)
    students = all_students()
    return render_template('registered_students.html',students=students, profile_pic=profile_pic)

@app.route('/registered_teachers')
def registered1():
    username = session.get('username')
    username = document_functions.replace_slash_with_dot(username)
    profile_pic = database.get_aprofile(username)
    teachers = all_teacher()
    return render_template('registered_teachers.html',teachers = teachers, profile_pic=profile_pic)



#======================Fee Payment==============================================



def get_student_data(admission_number):
    conn = sqlite3.connect('fees.db')
    cursor = conn.cursor()
    cursor.execute('SELECT total_paid, remaining_balance FROM students WHERE admission_number = ?', (admission_number,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (0, TOTAL_FEES)





# Function to get student data by either admission number or name
def get_student_by_admission_or_name(identifier):
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()

    # Check if identifier is a valid admission number or name
    cursor.execute('''
        SELECT admission_no FROM students
        WHERE admission_no = ? OR (first_name || ' ' || last_name) = ?
    ''', (identifier, identifier))

    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]  # Return admission number
    else:

        return None


# Updated function to handle name or admission number and fee update
def update_student_fees(identifier, amount_paid):
    # Check if the identifier is an admission number or full name
    admission_number = get_student_by_admission_or_name(identifier)

    if admission_number is None:
        return "Student not found"

    conn = sqlite3.connect('fees.db')
    cursor = conn.cursor()

    # Get the previous total paid and remaining balance
    previous_total_paid, _ = get_student_data(admission_number)
    total_paid = previous_total_paid + amount_paid
    remaining_balance = document_functions.current_fee() - total_paid

    # Update the students' fee data
    cursor.execute('''
        INSERT INTO students (admission_number, total_paid, remaining_balance)
        VALUES (?, ?, ?)
        ON CONFLICT(admission_number)
        DO UPDATE SET total_paid = excluded.total_paid, remaining_balance = excluded.remaining_balance
    ''', (admission_number, total_paid, remaining_balance))

    # Record the transaction in the payment_histo
    import pytz
    nairobi_tz = pytz.timezone('Africa/Nairobi')
    nairobi_time = datetime.now(nairobi_tz)
    date_time = nairobi_time.strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
        INSERT INTO payment_history (admission_number, amount_paid, remaining_balance, date_time)
        VALUES (?, ?, ?, ?)
    ''', (admission_number, amount_paid, remaining_balance, date_time))

    conn.commit()
    conn.close()

    return total_paid, remaining_balance



def get_payment_history(admission_number):
    conn = sqlite3.connect('fees.db')
    cursor = conn.cursor()
    cursor.execute('SELECT amount_paid, remaining_balance, date_time FROM payment_history WHERE admission_number = ?', (admission_number,))
    history = cursor.fetchall()
    conn.close()
    return history

@app.route('/fee_payment', methods=['GET','POST'])
def index1():
    # admission_no = get_student_by_admission_or_name(request.form['admissionNumber'])
    # admission_no = document_functions.replace_slash_with_dot(admission_no)
    return render_template('fees_payment.html' )

@app.route('/submit', methods=['POST'])
def submit():
    admission_number = request.form['admissionNumber']
    fee_paid = float(request.form['feePaid'])

    total_paid, remaining_balance = update_student_fees(admission_number, fee_paid)

    return jsonify({
        'total_paid': total_paid,
        'remaining_balance': remaining_balance
    })

@app.route('/receipt/<admission_no>', methods=['GET'])
def download_receipt(admission_no):
    admission_number = document_functions.replace_slash_with_slash(admission_no)
    total_paid, remaining_balance = get_student_data(admission_number)

    # Generate PDF receipt
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)

    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']

    # Receipt content
    elements = []

    # Title
    title = Paragraph(
        f"Payment Receipt for Admission Number: {document_functions.replace_slash_with_slash(admission_number)}",
        title_style)
    elements.append(title)

    # Spacer
    elements.append(Paragraph("<br/><br/>", normal_style))

    # Receipt table data
    data = [
        ["Description", "Amount (sh)"],
        ["Total Paid", f"{total_paid}"],
        ["Remaining Balance", f"{remaining_balance}"]
    ]

    # Create a table with a custom style
    table = Table(data, colWidths=[3 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Spacer
    elements.append(Paragraph("<br/><br/>", normal_style))

    # Thank you message
    thank_you = Paragraph("Thank you for your payment.", normal_style)
    elements.append(thank_you)

    # Build PDF
    pdf.build(elements)

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"receipt_{admission_number}.pdf",
                     mimetype='application/pdf')

@app.route('/history', methods=['GET'])
def view_history():
    admission_number = session.get('admission_no')
    admission_number = document_functions.replace_slash_with_slash(admission_number)
    history = get_payment_history(admission_number)
    return render_template('payment_history.html', history=history, admission_number=document_functions.replace_slash_with_dot(admission_number), profile_pic=database.get_profile(admission_number))

@app.route('/download_history', methods=['GET'])
def download_history():
    admission_number = session.get('admission_no')

    # Fetch payment history
    history = get_payment_history(document_functions.replace_slash_with_slash(admission_number))

    # Create buffer
    buffer = io.BytesIO()

    # Create a PDF document using SimpleDocTemplate
    pdf = SimpleDocTemplate(buffer, pagesize=A4)

    # Container for the elements in the PDF
    elements = []

    # Add a title
    styles = getSampleStyleSheet()
    title = Paragraph(f"Payment History for : {database.get_first_name( admission_number)} {database.get_middle_name(admission_number)} {database.get_last_name(admission_number)}", styles['Title'])
    elements.append(title)

    # Table data (headers)
    data = [['Amount Paid', 'Remaining Balance', 'Date & Time']]

    # Table data (rows)
    for amount_paid, remaining_balance, date_time in history:
        data.append([f"sh.{amount_paid}", f"sh.{remaining_balance}", date_time])

    # Create a table
    table = Table(data)

    # Apply table style
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Add table to elements
    elements.append(table)

    # Build the PDF
    pdf.build(elements)

    # Return PDF file
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"payment_history_{admission_number}.pdf",
                     mimetype='application/pdf')


#=====================Delete Student
def get_db_connection():
    conn = sqlite3.connect('student.db')
    conn.row_factory = sqlite3.Row
    return conn

# Route to render the HTML page


# API to fetch all students from the database
@app.route('/all_students', methods=['GET','POST'])
def get_students():
    conn = get_db_connection()
    students = conn.execute('''
    SELECT students.admission_no, students.first_name, students.last_name, rest.Grade
    FROM students
    JOIN rest ON students.admission_no = rest.admission_no
    ''').fetchall()
    conn.close()

    student_list = [{'admission_no': document_functions.replace_slash_with_dot(student['admission_no']), 'first_name': student['first_name'], 'last_name':student['last_name'],'grade':student['Grade']} for student in students]
    return jsonify(student_list)

@app.route('/all_teachers',  methods=['GET','POST'])
def all_teachers():
    with sqlite3.connect('admin.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT admin_data.position, admin_data.f_name, admin_data.l_name, teachers.grade, teachers.subject
        FROM admin_data
        JOIN teachers ON admin_data.position = teachers.username
        ORDER BY admin_data.position ASC
        ''')
        result = cursor.fetchall()

    # Convert result to a list of dictionaries
    teachers_list = [
        {
            "username": row[0],
            "f_name": row[1],
            "l_name": row[2],
            "grade": row[3],
            "subject": row[4]
        }
        for row in result
    ]

    return jsonify(teachers_list)  # Ensure the response is JSON-formatted


# API to delete a student by ID
@app.route('/delete_student/<admission_no>', methods=['DELETE','POST'])
def delete_student(admission_no):
    admission = document_functions.replace_slash_with_slash(admission_no)
    database.delete_student(admission)
    return jsonify({'success': True})

@app.route('/delete_teacher/<username>', methods=['DELETE','POST'])
def delete_teacher(username):
    database.delete_teacher(username)
    return jsonify({'success': True})
#===============Change Password
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    admission_number = session.get('admission_no')
    if request.method == 'POST':
        # Get form data
        admission_no = session.get('admission_no')  # Example admission number, ideally you'd get this from session or another source
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Connect to the database
        conn = sqlite3.connect('student.db')
        cursor = conn.cursor()

        # Check if current password is correct
        cursor.execute("SELECT password FROM logins WHERE admission_no = ?", (admission_no,))
        result = cursor.fetchone()

        if result and result[0] == current_password:
            # Check if the new password and confirmation match
            if new_password == confirm_password:
                # Update the password in the logins table
                cursor.execute("UPDATE logins SET password = ? WHERE admission_no = ?", (new_password, admission_no))
                conn.commit()
                flash('Password changed successfully!', 'success')
                return redirect(url_for('home'))
            else:
                flash('New password and confirmation do not match.', 'error')
        else:
            flash('Current password is incorrect.', 'error')

        conn.close()
    return render_template('change_password.html',profile_pic = database.get_profile(admission_number))

@app.route('/change_manager_password', methods=['GET', 'POST'])
def manager_password():
    username = session.get('username')
    username = document_functions.replace_slash_with_dot(username)
    profile_pic = database.get_aprofile(username)
    if request.method == 'POST':
        # Get form data
        admission_no = session.get('username')  # Example admission number, ideally you'd get this from session or another source
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Connect to the database
        conn = sqlite3.connect('manager.db')
        cursor = conn.cursor()

        # Check if current password is correct
        cursor.execute("SELECT password FROM logins WHERE username = ?", (admission_no,))
        result = cursor.fetchone()

        if result and result[0] == current_password:
            # Check if the new password and confirmation match
            if new_password == confirm_password:
                # Update the password in the logins table
                cursor.execute("UPDATE logins SET password = ? WHERE username = ?", (new_password, admission_no))
                conn.commit()
                flash('Password changed successfully!', 'success')
                print('password changed successfully')
                return redirect('/add_or_remove')
            else:
                flash('New password and confirmation do not match.', 'error')
                print('passwords dont match')
        else:
            flash('Current password is incorrect.', 'error')
            print('current password is incorrect')

        conn.close()
    return render_template('manager_password.html', profile_pic=profile_pic)

#==================Developer portal
UPLOAD_FOLDER = 'static/images'
FIXED_FILENAME = 'your_uploaded_image.jpg'

# Configure upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/developer')
def developer():
    return render_template('developer.html')

@app.route('/upload_image', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return "No file part"

    file = request.files['image']

    if file.filename == '':
        return "No selected file"

    if file:
        # Use the fixed filename for the uploaded image
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], FIXED_FILENAME)
        file.save(file_path)
        return f'Image successfully uploaded and saved as {FIXED_FILENAME}'
#===============================Exam Results
def view_student_marks():
    admission_no = session.get('admission_no')
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM marks
        WHERE admission_no = ?
        ''',(admission_no,))
        result = cursor.fetchall()
    return result

def view_student_marks2(admission_no, enrolled_subjects=None):
    """Get student marks with unpacked subjects for template rendering, filtered to enrolled subjects only."""
    if enrolled_subjects is None:
        enrolled_subjects = []
    
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT id, admission_no, year, term, exam_type, marks_json, average
        FROM marks
        WHERE admission_no = ?
        ORDER BY year DESC, term DESC
        ''',(admission_no,))
        rows = cursor.fetchall()
    
    result = []
    for row in rows:
        row_id, adm, year, term, exam_type, marks_json, avg = row
        try:
            marks = json.loads(marks_json) if marks_json else {}
        except (json.JSONDecodeError, ValueError):
            marks = {}
        
        # Build tuple with only enrolled subjects (dynamic length based on actual enrollment)
        subject_marks = tuple(marks.get(subj, '-') for subj in enrolled_subjects)
        avg_val = avg if avg is not None else '-'
        
        # Format: (id, year, term, exam_type, ...enrolled_subject_marks, avg)
        # Subjects are in the order from enrolled_subjects list
        result.append((row_id, year, term, exam_type) + subject_marks + (avg_val,))
    
    return result

#===========================================Change Student Logins
@app.route('/students_logins', methods=['GET', 'POST'])
def show_students():
    username =session.get('username')
    profile_pic = database.get_aprofile(username)
    conn = sqlite3.connect('student.db')
    ensure_student_logins_schema(conn)
    cursor = conn.cursor()

    email, name, last_name = None, None, None  # Default values

    # Check if it's a POST request to update a password
    if request.method == 'POST':
        action = request.form.get('action', 'update_password')
        admission_number = request.form['admission_number']

        if action == 'toggle_lock':
            new_state = int(request.form.get('lock_state', '0'))
            cursor.execute("SELECT 1 FROM logins WHERE admission_no = ?", (admission_number,))
            if cursor.fetchone():
                cursor.execute("UPDATE logins SET is_locked = ? WHERE admission_no = ?", (new_state, admission_number))
                sender_email = "richardkeith233@gmail.com"
                sender_password = "mnoj wsox aumw tkrs"  # Use an App Password if 2FA is enabled
                recipient_email = database.get_email(admission_number)

                subject = "Crimsons Student Portal"
                body = f"Hello {database.get_last_name(admission_number)},\n\nWe regret to inform you that your account has been locked by the Administration panel. Please confirm with the administration."

                send_mail1.send_email(sender_email, recipient_email, sender_password, last_name, subject, body)

            else:
                cursor.execute("INSERT INTO logins (admission_no, password, is_locked) VALUES (?, ?, ?)",
                               (admission_number, "", new_state))
            conn.commit()
        else:
            new_password = request.form['new_password']

            # Update the password in the logins table; insert if missing
            cursor.execute("SELECT 1 FROM logins WHERE admission_no = ?", (admission_number,))
            if cursor.fetchone():
                cursor.execute("UPDATE logins SET password = ? WHERE admission_no = ?", (new_password, admission_number))
            else:
                cursor.execute("INSERT INTO logins (admission_no, password, is_locked) VALUES (?, ?, 0)",
                               (admission_number, new_password))
            conn.commit()

            # Fetch the email, first name, and last name for the given admission number
            cursor.execute("SELECT email, first_name, last_name FROM students WHERE admission_no = ?", (admission_number,))
            result = cursor.fetchone()

            if result:
                email, name, last_name = result  # Unpacking the tuple

                # Send email notification about password change
                sender_email = "richardkeith233@gmail.com"
                sender_password = "mnoj wsox aumw tkrs"  # Use an App Password if 2FA is enabled
                recipient_email = email

                subject = "Crimsons Student Portal"
                body = f"Hello {name},\n\nYour new Password is: {new_password}. Please feel free to change it after logging in.\n\nBest regards,\nCrimsons Schools Portal"

                send_mail1.send_email(sender_email, recipient_email, sender_password, last_name, subject, body)

                
    # Server-side search + pagination support
    q = request.args.get('q', '')
    # pagination params
    try:
        page = int(request.args.get('page', 1))
    except (TypeError, ValueError):
        page = 1
    if page < 1:
        page = 1
    per_page = 20
    offset = (page - 1) * per_page

    if q:
        like_q = f"%{q}%"
        # total count for matched rows
        cursor.execute('''
            SELECT COUNT(*)
            FROM students
            LEFT JOIN logins ON students.admission_no = logins.admission_no
            WHERE students.admission_no LIKE ? OR students.first_name LIKE ? OR students.last_name LIKE ?
        ''', (like_q, like_q, like_q))
        total = cursor.fetchone()[0]

        # fetch paginated matched rows
        cursor.execute('''
            SELECT students.admission_no, students.first_name, students.last_name, logins.password, COALESCE(logins.is_locked, 0)
            FROM students
            LEFT JOIN logins ON students.admission_no = logins.admission_no
            WHERE students.admission_no LIKE ? OR students.first_name LIKE ? OR students.last_name LIKE ?
            ORDER BY students.rowid DESC
            LIMIT ? OFFSET ?
        ''', (like_q, like_q, like_q, per_page, offset))
    else:
        # total count for all rows
        cursor.execute('''
            SELECT COUNT(*)
            FROM students
            LEFT JOIN logins ON students.admission_no = logins.admission_no
        ''')
        total = cursor.fetchone()[0]

        # fetch paginated rows
        cursor.execute('''
            SELECT students.admission_no, students.first_name, students.last_name, logins.password, COALESCE(logins.is_locked, 0)
            FROM students
            LEFT JOIN logins ON students.admission_no = logins.admission_no
            ORDER BY students.rowid DESC
            LIMIT ? OFFSET ?
        ''', (per_page, offset))

    students = cursor.fetchall()
    # normalize missing passwords to empty string for display
    students = [(s[0], s[1], s[2], s[3] if s[3] is not None else '', s[4] if s[4] is not None else 0) for s in students]
    conn.close()

    # compute pagination metadata
    total_pages = max(1, (total + per_page - 1) // per_page)

    # Pass back the query and pagination info so the template can render controls
    return render_template('students_logins.html',  students=students, q=q, page=page, total_pages=total_pages,profile_pic=profile_pic)

@app.route('/teachers_logins', methods=['GET', 'POST'])
def show_teachers():
    username = session.get('username')
    profile_pic = database.get_aprofile(username)
    conn = sqlite3.connect('admin.db')
    ensure_admin_logins_schema(conn)
    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action', 'update_password')
        teacher_username = request.form['teacher_username']

        if action == 'toggle_lock':
            new_state = int(request.form.get('lock_state', '0'))
            cursor.execute("SELECT 1 FROM logins WHERE position = ?", (teacher_username,))
            if cursor.fetchone():
                cursor.execute("UPDATE logins SET is_locked = ? WHERE position = ?", (new_state, teacher_username))
            else:
                cursor.execute("INSERT INTO logins (position, password, is_locked) VALUES (?, ?, ?)",
                               (teacher_username, "", new_state))
            conn.commit()
        else:
            new_password = request.form['new_password']
            cursor.execute("SELECT 1 FROM logins WHERE position = ?", (teacher_username,))
            if cursor.fetchone():
                cursor.execute("UPDATE logins SET password = ? WHERE position = ?", (new_password, teacher_username))
            else:
                cursor.execute("INSERT INTO logins (position, password, is_locked) VALUES (?, ?, 0)",
                               (teacher_username, new_password))
            conn.commit()

    q = request.args.get('q', '')
    try:
        page = int(request.args.get('page', 1))
    except (TypeError, ValueError):
        page = 1
    if page < 1:
        page = 1
    per_page = 20
    offset = (page - 1) * per_page

    if q:
        like_q = f"%{q}%"
        cursor.execute('''
            SELECT COUNT(*)
            FROM teachers
            JOIN admin_data ON admin_data.position = teachers.username
            LEFT JOIN logins ON logins.position = teachers.username
            WHERE teachers.username LIKE ? OR admin_data.f_name LIKE ? OR admin_data.l_name LIKE ? OR teachers.email LIKE ?
        ''', (like_q, like_q, like_q, like_q))
        total = cursor.fetchone()[0]

        cursor.execute('''
            SELECT teachers.username, admin_data.f_name, admin_data.l_name, logins.password, COALESCE(logins.is_locked, 0)
            FROM teachers
            JOIN admin_data ON admin_data.position = teachers.username
            LEFT JOIN logins ON logins.position = teachers.username
            WHERE teachers.username LIKE ? OR admin_data.f_name LIKE ? OR admin_data.l_name LIKE ? OR teachers.email LIKE ?
            ORDER BY teachers.rowid DESC
            LIMIT ? OFFSET ?
        ''', (like_q, like_q, like_q, like_q, per_page, offset))
    else:
        cursor.execute('''
            SELECT COUNT(*)
            FROM teachers
            JOIN admin_data ON admin_data.position = teachers.username
            LEFT JOIN logins ON logins.position = teachers.username
        ''')
        total = cursor.fetchone()[0]

        cursor.execute('''
            SELECT teachers.username, admin_data.f_name, admin_data.l_name, logins.password, COALESCE(logins.is_locked, 0)
            FROM teachers
            JOIN admin_data ON admin_data.position = teachers.username
            LEFT JOIN logins ON logins.position = teachers.username
            ORDER BY teachers.rowid DESC
            LIMIT ? OFFSET ?
        ''', (per_page, offset))

    teachers = cursor.fetchall()
    teachers = [(t[0], t[1], t[2], t[3] if t[3] is not None else '', t[4] if t[4] is not None else 0) for t in teachers]
    conn.close()

    total_pages = max(1, (total + per_page - 1) // per_page)
    return render_template('teachers_logins.html', teachers=teachers, q=q, page=page, total_pages=total_pages, profile_pic=profile_pic)
#=====================Update fee balances for each student
# Route to display the HTML form
@app.route('/fee_update_success')
def f_success():
    username = session.get('username')
    username = document_functions.replace_slash_with_dot(username)
    profile_pic = database.get_aprofile(username)
    return render_template('update_fee_success.html', profile_pic=profile_pic)
@app.route('/set_fee', methods=['GET', 'POST'])
def set_fee():
    username = session.get('username')
    username = document_functions.replace_slash_with_dot(username)
    profile_pic = database.get_aprofile(username)
    if request.method == 'POST':
        # Get fee values from form submission
        term1_fee = request.form['term1']
        term2_fee = request.form['term2']
        term3_fee = request.form['term3']

        # Update the database with new fees
        conn = sqlite3.connect('fees.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE fee SET amount = ? WHERE term = ?', (term1_fee, 1))
        cursor.execute('UPDATE fee SET amount = ? WHERE term = ?', (term2_fee, 2))
        cursor.execute('UPDATE fee SET amount = ? WHERE term = ?', (term3_fee, 3))

        # Commit changes and close the connection
        conn.commit()
        conn.close()

        with sqlite3.connect('fees.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT amount FROM fee
            ''')
            data = cursor.fetchall()
        with sqlite3.connect('fees.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT term FROM fee
            ''')
            terms = cursor.fetchall()
            #===Determine the current time
            current_month = datetime.now().month

            # Determine the fee based on the month
            if current_month in [1, 2, 3, 4]:
                current_fee = data[0][0]
                term = terms[0][0]
            elif current_month in [5, 6, 7, 8]:
                current_fee = data[1][0]
                term = terms[1][0]
            elif current_month in [9, 10, 11, 12]:
                current_fee = data[2][0]
                term = terms[2][0]
            else:
                raise ValueError("Invalid month encountered.")

            # Connect to the SQLite database
            with sqlite3.connect('fees.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE current_fees SET term = ? , amount = ?
                ''', (term, current_fee))
                print('Data set sucessfuly')
                conn.commit()

        return redirect(url_for('f_success'))

    # Render the HTML form on GET request
    students = database.fee_data()

    return render_template('set_fee.html',students=students, profile_pic=profile_pic)

# Update student balances based on the current term
@app.route('/update_balances',  methods=['GET', 'POST'])
def update_balances():
    username = session.get('username')
    username = document_functions.replace_slash_with_dot(username)
    profile_pic = database.get_aprofile(username)
    if request.method == 'POST':
        fee_amount = request.form['fee_amount']
        with sqlite3.connect('fees.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT amount FROM fee
            ''')
            data = cursor.fetchall()
        with sqlite3.connect('fees.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT term FROM fee
            ''')
            terms = cursor.fetchall()
            #===Determine the current time
            current_month = datetime.now().month

            # Determine the fee based on the month
            if current_month in [1, 2, 3, 4]:
                current_fee = data[0][0]
                term = terms[0][0]
            elif current_month in [5, 6, 7, 8]:
                current_fee = data[1][0]
                term = terms[1][0]
            elif current_month in [9, 10, 11, 12]:
                current_fee = data[2][0]
                term = terms[2][0]
            else:
                raise ValueError("Invalid month encountered.")

            # Connect to the SQLite database
            with sqlite3.connect('fees.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE current_fees SET term = ? , amount = ?
                ''', (term, current_fee))
                print('Data set sucessfuly')
                conn.commit()


        with sqlite3.connect('fees.db') as conn:
            cursor = conn.cursor()

            # Get the fee for the current term
            cursor.execute('SELECT amount FROM current_fees')
            fees = cursor.fetchone()

            if not fees:
                return jsonify({'message': 'No fee set for this term'}), 400

            fee_amount = fees[0]

            # Update each student's balance
            cursor.execute('UPDATE students SET remaining_balance = remaining_balance + ?', (fee_amount,))

            conn.commit()

        return redirect(url_for('f_success'))
    return render_template('update_balances.html',fee_amount=document_functions.c_fee(), profile_pic=profile_pic)

@app.route('/add-student', methods=['POST'])
def add_student():
    username = session.get('username')
    username = document_functions.replace_slash_with_dot(username)
    profile_pic = database.get_aprofile(username)
    first_name = request.form['first_name'].upper()
    last_name = request.form['last_name'].upper()
    admission_no = database.get_admission_number(first_name, last_name)
    sickness = request.form['sickness']
    treatment = request.form['treatment']

    # Add to the database
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ill_students (admission_no,  sick, description)
            VALUES (?, ?, ?)
        """, (admission_no, sickness, treatment))
        conn.commit()

    return redirect('/health_issue',profile_pic=profile_pic)

@app.route('/delete-student/<admission_no>', methods=['POST'])
def delete_ill_student(admission_no):
    username = session.get('username')
    username = document_functions.replace_slash_with_dot(username)
    profile_pic = database.get_aprofile(username)
    admission_number =document_functions.replace_slash_with_slash(admission_no)
    # Remove the student from the database
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ill_students WHERE admission_no = ?", (admission_number,))
        conn.commit()

    return redirect('/health_issue', profile_pic=profile_pic)
@app.route('/add-student3', methods=['POST'])
def add_student_ncs():
    username = session.get('username')
    username = document_functions.replace_slash_with_dot(username)
    profile_pic = database.get_aprofile(username)
    admission_no = request.form['admission_no']
    reason = request.form['reason'].capitalize()
    duration = request.form['duration']
    send_date = request.form['send_date']
    return_date = request.form['return_date']
    status = 'pending'

    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO non_compliant (admission_no, send_date, return_date, status, duration, reason, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (admission_no,  send_date, return_date, status, duration, reason, status))
        conn.commit()

    return redirect('/non_compliant_students', profile_pic=profile_pic)

@app.route('/delete-student1/<admission_no>', methods=['POST'])
def delete_student_ncs(admission_no):
    username = session.get('username')
    username = document_functions.replace_slash_with_dot(username)
    profile_pic = database.get_aprofile(username)
    with sqlite3.connect('student.db') as conn:
        admission_number=document_functions.replace_slash_with_slash(admission_no)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM non_compliant WHERE admission_no = ?", (admission_number,))
        conn.commit()

    return redirect('/non_compliant_students', profile_pic=profile_pic)


from flask import redirect, url_for, request, session
import sqlite3

@app.route('/update-status/<admission_no>', methods=['POST'])
def update_status(admission_no):
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    username = document_functions.replace_slash_with_dot(username)
    admission_number = document_functions.replace_slash_with_slash(admission_no)

    new_status = request.form.get('status')
    if not new_status:
        return redirect(url_for('non_compliant_students'))

    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE non_compliant SET status = ? WHERE admission_no = ?",
            (new_status, admission_number)
        )
        conn.commit()

    return redirect(url_for('non_compliant_students'))

@app.route('/update-student', methods=['POST'])
def update_student():
    data = request.get_json()

    admission_no = data.get('admission_no')
    last_name = data.get('last_name')
    student_class = data.get('send_date')

    duration = data.get('duration')
    reason = data.get('status')
    status = data.get('status')

    if not all([admission_no, name, student_class, status]):
        return jsonify({'success': False, 'error': 'All fields are required'}), 400

    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE non_compliant
            SET first_name = ?, last_name = ?, send_date = ?, duration = ?, reason = ?, status = ?
            WHERE admission_no = ?
        """, (send_date, duration, reason, status, admission_no))
        conn.commit()

    return jsonify({'success': True})



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to get access token
def get_access_token():
    consumer_key = "twd2Fk9toBVjeGi67JCCfEqh0uB7OJPXNiA63g44ek3dpskP"
    consumer_secret = "9lXIcf6er5THdG7DAZWpv8sGeiXyEziH13RuTmuFVGAWhAJxB6LqPWMHUbrWFnx2"
    endpoint = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(endpoint, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        logger.error(f"Error generating token: {response.text}")
        return None

@app.route('/pay_myfees')
def my_fee_payment():
    admission_no = session.get('admission_no')
    return render_template('pay_fees.html', profile_pic=database.get_profile(admission_no))

# M-Pesa API Credentials
CONSUMER_KEY = "twd2Fk9toBVjeGi67JCCfEqh0uB7OJPXNiA63g44ek3dpskP"
CONSUMER_SECRET = "9lXIcf6er5THdG7DAZWpv8sGeiXyEziH13RuTmuFVGAWhAJxB6LqPWMHUbrWFnx2"
BUSINESS_SHORT_CODE = "174379"
PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
CALLBACK_URL = "https://crimsons.pythonanywhere.com/mpesa_callback"


@app.route("/pay_fees", methods=['GET', 'POST'])
def stk_push():
    phone = request.form["phone"]
    if phone.startswith("0"):
        phone = "254" + phone[1:]  # Convert 0712345678 to 254712345678
    amount = request.form["amount"]
    access_token = get_access_token()
    print("Access Token:", access_token)

    if not access_token:
        return jsonify({"error": "Failed to get access token"})

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode((BUSINESS_SHORT_CODE + PASSKEY + timestamp).encode()).decode()

    stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    payload = {
        "BusinessShortCode": BUSINESS_SHORT_CODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": BUSINESS_SHORT_CODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "account_reference",
        "TransactionDesc": "Fees payment"
    }

    response = requests.post(stk_url, json=payload, headers=headers)
    print("STK Push Response:", response.json())  # Debugging
    if response.status_code == 200:
        return jsonify({"status": "success", "message": "Payment in progress"})
    else:
        return jsonify({"status": "failure", "message": response.text}), response.status_code
    return jsonify(response.json())


# Callback listener to handle the result from Safaricom

@app.route("/mpesa_callback", methods=["POST","GET"])
def mpesa_callback():
    print("Hello  callback!!1")
    data = request.get_json()
    print("Hello  callback!!")
    if data and "Body" in data and "stkCallback" in data["Body"]:
        callback = data["Body"]["stkCallback"]
        result_code = callback["ResultCode"]
        transaction_id = callback.get("CheckoutRequestID", None)

        # Determine payment status
        status = "Fail" if result_code != 0 else "Success"


        print(f'payment is a {status}')

        # if "CallbackMetadata" in callback:
        #     for item in callback["CallbackMetadata"]["Item"]:
        #         if item["Name"] == "PhoneNumber":
        #             phone_number = item["Value"]
        #         if item["Name"] == "Amount":  # Extracting Amount
        #             amount = item["Value"]
        #         admission_no = session.get('admission_no')
        # print(f'{phone_number} paid {amount} of adimission_no {admission_no}')
        return redirect('/trainer')

    return jsonify({"error": "Invalid callback data"}), 400
#import pywhatkit

@app.route('/send_message', methods=['GET','POST'])
def whatsapp():
    try:

        phone = "+254110385662"
        message = "Hello, I hope this message finds you well. I have a query. Please assist me."

        pywhatkit.sendwhatmsg_instantly(phone, message)  # Short wait time
        return redirect('/trainer')

    except Exception as e:
        return f"Error: {e}"
@app.route('/teacher_signup')
def signup_form():
    return render_template('teachers_signup.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    username = request.form['username']
    f_name = request.form['fname']
    m_name = request.form['mname']
    l_name = request.form['lname']
    password = request.form['lname']
    gender = request.form['gender']
    age = request.form['age']
    id_number = request.form['id-number']



    email = request.form['email']
    phone = request.form['phone']
    grade = request.form['grade']
    subject = request.form['subject']
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect('admin.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO teachers (username, email, phone, grade, subject, date) VALUES (?, ?, ?, ?, ?, ?)',
                   (username, email, phone, grade, subject, date))
    conn.commit()
    cursor.execute('INSERT INTO logins(position, password) VALUES(?, ?)',(username, password))
    conn.commit()
    cursor.execute(
    'INSERT INTO admin_data (position, f_name, m_name, l_name, gender, age, id_number) VALUES (?, ?, ?, ?, ?, ?, ?)',
    (username, f_name, m_name, l_name, gender, age, id_number))

    conn.commit()
    conn.close()
    sender_email = "richardkeith233@gmail.com"
    sender_password = "mnoj wsox aumw tkrs"  # Use App Password if 2FA is enabled
    recipient_email = email
    password2 = l_name

    subject = "Crimsons portal"
    body = f"Welcome teacher {f_name} {l_name} and feel at home your last name will be your default password: {password2} and Username: {username}"

    send_mail1.send_email(sender_email,recipient_email, sender_password, password2, subject, body)

    return "Teacher Signup Successful!"

@app.route('/delete_students', methods=['GET','POST'])
def delete_students():
    username = session.get('username')
    username = document_functions.replace_slash_with_dot(username)
    profile_pic = database.get_aprofile(username)
    return render_template('students.html', profile_pic=profile_pic)

@app.route('/delete_teachers', methods=['GET','POST'])
def delete_teachers():
    username = session.get('username')
    username = document_functions.replace_slash_with_dot(username)
    profile_pic = database.get_aprofile(username)
    return render_template('teachers.html', profile_pic=profile_pic)

@app.route('/forgot_password1')
def forgot_password1():
    return render_template("forgot_password.html")
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():

    email = request.form['email']
    student_email = database.get_emails('student.db','students','email')
    admin_email = database.get_emails('manager.db', 'manager', 'email')
    teacher_email = database.get_emails('admin.db','teachers', 'email' )
    users = student_email + admin_email + teacher_email
    default_password = None
    if email in users:
        if email in student_email:
            default_password = database.get_password_s('student.db', email)
        elif email in admin_email:
            default_password = database.get_password_m('manager.db', email)
        elif email in teacher_email:
            default_password = database.get_password_t('admin.db', email)

             # You can generate a random one

        sender_email = "richardkeith233@gmail.com"
        sender_password = "mnoj wsox aumw tkrs"
        subject = "Password Reset"

        body = f"Your new password is: {default_password}. Please log in and change it."

        send_mail1.forgot_m_pass(sender_email,sender_password, email, subject, body)
            # Send email

    return redirect(url_for('password_reset'))
@app.route("/password_reset")
def password_reset():
    return render_template("password_reset.html")


#=============== SUBJECT ENROLLMENT ROUTES ===============#
import enroll_subjects

@app.route('/enroll_class_subjects', methods=['GET', 'POST'])
def enroll_class_subjects():
    """Main page for teacher to select class and enroll in subjects"""
    teacher_id = session.get('userName')
    if not teacher_id:
        return redirect(url_for('login'))
    
    profile_pic = database.get_profile_t(teacher_id)
    conn = sqlite3.connect("admin.db")
    cursor = conn.cursor()
    
    # Get the classes assigned to this teacher
    cursor.execute("SELECT grade FROM teachers WHERE username = ?", (teacher_id,))
    result = cursor.fetchone()
    conn.close()
    
    class_options = {}
    enrollment_status = None
    selected_class = None
    
    if result:
        grade_numbers = result[0].split(",")
        class_options = {num.strip(): class_mapping[num.strip()] for num in grade_numbers if num.strip() in class_mapping}
    
    # Handle class selection
    if request.method == 'POST':
        selected_class = request.form.get('class_select')
        if selected_class and selected_class in class_mapping1:
            grade_key = class_mapping1[selected_class]
            current_year = str(datetime.now().year)
            enrollment_status = enroll_subjects.get_class_enrollment_status(grade_key, current_year)
    
    return render_template('enroll_subjects.html', 
                         class_options=class_options,
                         available_subjects=enroll_subjects.AVAILABLE_SUBJECTS,
                         profile_pic=profile_pic,
                         selected_class=selected_class,
                         enrollment_status=enrollment_status)


@app.route('/enroll_class_subjects_submit', methods=['POST'])
def enroll_class_subjects_submit():
    """Process subject enrollment for entire class"""
    teacher_id = session.get('userName')
    if not teacher_id:
        return redirect(url_for('login'))
    
    class_id = request.form.get('class_id')
    selected_subjects = request.form.getlist('subjects')
    
    if not class_id or class_id not in class_mapping1:
        flash('Invalid class selected', 'error')
        return redirect(url_for('enroll_class_subjects'))
    
    if not selected_subjects:
        flash('Please select at least one subject', 'warning')
        return redirect(url_for('enroll_class_subjects'))
    
    grade_key = class_mapping1[class_id]
    current_year = str(datetime.now().year)
    enrollment_results = {}
    
    for subject in selected_subjects:
        result = enroll_subjects.enroll_class_in_subject(grade_key, subject, current_year)
        enrollment_results[subject] = result
    
    # Build success message
    message = f"Enrollment complete. "
    for subject, result in enrollment_results.items():
        message += f"{subject}: {result['enrolled']} students enrolled. "
    
    flash(message, 'success')
    return redirect(url_for('enroll_class_subjects', class_select=class_id))


@app.route('/manage_student_subjects', methods=['GET', 'POST'])
def manage_student_subjects_page():
    """View students in a class and their subject enrollment"""
    teacher_id = session.get('userName')
    if not teacher_id:
        return redirect(url_for('login'))
    
    profile_pic = database.get_profile_t(teacher_id)
    conn = sqlite3.connect("admin.db")
    cursor = conn.cursor()
    
    # Get teacher's classes
    cursor.execute("SELECT grade FROM teachers WHERE username = ?", (teacher_id,))
    result = cursor.fetchone()
    conn.close()
    
    class_options = {}
    students_info = []
    selected_class = None
    class_name = None
    
    if result:
        grade_numbers = result[0].split(",")
        class_options = {num.strip(): class_mapping[num.strip()] for num in grade_numbers if num.strip() in class_mapping}
    
    if request.method == 'POST':
        selected_class = request.form.get('class_select')
        if selected_class and selected_class in class_mapping1:
            grade_key = class_mapping1[selected_class]
            class_name = class_mapping.get(selected_class)
            
            # Get all students in class with their enrolled subjects
            all_students = enroll_subjects.get_students_in_class(grade_key)
            current_year = str(datetime.now().year)
            for student in all_students:
                admission_no, first_name, last_name = student
                enrolled_subjects = enroll_subjects.get_student_enrolled_subjects(admission_no, current_year)
                students_info.append({
                    'admission_no': admission_no,
                    'first_name': first_name,
                    'last_name': last_name,
                    'subjects': enrolled_subjects
                })
    
    return render_template('manage_student_subjects.html',
                         class_options=class_options,
                         profile_pic=profile_pic,
                         selected_class=selected_class,
                         class_name=class_name,
                         class_id=selected_class,
                         students=students_info)


@app.route('/edit_student_subjects', methods=['POST'])
def edit_student_subjects():
    """Edit subjects for a single student"""
    teacher_id = session.get('userName')
    if not teacher_id:
        return redirect(url_for('login'))
    
    admission_no = request.form.get('admission_no')
    class_id = request.form.get('class_id')
    
    profile_pic = database.get_profile_t(teacher_id)
    
    # Get student details
    conn = sqlite3.connect('student.db')
    cursor = conn.cursor()
    cursor.execute('SELECT first_name, last_name FROM students WHERE admission_no = ?', (admission_no,))
    student = cursor.fetchone()
    conn.close()
    
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('manage_student_subjects_page'))
    
    first_name, last_name = student
    current_year = str(datetime.now().year)
    enrolled_subjects = enroll_subjects.get_student_enrolled_subjects(admission_no, current_year)
    
    return render_template('edit_student_subjects.html',
                         admission_no=admission_no,
                         first_name=first_name,
                         last_name=last_name,
                         class_id=class_id,
                         available_subjects=enroll_subjects.AVAILABLE_SUBJECTS,
                         enrolled_subjects=enrolled_subjects,
                         profile_pic=profile_pic)


@app.route('/save_student_subjects', methods=['POST'])
def save_student_subjects():
    """Save subject changes for a student"""
    teacher_id = session.get('userName')
    if not teacher_id:
        return redirect(url_for('login'))
    
    admission_no = request.form.get('admission_no')
    class_id = request.form.get('class_id')
    selected_subjects = request.form.getlist('subjects')
    current_year = str(datetime.now().year)
    
    # Get current enrolled subjects
    current_subjects = set(enroll_subjects.get_student_enrolled_subjects(admission_no, current_year))
    new_subjects = set(selected_subjects)
    
    # Unenroll subjects that were removed
    for subject in current_subjects - new_subjects:
        enroll_subjects.unenroll_student_subject(admission_no, subject, current_year)
    
    # Enroll new subjects
    for subject in new_subjects - current_subjects:
        enroll_subjects.enroll_student_subject(admission_no, subject, current_year)
    
    flash('Subject enrollment updated successfully', 'success')
    return redirect(url_for('manage_student_subjects_page'))


# ===================== ATTENDANCE MANAGEMENT =====================

@app.route('/attendance')
def attendance():
    """Render attendance marking page for teachers"""
    teacher_id = session.get('userName')
    if not teacher_id:
        return redirect(url_for('login'))
    
    profile_pic = database.get_profile_t(teacher_id)
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('attendance.html', 
                         profile_pic=profile_pic, 
                         teacher_id=teacher_id,
                         current_date=current_date)


@app.route('/get_todays_marked_students', methods=['GET'])
def get_todays_marked_students():
    """Fetch all students marked present today"""
    teacher_id = session.get('userName')
    if not teacher_id:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT a.admission_no, s.first_name, s.last_name, a.time_in, r.Grade
        FROM attendance a
        JOIN students s ON a.admission_no = s.admission_no
        LEFT JOIN rest r ON a.admission_no = r.admission_no
        WHERE a.date = ? AND a.status = 'present'
        ORDER BY a.time_in ASC
        ''', (date,))
        records = cursor.fetchall()
    
    marked_students = [
        {
            'admission': record[0],
            'name': f"{record[1]} {record[2]}",
            'time': record[3],
            'grade': record[4] if record[4] else 'N/A'
        }
        for record in records
    ]
    
    return jsonify({'success': True, 'students': marked_students})

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    """Mark student attendance via QR code or admission number"""
    teacher_id = session.get('userName')
    if not teacher_id:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    data = request.get_json()
    admission_no = data.get('admission_no', '').strip()
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    if not admission_no:
        return jsonify({'success': False, 'message': 'Admission number required'})
    
    # Convert admission number if needed
    admission_no = document_functions.replace_slash_with_slash(admission_no)
    
    # Check if student exists and get grade
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT s.first_name, s.last_name, r.Grade 
        FROM students s
        LEFT JOIN rest r ON s.admission_no = r.admission_no
        WHERE s.admission_no = ?
        ''', (admission_no,))
        student = cursor.fetchone()
    
    if not student:
        return jsonify({'success': False, 'message': 'Student not found'})
    
    first_name, last_name, grade = student
    current_time = datetime.now().strftime('%H:%M:%S')
    
    # Mark attendance
    success = database.mark_student_attendance(admission_no, date, current_time, teacher_id)
    
    if success:
        return jsonify({
            'success': True, 
            'message': f'{first_name} {last_name} marked present',
            'student_name': f'{first_name} {last_name}',
            'grade': grade if grade else 'N/A',
            'time': current_time
        })
    else:
        return jsonify({'success': False, 'message': 'Error marking attendance'})


@app.route('/get_class_attendance')
def get_class_attendance_route():
    """Get attendance list for a class"""
    teacher_id = session.get('userName')
    if not teacher_id:
        return redirect(url_for('login'))
    
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    class_id = request.args.get('class_id')
    
    if not class_id or class_id not in class_mapping1:
        flash('Invalid class selected', 'error')
        return redirect(url_for('attendance'))
    
    grade_key = class_mapping1[class_id]
    attendance_records = database.get_class_attendance(grade_key, date)
    profile_pic = database.get_profile_t(teacher_id)
    
    return render_template('attendance_list.html',
                         attendance_records=attendance_records,
                         class_name=class_mapping[class_id],
                         date=date,
                         profile_pic=profile_pic)


@app.route('/scan_qr_python', methods=['GET'])
def scan_qr_python():
    """
    Server-side QR code scanning using Python.
    Captures frame from camera and detects QR code.
    """
    teacher_id = session.get('userName')
    if not teacher_id:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    try:
        qr_data, frame_b64 = qr_scanner.capture_and_scan_frame()
        
        if qr_data:
            admission_no = qr_scanner.extract_admission_number(qr_data)
            if admission_no:
                return jsonify({
                    'success': True,
                    'qr_detected': True,
                    'admission_no': admission_no,
                    'qr_data': qr_data,
                    'frame': frame_b64 if frame_b64 else None
                })
            else:
                return jsonify({
                    'success': False,
                    'qr_detected': True,
                    'message': 'QR code found but could not extract admission number',
                    'frame': frame_b64 if frame_b64 else None
                })
        else:
            return jsonify({
                'success': False,
                'qr_detected': False,
                'message': 'No QR code detected',
                'frame': frame_b64 if frame_b64 else None
            })
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error in scan_qr_python: {str(e)}")
        return jsonify({'success': False, 'message': f'Scanning error: {str(e)}'})


@app.route('/scan_qr_from_image', methods=['POST'])
def scan_qr_from_image():
    """
    Scans QR code from an image uploaded from the client.
    """
    teacher_id = session.get('userName')
    if not teacher_id:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    try:
        data = request.get_json()
        image_base64 = data.get('image', '')
        
        if not image_base64:
            return jsonify({'success': False, 'message': 'No image provided'})
        
        qr_data = qr_scanner.scan_qr_from_base64(image_base64)
        
        if qr_data:
            admission_no = qr_scanner.extract_admission_number(qr_data)
            if admission_no:
                return jsonify({
                    'success': True,
                    'qr_detected': True,
                    'admission_no': admission_no,
                    'qr_data': qr_data
                })
            else:
                return jsonify({
                    'success': False,
                    'qr_detected': True,
                    'message': 'QR code found but could not extract admission number'
                })
        else:
            return jsonify({
                'success': False,
                'qr_detected': False,
                'message': 'No QR code detected in image'
            })
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error in scan_qr_from_image: {str(e)}")
        return jsonify({'success': False, 'message': f'Scanning error: {str(e)}'})


@app.route('/students_by_grade')
def students_by_grade():
    """View all students grouped by grade"""
    teacher_id = session.get('userName')
    if not teacher_id:
        return redirect(url_for('login'))
    
    profile_pic = database.get_profile_t(teacher_id)
    
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        # Get all students grouped by grade, ordered by grade and name
        cursor.execute('''
            SELECT r.Grade, s.admission_no, s.first_name, s.last_name
            FROM students s
            LEFT JOIN rest r ON s.admission_no = r.admission_no
            ORDER BY r.Grade ASC, s.last_name ASC, s.first_name ASC
        ''')
        students = cursor.fetchall()
    
    # Group students by grade
    students_by_grade_dict = {}
    for grade, admission_no, first_name, last_name in students:
        grade_name = grade if grade else 'Unassigned'
        if grade_name not in students_by_grade_dict:
            students_by_grade_dict[grade_name] = []
        students_by_grade_dict[grade_name].append({
            'admission_no': admission_no,
            'first_name': first_name,
            'last_name': last_name,
            'admission_no_encoded': document_functions.replace_slash_with_dot(admission_no)
        })
    
    # Sort grades
    sorted_grades = sorted(students_by_grade_dict.keys())
    
    # Calculate total students
    total_students = sum(len(students) for students in students_by_grade_dict.values())
    
    return render_template('students_by_grade.html',
                         students_by_grade=students_by_grade_dict,
                         sorted_grades=sorted_grades,
                         total_students=total_students,
                         profile_pic=profile_pic)


@app.route('/attendance_history/<admission_no>')
def attendance_history(admission_no):
    """View attendance history for a student"""
    teacher_id = session.get('userName')
    if not teacher_id:
        return redirect(url_for('login'))
    
    admission_n = document_functions.replace_slash_with_slash(admission_no)
    
    # Get student info
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT first_name, last_name FROM students WHERE admission_no = ?', (admission_n,))
        student = cursor.fetchone()
    
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('attendance'))
    
    first_name, last_name = student
    history = database.get_student_attendance_history(admission_n, days=60)
    profile_pic = database.get_profile_t(teacher_id)
    
    return render_template('attendance_history.html',
                         first_name=first_name,
                         last_name=last_name,
                         admission_no=document_functions.replace_slash_with_dot(admission_no),
                         history=history,
                         profile_pic=profile_pic)


@app.route('/register_out', methods=['GET', 'POST'])
def register_out():
    """Page for student checkout"""
    teacher_id = session.get('userName')
    if not teacher_id:
        return redirect(url_for('login'))
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    profile_pic = database.get_profile_t(teacher_id)
    
    return render_template('register_out.html', 
                         current_date=current_date,
                         profile_pic=profile_pic)


@app.route('/attendance_report', methods=['GET', 'POST'])
def attendance_report():
    """View attendance report with filters"""
    teacher_id = session.get('userName')
    if not teacher_id:
        return redirect(url_for('login'))
    
    profile_pic = database.get_profile_t(teacher_id)
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Default filters
    filter_date = request.args.get('date', current_date)
    filter_grade = request.args.get('grade', '')
    filter_admission = request.args.get('admission', '').strip()
    filter_name = request.args.get('name', '').strip()
    
    # Build query based on filters
    query = '''
    SELECT a.admission_no, s.first_name, s.last_name, a.time_in, a.time_out, 
           a.marked_by, a.marked_out_by, r.Grade
    FROM attendance a
    JOIN students s ON a.admission_no = s.admission_no
    LEFT JOIN rest r ON a.admission_no = r.admission_no
    WHERE a.date = ?
    '''
    
    params = [filter_date]
    
    if filter_grade:
        query += ' AND r.Grade = ?'
        params.append(filter_grade)
    
    if filter_admission:
        query += ' AND a.admission_no LIKE ?'
        params.append(f'%{filter_admission}%')
    
    if filter_name:
        query += ' AND (s.first_name LIKE ? OR s.last_name LIKE ?)'
        params.append(f'%{filter_name}%')
        params.append(f'%{filter_name}%')
    
    query += ' ORDER BY r.Grade ASC, s.last_name ASC'
    
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        records = cursor.fetchall()
    
    # Get unique grades for filter dropdown
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT Grade FROM rest ORDER BY Grade ASC')
        grades = [row[0] for row in cursor.fetchall() if row[0]]
    
    attendance_records = [
        {
            'admission': record[0],
            'first_name': record[1],
            'last_name': record[2],
            'time_in': record[3],
            'time_out': record[4],
            'marked_by': record[5],
            'marked_out_by': record[6] if record[6] else '-',
            'grade': record[7] if record[7] else 'N/A'
        }
        for record in records
    ]
    
    return render_template('attendance_report.html',
                         attendance_records=attendance_records,
                         grades=grades,
                         filter_date=filter_date,
                         filter_grade=filter_grade,
                         filter_admission=filter_admission,
                         filter_name=filter_name,
                         profile_pic=profile_pic,
                         total_present=len(attendance_records))


@app.route('/mark_checkout', methods=['POST'])
def mark_checkout():
    """Mark student checkout (register out)"""
    teacher_id = session.get('userName')
    if not teacher_id:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    data = request.get_json()
    admission_no = data.get('admission_no', '').strip()
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    if not admission_no:
        return jsonify({'success': False, 'message': 'Admission number required'})
    
    # Convert admission number if needed
    admission_no = document_functions.replace_slash_with_slash(admission_no)
    
    # Check if student exists and is checked in
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT s.first_name, s.last_name, r.Grade, a.time_in, a.time_out
        FROM students s
        LEFT JOIN rest r ON s.admission_no = r.admission_no
        LEFT JOIN attendance a ON s.admission_no = a.admission_no AND a.date = ?
        WHERE s.admission_no = ?
        ''', (date, admission_no))
        student = cursor.fetchone()

    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE attendance 
        SET status = 'out'
        WHERE admission_no = ? AND date = ?
        ''', (admission_no, date))
        conn.commit()

    
    if not student:
        return jsonify({'success': False, 'message': 'Student not found'})
    
    first_name, last_name, grade, time_in, time_out = student
    
    if not time_in:
        return jsonify({'success': False, 'message': 'Student has not checked in today'})
    
    if time_out:
        return jsonify({'success': False, 'message': 'Student already checked out'})
    
    current_time = datetime.now().strftime('%H:%M:%S')
    
    # Mark checkout
    success = database.mark_student_checkout(admission_no, date, current_time, teacher_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': f'{first_name} {last_name} checked out',
            'student_name': f'{first_name} {last_name}',
            'grade': grade if grade else 'N/A',
            'time_in': time_in,
            'time_out': current_time
        })
    else:
        return jsonify({'success': False, 'message': 'Error marking checkout'})


@app.route('/get_todays_checkouts', methods=['GET'])
def get_todays_checkouts():
    """Get all students checked out today"""
    teacher_id = session.get('userName')
    if not teacher_id:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT a.admission_no, s.first_name, s.last_name, a.time_in, a.time_out, a.marked_out_by, r.Grade
        FROM attendance a
        JOIN students s ON a.admission_no = s.admission_no
        LEFT JOIN rest r ON a.admission_no = r.admission_no
        WHERE a.date = ? AND a.time_out IS NOT NULL
        ORDER BY a.time_out DESC
        ''', (date,))
        records = cursor.fetchall()
    
    checkout_students = [
        {
            'admission': record[0],
            'name': f"{record[1]} {record[2]}",
            'time_in': record[3],
            'time_out': record[4],
            'marked_out_by': record[5] if record[5] else 'System',
            'grade': record[6] if record[6] else 'N/A'
        }
        for record in records
    ]
    
    return jsonify({'success': True, 'checkouts': checkout_students})
    


@app.route('/teacher/upload_assignment', methods=['GET', 'POST'])
def upload_assignment():
    # teachers only
    if 'userName' not in session:
        flash('Please log in as a teacher to upload assignments')
        return redirect(url_for('login'))

    if request.method == 'POST':
        target_class_display = request.form.get('target_class', 'All')
        # Convert display name back to numeric key for storage
        target_class = next((k for k, v in class_mapping.items() if v == target_class_display), target_class_display)
        description = request.form.get('description', '')
        f = request.files.get('assignment_file')
        if not f or f.filename == '':
            flash('No file selected')
            return redirect(request.url)

        if not allowed_assignment_file(f.filename):
            flash('File type not allowed')
            return redirect(request.url)

        os.makedirs(PROTECTED_ASSIGNMENTS_FOLDER, exist_ok=True)
        stored_name = f"{int(time.time())}_{secure_filename(f.filename)}"
        filepath = os.path.join(PROTECTED_ASSIGNMENTS_FOLDER, stored_name)
        f.save(filepath)

        with sqlite3.connect('student.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assignments(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stored_name TEXT,
                    original_name TEXT,
                    target_class TEXT,
                    uploaded_by TEXT,
                    upload_time TEXT,
                    description TEXT
                )
            ''')
            # Add description column if it doesn't exist (migration)
            try:
                cursor.execute('ALTER TABLE assignments ADD COLUMN description TEXT')
            except sqlite3.OperationalError:
                # Column already exists
                pass
            
            cursor.execute('''
                INSERT INTO assignments (stored_name, original_name, target_class, uploaded_by, upload_time, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (stored_name, f.filename, target_class, session.get('userName'), datetime.now().isoformat(), description))
            conn.commit()

        flash('Assignment uploaded successfully')
        return redirect(url_for('teacher_assignments'))

    # GET: list classes assigned to this teacher using the mapping
    teacher_username = session.get('userName')
    with sqlite3.connect('admin.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT grade FROM teachers WHERE username = ?', (teacher_username,))
        result = cursor.fetchone()
    
    classes = []
    if result and result[0]:
        # Parse comma-separated grade numbers
        grade_numbers = [num.strip() for num in result[0].split(',')]
        # Map to display names using class_mapping1
        classes = [(num, class_mapping1.get(num, num)) for num in grade_numbers if num in class_mapping1]

    return render_template('upload_assignment.html', classes=classes, profile_pic=database.get_profile_t(teacher_username))


@app.route('/teacher/assignments')
def teacher_assignments():
    # teachers view their own uploaded assignments
    if 'userName' not in session:
        return redirect(url_for('login'))

    teacher_username = session.get('userName')

    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, original_name, target_class, description, upload_time
            FROM assignments
            WHERE uploaded_by = ?
            ORDER BY upload_time DESC
        ''', (teacher_username,))
        rows = cursor.fetchall()

    assignments = [
        {
            'id': r[0],
            'name': r[1],
            'target_class': class_mapping1.get(r[2], r[2]),  # Convert key to display name
            'description': r[3] if r[3] else '(No description)',
            'upload_time': r[4]
        }
        for r in rows
    ]

    return render_template('teacher_assignments.html', assignments=assignments, profile_pic=database.get_profile_t(teacher_username))


@app.route('/teacher/assignments/delete/<int:assignment_id>', methods=['POST'])
def delete_assignment(assignment_id):
    # delete assignment (teachers only)
    if 'userName' not in session:
        flash('Please log in as a teacher')
        return redirect(url_for('login'))

    teacher_username = session.get('userName')

    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT stored_name, uploaded_by FROM assignments WHERE id = ?', (assignment_id,))
        row = cursor.fetchone()

    if not row:
        flash('Assignment not found')
        return redirect(url_for('teacher_assignments'))

    stored_name, uploaded_by = row

    # Authorization: only the teacher who uploaded it can delete it
    if uploaded_by != teacher_username:
        flash('You can only delete your own assignments')
        return redirect(url_for('teacher_assignments'))

    # Delete file from protected folder
    filepath = os.path.join(PROTECTED_ASSIGNMENTS_FOLDER, stored_name)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception as e:
            flash(f'Error deleting file: {str(e)}')
            return redirect(url_for('teacher_assignments'))

    # Delete from database
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM assignments WHERE id = ?', (assignment_id,))
        conn.commit()

    flash('Assignment deleted successfully')
    return redirect(url_for('teacher_assignments'))


@app.route('/assignments')
def assignments_list():
    # students view assignments for their class
    if 'admission_no' not in session:
        return redirect(url_for('login'))

    admission_no = session.get('admission_no')
    student_grade = database.get_grade_st(admission_no) or 'Unassigned'
    
    # Normalize student grade to numeric key
    # Try to find the numeric key that maps to the student's grade
    grade_key = None
    if student_grade != 'Unassigned':
        # Check if it's already a numeric key
        if student_grade in class_mapping1:
            grade_key = student_grade
        else:
            # Try to find it in reverse (grade display name to key)
            for key, display_name in class_mapping1.items():
                if display_name == student_grade:
                    grade_key = key
                    break
            # If still not found, use the student grade as-is
            if not grade_key:
                grade_key = student_grade

    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, original_name, target_class, uploaded_by, upload_time, description
            FROM assignments
            WHERE target_class = ?
            ORDER BY upload_time DESC
        ''', (grade_key,))
        rows = cursor.fetchall()

    assignments = [
        {
            'id': r[0],
            'name': r[1],
            'target_class': class_mapping1.get(r[2], r[2]),  # Convert key to display name
            'uploaded_by': r[3],
            'upload_time': r[4],
            'description': r[5] if r[5] else '(No description)'
        }
        for r in rows
    ]

    return render_template('assignments.html', assignments=assignments, profile_pic=database.get_profile(admission_no))


@app.route('/assignments/download/<int:assignment_id>')
def download_assignment(assignment_id):
    with sqlite3.connect('student.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT stored_name, original_name, target_class FROM assignments WHERE id = ?', (assignment_id,))
        row = cursor.fetchone()

    if not row:
        flash('Assignment not found')
        return redirect(url_for('assignments_list'))

    stored_name, original_name, target_class = row

    # Authorization: allow if student and class matches, or if teacher is logged in
    if 'admission_no' in session:
        student_grade = database.get_grade_st(session.get('admission_no'))
        # Normalize student grade to numeric key
        grade_key = None
        if student_grade:
            if student_grade in class_mapping1:
                grade_key = student_grade
            else:
                for key, display_name in class_mapping1.items():
                    if display_name == student_grade:
                        grade_key = key
                        break
                if not grade_key:
                    grade_key = student_grade
        
        if grade_key != target_class:
            flash('You are not authorized to download this file')
            return redirect(url_for('assignments_list'))
    elif 'userName' in session:
        # teacher/manager allowed
        pass
    else:
        return redirect(url_for('login'))

    filepath = os.path.join(PROTECTED_ASSIGNMENTS_FOLDER, stored_name)
    if not os.path.exists(filepath):
        flash('File missing on server')
        return redirect(url_for('assignments_list'))

    return send_file(filepath, as_attachment=True, download_name=original_name)

    return jsonify({'success': True, 'checkouts': checkout_students})


if __name__ == '__main__':
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')
    database.add_all_tables()
    app.run(debug=True)
