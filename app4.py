
# import requests
# import profile1
# import send_mail1
# from requests.auth import HTTPBasicAuth
# import base64
# import webbrowser
# import qrcode3
# from flask import Flask, render_template, request, redirect,jsonify, flash, url_for, send_from_directory, session, send_file, request
# import sqlite3, os, database, document_functions, json,requests
# import io
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
# from reportlab.lib.units import inch
# from reportlab.pdfgen import canvas
# from datetime import datetime
# import logging
# import time
# import graph2
# import enroll_subjects

# app = Flask(__name__)

# app.secret_key = 'My_Secret_Key'

# TOTAL_FEES = 2000

# @app.route('/', methods=['GET', 'POST'])
# def login():

#     if request.method == 'POST':

#         admission_no = request.form['admission_no']
#         password = request.form['password']

#         with sqlite3.connect('student.db') as conn:
#             cursor = conn.cursor()
#             cursor.execute('''
#                 SELECT COUNT(*)
#                 FROM logins
#                 WHERE admission_no = ? AND password = ?
#             ''', (admission_no, password))

#             count = cursor.fetchone()[0]
#             if count > 0:  # If the student exists,
#                 session['admission_no'] = admission_no
#                 return redirect(url_for('home'))
#             elif count < 1:
#                 with sqlite3.connect('manager.db') as conn:
#                     cursor = conn.cursor()
#                     cursor.execute('''
#                     SELECT COUNT(*)
#                     FROM logins
#                     WHERE username = ? AND password = ?

#                     ''', (admission_no, password))
#                     count = cursor.fetchone()[0]
#                     if count > 0:
#                         session['username'] = admission_no
#                         return redirect(url_for('add_or_remove_student'))
#                     else:
#                         with sqlite3.connect('admin.db') as conn:
#                             cursor = conn.cursor()
#                             cursor.execute('''
#                                 SELECT COUNT(*)
#                                 FROM logins
#                                 WHERE position = ? AND password = ?
#                             ''', (admission_no, password))

#                             count = cursor.fetchone()[0]
#                             if count > 0:
#                                 session['userName'] = admission_no
#                                 return redirect(url_for('admin_dashboard'))

#                             else:
#                                 return render_template('login.html', error="Invalid admission number or password")
#     return render_template('login.html')

# #====================profile
# @app.route('/home')
# def home():
#     admission_no = session.get('admission_no')
#     admission_number = session.get('admission_no')
#     dates, amounts, remaining_balance = graph2.profile(admission_number)
#     return render_template('home.html', name=database.get_first_name(admission_no),sname=database.get_last_name(admission_no),email=database.get_email(admission_no),phone = database.get_phone(admission_no), gender= database.get_gender(admission_no),profile_pic = database.get_profile(admission_no),
#                            greeting=document_functions.greet_based_on_time(), admission_no=document_functions.replace_slash_with_dot(admission_no),dates=dates, amounts=amounts,remaining_balance=remaining_balance,admission_number= admission_number,\
#                            admission_date = database.get_admission_date(admission_number))
# #=============Update student Qr
# @app.route('/updateQrSt')
# def student_qr():
#     admission_no = session.get('admission_no')
#     fname=database.get_first_name(admission_no)
#     lname=database.get_last_name(admission_no)
#     dob = database.get_admission_date_st(admission_no)
#     grade = database.get_grade_st(admission_no)
#     qrcode3.generate_qr_st(fname, lname, dob, admission_no, grade)
#     profile_pic = database.get_profile(admission_no)
#     qrcode_pic = database.get_qr_pic_st(admission_no)
#     print("success")
#     return render_template('stqrcode.html',profile_pic = profile_pic, qrcode_pic = qrcode_pic)
# @app.route('/tdash')
# def teacher_home():
#     userName = session.get('userName')
#     return render_template('thome.html',profile_pic = database.get_profile_t(userName),name = database.get_first_name_t(userName), sname=database.get_last_name_t(userName),email=database.get_email_t(userName),phone = database.get_phone_t(userName), gender= database.get_gender_t(userName), join_date = database.get_join_date_t(userName))
# @app.route('/fee')
# def fee():
#     return render_template('fee.html')


# @app.route('/student_scores')
# def student_scores():
#     admission_no = session.get('admission_no')
#     conn = sqlite3.connect('student.db')
#     cursor = conn.cursor()

#     # Get the current year and calculate the past four years
#     current_year = datetime.now().year
#     years = [current_year - i for i in range(4)]

#     # Query to get exam scores for the past available years
#     query = '''
#         SELECT year, term, average
#         FROM marks
#         WHERE admission_no = ? AND year <= ?
#         ORDER BY year, term
#     '''
#     cursor.execute(query, (admission_no, current_year))
#     rows = cursor.fetchall()
#     conn.close()

#     # Organize data into a dictionary by year
#     exam_scores = {str(year): [] for year in years}
#     # Get enrolled subjects for the current year
#     enrolled_subjects = enroll_subjects.get_student_enrolled_subjects(admission_no, current_year)
#     for row in rows:
#         year, term, average = row
#         exam_scores[str(year)].append(average)

#     # Filter out years with no data
#     exam_scores = {year: average for year,average in exam_scores.items() if average}
#     exam_list= database.get_exam_type(admission_no)

#     # Fetch structured student marks filtered to enrolled subjects
#     try:
#         student_marks = view_student_marks2(admission_no, enrolled_subjects)
#     except Exception:
#         student_marks = []

#     return render_template('examtrend.html', exam_scores=exam_scores, student_id=admission_no, student_marks=student_marks, length = len(student_marks), profile_pic = database.get_profile(admission_no), exam_list=exam_list, enrolled_subjects=enrolled_subjects)


# @app.route('/settings')
# def settings():
#     admission_no = session.get('admission_no')
#     profile_pic = database.get_profile(admission_no)
#     return render_template('settings.html',profile_pic=profile_pic, admission_no = admission_no)

# @app.route('/trainer2')
# def trainer2():
#     return render_template('trainer2.html')

# @app.route('/logout')
# def logout():
#     admission_no = session.get('admission_no')
#     profile_pic = database.get_profile(admission_no)
#     return redirect(url_for('login'))


# #_______________________________________________________________________________________
# #=================================================================================#
# #----------------ADMIN----------------------
# # List of subjects (make sure the names match the ones in the HTML form)
# subjects = ['mathematics', 'biology', 'chemistry', 'physics', 'geography', 'business', 'english', 'kiswahili', 'cre',
#             'french']


# @app.route('/admin_dash')
# def admin_dashboard():
#     admission_no = None
#     return render_template("admin_dashboard.html", admission_no=admission_no)


# @app.route('/submit_marks', methods=['POST'])
# def submit_marks():
#     # Extract marks from the form and put them into a list
#     marks_list = [int(request.form[subject]) for subject in subjects]

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



# @app.route('/submit_selection', methods=['GET', 'POST'])
# def submit_selection():
#     return redirect(url_for('enter_student_marks'))


# @app.route('/submit_check', methods=['POST'])
# def submit_check():
#     marks_list = [int(request.form[subject]) for subject in subjects]
#     database.insert_marks(document_functions.replace_slash_with_slash(request.form['admission_no']), marks_list)


# class_mapping = {
#     "1": "Grade 1",
#     "2": "Grade 2",
#     "3": "Grade 3",
#     "4": "Grade 4",
#     "5": "Grade 5",
#     "6": "Grade 6",
#     "7": "Form 1",
#     "8": "Form 2",
#     "9": "Form 3",
#     "10": "Form 4",
#     "11": "Form 5",
#     "12": "Form 6",
# }
# class_mapping1 = {
#     "1": "playgroup",
#     "2": "pp1",
#     "3": "pp2",
#     "4": "grade1",
#     "5": "grade2",
#     "6": "grade3",
#     "7": "grade4",
#     "8": "grade5",
#     "9": "grade6",
#     "10": "grade7",
#     "11": "grade8",
#     "12": "grade9",
#     "13": "grade10",
#     "14": "grade11",
#     "15": "grade12",
# }

# @app.route("/type_check2")
# def teacher_classes():
#     teacher_id = session.get('userName')
#     conn = sqlite3.connect("admin.db")
#     cursor = conn.cursor()

#     # Fetch the subjects column for the teacher
#     cursor.execute("SELECT grade FROM teachers WHERE username = ?", (teacher_id,))
#     result = cursor.fetchone()
#     conn.close()

#     if result:
#         subject_numbers = result[0].split(",")  # Convert "4,5,6" to ["4", "5", "6"]
#         class_options = {num: class_mapping[num] for num in subject_numbers if num in class_mapping}

#     else:
#         class_options = {}

#     return render_template("type_check1.html", class_options=class_options, profile_pic = database.get_profile_t(teacher_id))

# @app.route('/type_check')
# def type_check():
#     teacher_id = session.get('userName')
#     conn = sqlite3.connect("admin.db")
#     cursor = conn.cursor()

#     # Fetch the subjects column for the teacher
#     cursor.execute("SELECT grade FROM teachers WHERE username = ?", (teacher_id,))
#     result = cursor.fetchone()
#     conn.close()

#     if result:
#         subject_numbers = result[0].split(",")  # Convert "4,5,6" to ["4", "5", "6"]
#         class_options = {num: class_mapping[num] for num in subject_numbers if num in class_mapping}

#     else:
#         class_options = {}

#     return render_template("type_check.html", class_options=class_options, profile_pic = database.get_profile_t(teacher_id))



# @app.route('/students', methods=['GET', 'POST'])
# def view_students():
#     year = int(request.form['year'])
#     term = int(request.form['term'])
#     exam_type = request.form['type']
#     grade = request.form['class']
#     data = database.get_students_marks_filtered(year, term, exam_type, grade)
#     print(f"the data is:{data}")
#     return render_template('exam_list.html', students=data)


# @app.route('/enter_marks/<admission_no>', methods=['GET', 'POST'])
# def enter_student_marks(admission_no):
#     admission_n = document_functions.replace_slash_with_slash(admission_no)
#     year = request.form['year']
#     term = int(request.form['term'])
#     exam_type = request.form['type']
#     database.insert_time(admission_n, year, term, exam_type)

#     return render_template('enter_marks.html', admission_no=admission_n,year=year,exam_type=exam_type, term=term)


# @app.route('/view_students_marks')
# def view_students_marks():
#     teacher_id = session.get('userName')
#     conn = sqlite3.connect("admin.db")
#     cursor = conn.cursor()

#     # Fetch the subjects column for the teacher
#     cursor.execute("SELECT grade FROM teachers WHERE username = ?", (teacher_id,))
#     result = cursor.fetchone()
#     conn.close()

#     if result:
#         subject_numbers = result[0].split(",")  # Convert "4,5,6" to ["4", "5", "6"]
#         grade_list = [class_mapping1[num] for num in subject_numbers if num in class_mapping1]
#         print(grade_list)

#     else:
#         grade_list = {}
#     return render_template('view_students_marks.html', students=database.view_students(grade_list),profile_pic = database.get_profile_t(teacher_id))


# @app.route('/<admission_no>')
# def enter_marks(admission_no):
#     teacher_id = session.get('userName')
#     admission_n = document_functions.replace_slash_with_slash(admission_no)
#     return render_template('type_checker.html', admission_no=admission_no,
#                            first_name=database.get_first_name(admission_n),profile_pic = database.get_profile_t(teacher_id))


# @app.route('/exam_list')
# def students_results():
#     return render_template('exam_list.html', students=database.get_all_students_exams())


# #-------------Upload a Memo
# # Set the directories for file uploads
# BOOKS_FOLDER = 'static/uploads/books/'
# IMAGES_FOLDER = 'static/uploads/images/'
# app.config['BOOKS_FOLDER'] = BOOKS_FOLDER
# app.config['IMAGES_FOLDER'] = IMAGES_FOLDER

# # Ensure the upload folders exist
# os.makedirs(BOOKS_FOLDER, exist_ok=True)
# os.makedirs(IMAGES_FOLDER, exist_ok=True)


# @app.route('/memo')
# def index():
#     # List all uploaded books with their front images
#     books = []
#     for filename in os.listdir(app.config['BOOKS_FOLDER']):
#         image_name = os.path.splitext(filename)[0] + ".jpg"  # Assuming images are uploaded as .jpg
#         image_path = os.path.join(app.config['IMAGES_FOLDER'], image_name)
#         books.append({
#             "filename": filename,
#             "image": image_name if os.path.exists(image_path) else None
#         })
#     return render_template('index.html', books=books)


# @app.route('/upload', methods=['GET', 'POST'])
# def upload():
#     if request.method == 'POST':
#         file = request.files.get('file')
#         image = request.files.get('image')

#         if file and file.filename.endswith('.pdf'):
#             # Save the PDF book
#             filepath = os.path.join(app.config['BOOKS_FOLDER'], file.filename)
#             file.save(filepath)

#             # Save the front image (if provided)
#             if image and image.filename.endswith(('.jpg', '.jpeg', '.png')):
#                 image_name = os.path.splitext(file.filename)[0] + ".jpg"
#                 imagepath = os.path.join(app.config['IMAGES_FOLDER'], image_name)
#                 image.save(imagepath)

#             return redirect(url_for('index'))

#     return render_template('upload.html')
# @app.route('/trainer')
# def trainer():
#     timer=document_functions.copyright_updater()
#     username = session.get('username')
#     username = document_functions.replace_slash_with_dot(username)
#     profile_pic = database.get_aprofile(username)
#     return render_template('trainer.html',timer=timer,profile_pic=profile_pic)

# @app.route('/download/<filename>')
# def download(filename):
#     # Allow users to download the uploaded books
#     return send_from_directory(app.config['BOOKS_FOLDER'], filename, as_attachment=True)


# @app.route('/delete/<filename>', methods=['POST'])
# def delete(filename):
#     # Delete the PDF book and its front image
#     book_path = os.path.join(app.config['BOOKS_FOLDER'], filename)
#     image_name = os.path.splitext(filename)[0] + ".jpg"
#     image_path = os.path.join(app.config['IMAGES_FOLDER'], image_name)

#     if os.path.exists(book_path):
#         os.remove(book_path)
#     if os.path.exists(image_path):
#         os.remove(image_path)

#     return redirect(url_for('index'))


# @app.route('/view_memo')
# def view_memo():
#     books = []
#     for filename in os.listdir(app.config['BOOKS_FOLDER']):
#         image_name = os.path.splitext(filename)[0] + ".jpg"  # Assuming images are uploaded as .jpg
#         image_path = os.path.join(app.config['IMAGES_FOLDER'], image_name)
#         books.append({
#             "filename": filename,
#             "image": image_name if os.path.exists(image_path) else None
#         })
#         admission_no = session.get('admission_no')
#     return render_template("view_memo.html", books=books, profile_pic = database.get_profile(admission_no))



# def load_user_data(username):
#     if os.path.exists('user_data.json'):
#         with open('user_data.json', 'r') as f:
#             try:
#                 data = json.load(f)
#                 return data.get(username, {"username": username, "profile_picture": None})
#             except json.JSONDecodeError:
#                 return {"username": username, "profile_picture": None}
#     else:
#         return {"username": username, "profile_picture": None}


# # Save user data to a JSON file
# def save_user_data(username, user_data):
#     data = {}
#     if os.path.exists('user_data.json'):
#         with open('user_data.json', 'r') as f:
#             try:
#                 data = json.load(f)
#             except json.JSONDecodeError:
#                 pass
#     data[username] = user_data
#     with open('user_data.json', 'w') as f:
#         json.dump(data, f)


# # Route for user profile
# @app.route('/profile', methods=['POST'])
# def profile():
#     admission_no = request.form.get('admission_no')
#     image_file = request.files.get('profile_pic')

#     if image_file:
#         profile1.insert_image('student.db', admission_no, image_file)
#         return redirect(url_for('settings'))
#     else:
#         return "No image selected!", 400

# @app.route('/tprofile', methods=['POST','GET'])
# def tprofile():
#     username = request.form.get('userName')
#     image_file = request.files.get('profile_pic')

#     if image_file:
#         profile1.insert_image_t('admin.db', username, image_file)
#         return redirect(url_for('tsetting'))
#     else:
#         return "No image selected!", 400


# @app.route('/tsetting')
# def tsetting():
#     username = session.get('userName')
#     profile_pic = database.get_profile_t(username)
#     return render_template('tsetting.html',profile_pic=profile_pic, username = username)

# @app.route("/tphone_number_update", methods=['GET', 'POST'])
# def tphone_number_update():
#     phone = request.form['phone']
#     username = session.get('userName')
#     try:
#         with sqlite3.connect('admin.db') as conn:
#             cursor = conn.cursor()
#             cursor.execute('''
#                 UPDATE teachers SET phone = ? WHERE username = ?
#             ''', (phone, username))
#             conn.commit()
#     except sqlite3.Error as e:
#         # Corrected indentation here
#         print("Database error:", e)
#     return redirect(url_for('tsetting'))


# @app.route("/temail_update", methods=['GET', 'POST'])
# def temail_update():
#     email = request.form['email']
#     username = session.get('userName')
#     with sqlite3.connect('admin.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#         UPDATE teachers SET email = ? WHERE username = ?
#                       ''',(email,username))
#         conn.commit()
#     return redirect(url_for('tsetting'))


# @app.route('/compiler')
# def compiler():
#     return render_template('compiler.html')


# @app.route('/manager')
# def manager():
#     return render_template('manager.html')


# @app.route('/dash')
# def dashb():
#     admission_no = session.get('admission_no')
#     # Get the profile picture from session or set a default one
#     profile_picture = session.get('profile_picture', 'person1.png')
#     username = request.args.get('username')
#     user_data = load_user_data(username)
#     admission=document_functions.replace_slash_with_dot(admission_no)
#     if request.method == 'POST':
#         if 'profile_picture' in request.files:
#             profile_picture = request.files['profile_picture']
#             if profile_picture.filename != '':
#                 profile_pic_path = f'static/uploads/{username}_profile_picture.jpg'
#                 profile_picture.save(profile_pic_path)
#                 user_data['profile_picture'] = profile_pic_path
#                 save_user_data(username, user_data)

#     return render_template('dashboard.html', profile_picture=user_data['profile_picture'],admission_no=admission)



# @app.route('/students_with_balance')
# def students_with_balance():
#     students = database.get_students_with_balance()
#     return render_template('students_with_balance.html', students=students)


# #===============Add Student
# @app.route('/add_or_remove')
# def add_or_remove_student():
#     return render_template("add_or_remove_student.html")

# @app.route('/add_remove_teacher')
# def a_or_r():
#     return render_template("add_or_remove_teacher.html")

# @app.route('/add_student')
# def add():
#     return render_template('add_student.html')


# @app.route('/signup_success')
# def signup_success():
#     return render_template('signup_success.html')


# @app.route('/submit_signup', methods=['POST'])
# def submit_signup():
#     first_name = request.form['first_name'].upper()
#     middle_name = request.form['middle_name'].upper()
#     last_name = request.form['last_name'].upper()
#     age = request.form['age']
#     gender = request.form['gender']
#     grade = request.form['grade']
#     sickness = request.form['sickness'].capitalize()
#     treatment = request.form['treatment'].capitalize()
#     admission_no = request.form['admission_no']
#     phone = request.form['phone']
#     email = request.form['email']
#     existing_student = database.student_exist(admission_no)
#     existing_email = database.student_email_exists(admission_no)
#     if existing_student:
#         # Admission number already exists
#         flash("Error: A student with this admission number already exists.", "error")
#         return redirect(url_for('index'))
#     if existing_email:
#         flash("Student with the same email exists try to login")
#         return redirect(url_for('index'))

#     database.add_someone(admission_no, first_name, middle_name, last_name, gender, age, email)
#     database.add_level(admission_no, grade,phone,datetime.now())
#     database.put_ill_students(admission_no, sickness, treatment)
#     database.add_login(admission_no, last_name)
#     sender_email = "richardkeith233@gmail.com"
#     sender_password = "mnoj wsox aumw tkrs"  # Use App Password if 2FA is enabled
#     recipient_email = email
#     password2 = last_name

#     subject = "Chuka University"
#     body = f"Welcome and feel at home your last name will be your default password: {password2}, Your admission number: {admission_no}"

#     send_mail1.send_email(sender_email,recipient_email, sender_password, password2, subject, body)
#     return redirect(url_for('signup_success'))

# #=================Send mail



# #=================Non Compliant Student
# @app.route('/non_compliant_students')
# def non_compliant_students():
#     students = database.non_compliant_students()
#     return render_template('non_compliant_students.html', students=students)


# #===============Ill Students
# @app.route('/health_issue')
# def health_issue():
#     students = database.get_ill_students()
#     return render_template('health_issue.html', students=students)
# #================Add Health issue Student==========
# #================Remove Health issue Student=============
# #================View all registered students=============
# def all_students():
#     with sqlite3.connect('student.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#         SELECT students.admission_no, students.first_name, students.last_name, rest.phone_number, rest.Grade
#         FROM students
#         JOIN rest ON students.admission_no = rest.admission_no
#         ORDER BY rest.Grade ASC
#         ''')
#         result = cursor.fetchall()
#         return result

# @app.route('/all_teacher',  methods=['GET','POST'])
# def all_teacher():
#     with sqlite3.connect('admin.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#         SELECT admin_data.position, admin_data.f_name, admin_data.l_name, teachers.grade, teachers.subject
#         FROM admin_data
#         JOIN teachers ON admin_data.position = teachers.username
#         ORDER BY admin_data.position ASC
#         ''')
#         result = cursor.fetchall()
#         return result


# @app.route("/phone_number_update", methods=['GET', 'POST'])
# def phone_number_update():
#     phone = request.form['phone']
#     admission_no = session.get('admission_no')
#     with sqlite3.connect('student.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#         UPDATE rest SET phone_number = ? WHERE admission_no = ?
#                        ''',(phone,admission_no))
#         conn.commit()
#     return redirect(url_for('settings'))

# @app.route("/email_update", methods=['GET', 'POST'])
# def email_update():
#     email = request.form['email']
#     admission_no = session.get('admission_no')
#     with sqlite3.connect('student.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#         UPDATE students SET email = ? WHERE admission_no = ?
#                        ''',(email,admission_no))
#         conn.commit()
#     return redirect(url_for('settings'))

# @app.route('/registered_students')
# def registered():
#     students = all_students()
#     return render_template('registered_students.html',students=students)

# @app.route('/registered_teachers')
# def registered1():
#     teachers = all_teacher()
#     return render_template('registered_teachers.html',teachers = teachers)



# #======================Fee Payment==============================================



# def get_student_data(admission_number):
#     conn = sqlite3.connect('fees.db')
#     cursor = conn.cursor()
#     cursor.execute('SELECT total_paid, remaining_balance FROM students WHERE admission_number = ?', (admission_number,))
#     result = cursor.fetchone()
#     conn.close()
#     return result if result else (0, TOTAL_FEES)





# # Function to get student data by either admission number or name
# def get_student_by_admission_or_name(identifier):
#     conn = sqlite3.connect('student.db')
#     cursor = conn.cursor()

#     # Check if identifier is a valid admission number or name
#     cursor.execute('''
#         SELECT admission_no FROM students
#         WHERE admission_no = ? OR (first_name || ' ' || last_name) = ?
#     ''', (identifier, identifier))

#     result = cursor.fetchone()
#     conn.close()

#     if result:
#         return result[0]  # Return admission number
#     else:

#         return None


# # Updated function to handle name or admission number and fee update
# def update_student_fees(identifier, amount_paid):
#     # Check if the identifier is an admission number or full name
#     admission_number = get_student_by_admission_or_name(identifier)

#     if admission_number is None:
#         return "Student not found"

#     conn = sqlite3.connect('fees.db')
#     cursor = conn.cursor()

#     # Get the previous total paid and remaining balance
#     previous_total_paid, _ = get_student_data(admission_number)
#     total_paid = previous_total_paid + amount_paid
#     remaining_balance = document_functions.current_fee() - total_paid

#     # Update the students' fee data
#     cursor.execute('''
#         INSERT INTO students (admission_number, total_paid, remaining_balance)
#         VALUES (?, ?, ?)
#         ON CONFLICT(admission_number)
#         DO UPDATE SET total_paid = excluded.total_paid, remaining_balance = excluded.remaining_balance
#     ''', (admission_number, total_paid, remaining_balance))

#     # Record the transaction in the payment_histo
#     import pytz
#     nairobi_tz = pytz.timezone('Africa/Nairobi')
#     nairobi_time = datetime.now(nairobi_tz)
#     date_time = nairobi_time.strftime('%Y-%m-%d %H:%M:%S')

#     cursor.execute('''
#         INSERT INTO payment_history (admission_number, amount_paid, remaining_balance, date_time)
#         VALUES (?, ?, ?, ?)
#     ''', (admission_number, amount_paid, remaining_balance, date_time))

#     conn.commit()
#     conn.close()

#     return total_paid, remaining_balance



# def get_payment_history(admission_number):
#     conn = sqlite3.connect('fees.db')
#     cursor = conn.cursor()
#     cursor.execute('SELECT amount_paid, remaining_balance, date_time FROM payment_history WHERE admission_number = ?', (admission_number,))
#     history = cursor.fetchall()
#     conn.close()
#     return history

# @app.route('/fee_payment', methods=['GET','POST'])
# def index1():
#     # admission_no = get_student_by_admission_or_name(request.form['admissionNumber'])
#     # admission_no = document_functions.replace_slash_with_dot(admission_no)
#     return render_template('fees_payment.html' )

# @app.route('/submit', methods=['POST'])
# def submit():
#     admission_number = request.form['admissionNumber']
#     fee_paid = float(request.form['feePaid'])

#     total_paid, remaining_balance = update_student_fees(admission_number, fee_paid)

#     return jsonify({
#         'total_paid': total_paid,
#         'remaining_balance': remaining_balance
#     })

# @app.route('/receipt/<admission_no>', methods=['GET'])
# def download_receipt(admission_no):
#     admission_number = document_functions.replace_slash_with_slash(admission_no)
#     total_paid, remaining_balance = get_student_data(admission_number)

#     # Generate PDF receipt
#     buffer = io.BytesIO()
#     pdf = SimpleDocTemplate(buffer, pagesize=A4)

#     # Styles
#     styles = getSampleStyleSheet()
#     title_style = styles['Title']
#     normal_style = styles['Normal']

#     # Receipt content
#     elements = []

#     # Title
#     title = Paragraph(
#         f"Payment Receipt for Admission Number: {document_functions.replace_slash_with_slash(admission_number)}",
#         title_style)
#     elements.append(title)

#     # Spacer
#     elements.append(Paragraph("<br/><br/>", normal_style))

#     # Receipt table data
#     data = [
#         ["Description", "Amount (sh)"],
#         ["Total Paid", f"{total_paid}"],
#         ["Remaining Balance", f"{remaining_balance}"]
#     ]

#     # Create a table with a custom style
#     table = Table(data, colWidths=[3 * inch, 2 * inch])
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))

#     elements.append(table)

#     # Spacer
#     elements.append(Paragraph("<br/><br/>", normal_style))

#     # Thank you message
#     thank_you = Paragraph("Thank you for your payment.", normal_style)
#     elements.append(thank_you)

#     # Build PDF
#     pdf.build(elements)

#     buffer.seek(0)
#     return send_file(buffer, as_attachment=True, download_name=f"receipt_{admission_number}.pdf",
#                      mimetype='application/pdf')

# @app.route('/history', methods=['GET'])
# def view_history():
#     admission_number = session.get('admission_no')
#     admission_number = document_functions.replace_slash_with_slash(admission_number)
#     history = get_payment_history(admission_number)
#     return render_template('payment_history.html', history=history, admission_number=document_functions.replace_slash_with_dot(admission_number), profile_pic=database.get_profile(admission_number))

# @app.route('/download_history', methods=['GET'])
# def download_history():
#     admission_number = session.get('admission_no')

#     # Fetch payment history
#     history = get_payment_history(document_functions.replace_slash_with_slash(admission_number))

#     # Create buffer
#     buffer = io.BytesIO()

#     # Create a PDF document using SimpleDocTemplate
#     pdf = SimpleDocTemplate(buffer, pagesize=A4)

#     # Container for the elements in the PDF
#     elements = []

#     # Add a title
#     styles = getSampleStyleSheet()
#     title = Paragraph(f"Payment History for : {database.get_first_name( admission_number)} {database.get_middle_name(admission_number)} {database.get_last_name(admission_number)}", styles['Title'])
#     elements.append(title)

#     # Table data (headers)
#     data = [['Amount Paid', 'Remaining Balance', 'Date & Time']]

#     # Table data (rows)
#     for amount_paid, remaining_balance, date_time in history:
#         data.append([f"sh.{amount_paid}", f"sh.{remaining_balance}", date_time])

#     # Create a table
#     table = Table(data)

#     # Apply table style
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background color
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
#         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#         ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))

#     # Add table to elements
#     elements.append(table)

#     # Build the PDF
#     pdf.build(elements)

#     # Return PDF file
#     buffer.seek(0)
#     return send_file(buffer, as_attachment=True, download_name=f"payment_history_{admission_number}.pdf",
#                      mimetype='application/pdf')


# #=====================Delete Student
# def get_db_connection():
#     conn = sqlite3.connect('student.db')
#     conn.row_factory = sqlite3.Row
#     return conn

# # Route to render the HTML page


# # API to fetch all students from the database
# @app.route('/all_students', methods=['GET','POST'])
# def get_students():
#     conn = get_db_connection()
#     students = conn.execute('''
#     SELECT students.admission_no, students.first_name, students.last_name, rest.Grade
#     FROM students
#     JOIN rest ON students.admission_no = rest.admission_no
#     ''').fetchall()
#     conn.close()

#     student_list = [{'admission_no': document_functions.replace_slash_with_dot(student['admission_no']), 'first_name': student['first_name'], 'last_name':student['last_name'],'grade':student['Grade']} for student in students]
#     return jsonify(student_list)

# @app.route('/all_teachers',  methods=['GET','POST'])
# def all_teachers():
#     with sqlite3.connect('admin.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#         SELECT admin_data.position, admin_data.f_name, admin_data.l_name, teachers.grade, teachers.subject
#         FROM admin_data
#         JOIN teachers ON admin_data.position = teachers.username
#         ORDER BY admin_data.position ASC
#         ''')
#         result = cursor.fetchall()

#     # Convert result to a list of dictionaries
#     teachers_list = [
#         {
#             "username": row[0],
#             "f_name": row[1],
#             "l_name": row[2],
#             "grade": row[3],
#             "subject": row[4]
#         }
#         for row in result
#     ]

#     return jsonify(teachers_list)  # Ensure the response is JSON-formatted


# # API to delete a student by ID
# @app.route('/delete_student/<admission_no>', methods=['DELETE','POST'])
# def delete_student(admission_no):
#     admission = document_functions.replace_slash_with_slash(admission_no)
#     database.delete_student(admission)
#     return jsonify({'success': True})

# @app.route('/delete_teacher/<username>', methods=['DELETE','POST'])
# def delete_teacher(username):
#     database.delete_teacher(username)
#     return jsonify({'success': True})
# #===============Change Password
# @app.route('/change_password', methods=['GET', 'POST'])
# def change_password():
#     admission_number = session.get('admission_no')
#     if request.method == 'POST':
#         # Get form data
#         admission_no = session.get('admission_no')  # Example admission number, ideally you'd get this from session or another source
#         current_password = request.form['current_password']
#         new_password = request.form['new_password']
#         confirm_password = request.form['confirm_password']

#         # Connect to the database
#         conn = sqlite3.connect('student.db')
#         cursor = conn.cursor()

#         # Check if current password is correct
#         cursor.execute("SELECT password FROM logins WHERE admission_no = ?", (admission_no,))
#         result = cursor.fetchone()

#         if result and result[0] == current_password:
#             # Check if the new password and confirmation match
#             if new_password == confirm_password:
#                 # Update the password in the logins table
#                 cursor.execute("UPDATE logins SET password = ? WHERE admission_no = ?", (new_password, admission_no))
#                 conn.commit()
#                 flash('Password changed successfully!', 'success')
#                 return redirect(url_for('home'))
#             else:
#                 flash('New password and confirmation do not match.', 'error')
#         else:
#             flash('Current password is incorrect.', 'error')

#         conn.close()
#     return render_template('change_password.html',profile_pic = database.get_profile(admission_number))

# @app.route('/change_manager_password', methods=['GET', 'POST'])
# def manager_password():
#     if request.method == 'POST':
#         # Get form data
#         admission_no = session.get('username')  # Example admission number, ideally you'd get this from session or another source
#         current_password = request.form['current_password']
#         new_password = request.form['new_password']
#         confirm_password = request.form['confirm_password']

#         # Connect to the database
#         conn = sqlite3.connect('manager.db')
#         cursor = conn.cursor()

#         # Check if current password is correct
#         cursor.execute("SELECT password FROM logins WHERE username = ?", (admission_no,))
#         result = cursor.fetchone()

#         if result and result[0] == current_password:
#             # Check if the new password and confirmation match
#             if new_password == confirm_password:
#                 # Update the password in the logins table
#                 cursor.execute("UPDATE logins SET password = ? WHERE username = ?", (new_password, admission_no))
#                 conn.commit()
#                 flash('Password changed successfully!', 'success')
#                 print('password changed successfully')
#                 return redirect('/add_or_remove')
#             else:
#                 flash('New password and confirmation do not match.', 'error')
#                 print('passwords dont match')
#         else:
#             flash('Current password is incorrect.', 'error')
#             print('current password is incorrect')

#         conn.close()
#     return render_template('manager_password.html')

# #==================Developer portal
# UPLOAD_FOLDER = 'static/images'
# FIXED_FILENAME = 'your_uploaded_image.jpg'

# # Configure upload folder
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Ensure the upload folder exists
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# @app.route('/developer')
# def developer():
#     return render_template('developer.html')

# @app.route('/upload_image', methods=['POST'])
# def upload_file():
#     if 'image' not in request.files:
#         return "No file part"

#     file = request.files['image']

#     if file.filename == '':
#         return "No selected file"

#     if file:
#         # Use the fixed filename for the uploaded image
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], FIXED_FILENAME)
#         file.save(file_path)
#         return f'Image successfully uploaded and saved as {FIXED_FILENAME}'
# #===============================Exam Results
# def view_student_marks():
#     admission_no = session.get('admission_no')
#     with sqlite3.connect('student.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#         SELECT * FROM marks
#         WHERE admission_no = ?
#         ''',(admission_no,))
#     result = cursor.fetchall()
#     return result


# def view_student_marks2(admission_no, enrolled_subjects=None):
#     """Get student marks with unpacked subjects for template rendering, filtered to enrolled subjects only."""
#     if enrolled_subjects is None:
#         enrolled_subjects = []

#     with sqlite3.connect('student.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute('''
#         SELECT id, admission_no, year, term, exam_type, marks_json, average
#         FROM marks
#         WHERE admission_no = ?
#         ORDER BY year DESC, term DESC
#         ''',(admission_no,))
#         rows = cursor.fetchall()

#     result = []
#     for row in rows:
#         row_id, adm, year, term, exam_type, marks_json, avg = row
#         try:
#             marks = json.loads(marks_json) if marks_json else {}
#         except (json.JSONDecodeError, ValueError):
#             marks = {}

#         # Build tuple with only enrolled subjects (dynamic length based on actual enrollment)
#         subject_marks = tuple(marks.get(subj, '-') for subj in enrolled_subjects)
#         avg_val = avg if avg is not None else '-'

#         # Format: (id, year, term, exam_type, ...enrolled_subject_marks, avg)
#         # Subjects are in the order from enrolled_subjects list
#         result.append((row_id, year, term, exam_type) + subject_marks + (avg_val,))

#     return result
# #===========================================Change Student Logins
# @app.route('/students_logins', methods=['GET', 'POST'])
# def show_students():
#     conn = sqlite3.connect('student.db')
#     cursor = conn.cursor()

#     email, name, last_name = None, None, None  # Default values

#     # Check if it's a POST request to update a password
#     if request.method == 'POST':
#         admission_number = request.form['admission_number']
#         new_password = request.form['new_password']

#         # Update the password in the logins table; insert if missing
#         cursor.execute("SELECT 1 FROM logins WHERE admission_no = ?", (admission_number,))
#         if cursor.fetchone():
#             cursor.execute("UPDATE logins SET password = ? WHERE admission_no = ?", (new_password, admission_number))
#         else:
#             cursor.execute("INSERT INTO logins (admission_no, password) VALUES (?, ?)", (admission_number, new_password))
#         conn.commit()

#         # Fetch the email, first name, and last name for the given admission number
#         cursor.execute("SELECT email, first_name, last_name FROM students WHERE admission_no = ?", (admission_number,))
#         result = cursor.fetchone()

#         if result:
#             email, name, last_name = result  # Unpacking the tuple

#             # Send Email Notification
#             sender_email = "richardkeith233@gmail.com"
#             sender_password = "mnoj wsox aumw tkrs"  # Use an App Password if 2FA is enabled
#             recipient_email = email

#             subject = "Crimsons Student Portal"
#             body = f"Hello {name},\n\nWe regret to inform you that your password has been updated by the Administration panel. Please confirm with the administration."

#             send_mail1.send_email(sender_email, recipient_email, sender_password, last_name, subject, body)

#     # Server-side search + pagination support
#     q = request.args.get('q', '')
#     # pagination params
#     try:
#         page = int(request.args.get('page', 1))
#     except (TypeError, ValueError):
#         page = 1
#     if page < 1:
#         page = 1
#     per_page = 20
#     offset = (page - 1) * per_page

#     if q:
#         like_q = f"%{q}%"
#         # total count for matched rows
#         cursor.execute('''
#             SELECT COUNT(*)
#             FROM students
#             LEFT JOIN logins ON students.admission_no = logins.admission_no
#             WHERE students.admission_no LIKE ? OR students.first_name LIKE ? OR students.last_name LIKE ?
#         ''', (like_q, like_q, like_q))
#         total = cursor.fetchone()[0]

#         # fetch paginated matched rows
#         cursor.execute('''
#             SELECT students.admission_no, students.first_name, students.last_name, logins.password
#             FROM students
#             LEFT JOIN logins ON students.admission_no = logins.admission_no
#             WHERE students.admission_no LIKE ? OR students.first_name LIKE ? OR students.last_name LIKE ?
#             ORDER BY students.rowid DESC
#             LIMIT ? OFFSET ?
#         ''', (like_q, like_q, like_q, per_page, offset))
#     else:
#         # total count for all rows
#         cursor.execute('''
#             SELECT COUNT(*)
#             FROM students
#             LEFT JOIN logins ON students.admission_no = logins.admission_no
#         ''')
#         total = cursor.fetchone()[0]

#         # fetch paginated rows
#         cursor.execute('''
#             SELECT students.admission_no, students.first_name, students.last_name, logins.password
#             FROM students
#             LEFT JOIN logins ON students.admission_no = logins.admission_no
#             ORDER BY students.rowid DESC
#             LIMIT ? OFFSET ?
#         ''', (per_page, offset))

#     students = cursor.fetchall()
#     # normalize missing passwords to empty string for display
#     students = [(s[0], s[1], s[2], s[3] if s[3] is not None else '') for s in students]
#     conn.close()

#     # compute pagination metadata
#     total_pages = max(1, (total + per_page - 1) // per_page)

#     # Pass back the query and pagination info so the template can render controls
#     return render_template('students_logins.html', students=students, q=q, page=page, total_pages=total_pages)
# #=====================Update fee balances for each student
# # Route to display the HTML form
# @app.route('/fee_update_success')
# def f_success():
#     return render_template('update_fee_success.html')
# @app.route('/set_fee', methods=['GET', 'POST'])
# def set_fee():
#     if request.method == 'POST':
#         # Get fee values from form submission
#         term1_fee = request.form['term1']
#         term2_fee = request.form['term2']
#         term3_fee = request.form['term3']

#         # Update the database with new fees
#         conn = sqlite3.connect('fees.db')
#         cursor = conn.cursor()
#         cursor.execute('UPDATE fee SET amount = ? WHERE term = ?', (term1_fee, 1))
#         cursor.execute('UPDATE fee SET amount = ? WHERE term = ?', (term2_fee, 2))
#         cursor.execute('UPDATE fee SET amount = ? WHERE term = ?', (term3_fee, 3))

#         # Commit changes and close the connection
#         conn.commit()
#         conn.close()

#         with sqlite3.connect('fees.db') as conn:
#             cursor = conn.cursor()
#             cursor.execute('''
#             SELECT amount FROM fee
#             ''')
#             data = cursor.fetchall()
#         with sqlite3.connect('fees.db') as conn:
#             cursor = conn.cursor()
#             cursor.execute('''
#             SELECT term FROM fee
#             ''')
#             terms = cursor.fetchall()
#             #===Determine the current time
#             current_month = datetime.now().month

#             # Determine the fee based on the month
#             if current_month in [1, 2, 3, 4]:
#                 current_fee = data[0][0]
#                 term = terms[0][0]
#             elif current_month in [5, 6, 7, 8]:
#                 current_fee = data[1][0]
#                 term = terms[1][0]
#             elif current_month in [9, 10, 11, 12]:
#                 current_fee = data[2][0]
#                 term = terms[2][0]
#             else:
#                 raise ValueError("Invalid month encountered.")

#             # Connect to the SQLite database
#             with sqlite3.connect('fees.db') as conn:
#                 cursor = conn.cursor()
#                 cursor.execute('''
#                     UPDATE current_fees SET term = ? , amount = ?
#                 ''', (term, current_fee))
#                 print('Data set sucessfuly')
#                 conn.commit()

#         return redirect(url_for('f_success'))

#     # Render the HTML form on GET request
#     students = database.fee_data()

#     return render_template('set_fee.html',students=students)

# # Update student balances based on the current term
# @app.route('/update_balances',  methods=['GET', 'POST'])
# def update_balances():
#     if request.method == 'POST':
#         fee_amount = request.form['fee_amount']
#         with sqlite3.connect('fees.db') as conn:
#             cursor = conn.cursor()
#             cursor.execute('''
#             SELECT amount FROM fee
#             ''')
#             data = cursor.fetchall()
#         with sqlite3.connect('fees.db') as conn:
#             cursor = conn.cursor()
#             cursor.execute('''
#             SELECT term FROM fee
#             ''')
#             terms = cursor.fetchall()
#             #===Determine the current time
#             current_month = datetime.now().month

#             # Determine the fee based on the month
#             if current_month in [1, 2, 3, 4]:
#                 current_fee = data[0][0]
#                 term = terms[0][0]
#             elif current_month in [5, 6, 7, 8]:
#                 current_fee = data[1][0]
#                 term = terms[1][0]
#             elif current_month in [9, 10, 11, 12]:
#                 current_fee = data[2][0]
#                 term = terms[2][0]
#             else:
#                 raise ValueError("Invalid month encountered.")

#             # Connect to the SQLite database
#             with sqlite3.connect('fees.db') as conn:
#                 cursor = conn.cursor()
#                 cursor.execute('''
#                     UPDATE current_fees SET term = ? , amount = ?
#                 ''', (term, current_fee))
#                 print('Data set sucessfuly')
#                 conn.commit()


#         with sqlite3.connect('fees.db') as conn:
#             cursor = conn.cursor()

#             # Get the fee for the current term
#             cursor.execute('SELECT amount FROM current_fees')
#             fees = cursor.fetchone()

#             if not fees:
#                 return jsonify({'message': 'No fee set for this term'}), 400

#             fee_amount = fees[0]

#             # Update each student's balance
#             cursor.execute('UPDATE students SET remaining_balance = remaining_balance + ?', (fee_amount,))

#             conn.commit()

#         return redirect(url_for('f_success'))
#     return render_template('update_balances.html',fee_amount=document_functions.c_fee())

# @app.route('/add-student', methods=['POST'])
# def add_student():
#     first_name = request.form['first_name'].upper()
#     last_name = request.form['last_name'].upper()
#     admission_no = database.get_admission_number(first_name, last_name)
#     sickness = request.form['sickness']
#     treatment = request.form['treatment']

#     # Add to the database
#     with sqlite3.connect('student.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute("""
#             INSERT INTO ill_students (admission_no,  sick, description)
#             VALUES (?, ?, ?)
#         """, (admission_no, sickness, treatment))
#         conn.commit()

#     return redirect('/health_issue')

# @app.route('/delete-student/<admission_no>', methods=['POST'])
# def delete_ill_student(admission_no):
#     admission_number =document_functions.replace_slash_with_slash(admission_no)
#     # Remove the student from the database
#     with sqlite3.connect('student.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute("DELETE FROM ill_students WHERE admission_no = ?", (admission_number,))
#         conn.commit()

#     return redirect('/health_issue')
# @app.route('/add-student3', methods=['POST'])
# def add_student_ncs():
#     admission_no = request.form['admission_no']
#     reason = request.form['reason'].capitalize()
#     duration = request.form['duration']
#     send_date = request.form['send_date']
#     return_date = request.form['return_date']
#     status = 'pending'

#     with sqlite3.connect('student.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute("""
#             INSERT INTO non_compliant (admission_no, send_date, return_date, status, duration, reason, status)
#             VALUES (?, ?, ?, ?, ?, ?, ?)
#         """, (admission_no,  send_date, return_date, status, duration, reason, status))
#         conn.commit()

#     return redirect('/non_compliant_students')

# @app.route('/delete-student1/<admission_no>', methods=['POST'])
# def delete_student_ncs(admission_no):
#     with sqlite3.connect('student.db') as conn:
#         admission_number=document_functions.replace_slash_with_slash(admission_no)
#         cursor = conn.cursor()
#         cursor.execute("DELETE FROM non_compliant WHERE admission_no = ?", (admission_number,))
#         conn.commit()

#     return redirect('/non_compliant_students')


# @app.route('/update-status/<admission_no>', methods=['POST'])
# def update_status(admission_no):
#     admission_number=document_functions.replace_slash_with_slash(admission_no)
#     new_status = request.form['status']

#     with sqlite3.connect('student.db') as conn:
#         cursor = conn.cursor()
#         cursor.execute("""
#             UPDATE non_compliant
#             SET status = ?
#             WHERE admission_no = ?
#         """, (new_status, admission_number))
#         conn.commit()

#     return redirect('/non_compliant_students')

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Function to get access token
# def get_access_token():
#     consumer_key = "twd2Fk9toBVjeGi67JCCfEqh0uB7OJPXNiA63g44ek3dpskP"
#     consumer_secret = "9lXIcf6er5THdG7DAZWpv8sGeiXyEziH13RuTmuFVGAWhAJxB6LqPWMHUbrWFnx2"
#     endpoint = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

#     response = requests.get(endpoint, auth=HTTPBasicAuth(consumer_key, consumer_secret))
#     if response.status_code == 200:
#         return response.json().get("access_token")
#     else:
#         logger.error(f"Error generating token: {response.text}")
#         return None

# @app.route('/pay_myfees')
# def my_fee_payment():
#     admission_no = session.get('admission_no')
#     return render_template('pay_fees.html', profile_pic=database.get_profile(admission_no))

# # M-Pesa API Credentials
# CONSUMER_KEY = "twd2Fk9toBVjeGi67JCCfEqh0uB7OJPXNiA63g44ek3dpskP"
# CONSUMER_SECRET = "9lXIcf6er5THdG7DAZWpv8sGeiXyEziH13RuTmuFVGAWhAJxB6LqPWMHUbrWFnx2"
# BUSINESS_SHORT_CODE = "174379"
# PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
# CALLBACK_URL = "https://crimsons.pythonanywhere.com/mpesa_callback"


# @app.route("/pay_fees", methods=['GET', 'POST'])
# def stk_push():
#     phone = request.form["phone"]
#     if phone.startswith("0"):
#         phone = "254" + phone[1:]  # Convert 0712345678 to 254712345678
#     amount = request.form["amount"]
#     access_token = get_access_token()
#     print("Access Token:", access_token)

#     if not access_token:
#         return jsonify({"error": "Failed to get access token"})

#     timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
#     password = base64.b64encode((BUSINESS_SHORT_CODE + PASSKEY + timestamp).encode()).decode()

#     stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
#     headers = {
#             'Content-Type': 'application/json',
#             'Authorization': f'Bearer {access_token}'
#         }
#     payload = {
#         "BusinessShortCode": BUSINESS_SHORT_CODE,
#         "Password": password,
#         "Timestamp": timestamp,
#         "TransactionType": "CustomerPayBillOnline",
#         "Amount": amount,
#         "PartyA": phone,
#         "PartyB": BUSINESS_SHORT_CODE,
#         "PhoneNumber": phone,
#         "CallBackURL": CALLBACK_URL,
#         "AccountReference": "account_reference",
#         "TransactionDesc": "Fees payment"
#     }

#     response = requests.post(stk_url, json=payload, headers=headers)
#     print("STK Push Response:", response.json())  # Debugging
#     if response.status_code == 200:
#         return jsonify({"status": "success", "message": "Payment in progress"})
#     else:
#         return jsonify({"status": "failure", "message": response.text}), response.status_code
#     return jsonify(response.json())


# # Callback listener to handle the result from Safaricom

# @app.route("/mpesa_callback", methods=["POST","GET"])
# def mpesa_callback():
#     print("Hello  callback!!1")
#     data = request.get_json()
#     print("Hello  callback!!")
#     if data and "Body" in data and "stkCallback" in data["Body"]:
#         callback = data["Body"]["stkCallback"]
#         result_code = callback["ResultCode"]
#         transaction_id = callback.get("CheckoutRequestID", None)

#         # Determine payment status
#         status = "Fail" if result_code != 0 else "Success"


#         print(f'payment is a {status}')

#         # if "CallbackMetadata" in callback:
#         #     for item in callback["CallbackMetadata"]["Item"]:
#         #         if item["Name"] == "PhoneNumber":
#         #             phone_number = item["Value"]
#         #         if item["Name"] == "Amount":  # Extracting Amount
#         #             amount = item["Value"]
#         #         admission_no = session.get('admission_no')
#         # print(f'{phone_number} paid {amount} of adimission_no {admission_no}')
#         return redirect('/trainer')

#     return jsonify({"error": "Invalid callback data"}), 400
# #import pywhatkit

# @app.route('/send_message', methods=['GET','POST'])
# def whatsapp():
#     try:

#         phone = "+254110385662"
#         message = "Hello, I hope this message finds you well. I have a query. Please assist me."

#         pywhatkit.sendwhatmsg_instantly(phone, message)  # Short wait time
#         return redirect('/trainer')

#     except Exception as e:
#         return f"Error: {e}"
# @app.route('/teacher_signup')
# def signup_form():
#     return render_template('teachers_signup.html')

# @app.route('/signup', methods=['GET','POST'])
# def signup():
#     username = request.form['username']
#     f_name = request.form['fname']
#     m_name = request.form['mname']
#     l_name = request.form['lname']
#     password = request.form['lname']
#     gender = request.form['gender']
#     age = request.form['age']
#     id_number = request.form['id-number']



#     email = request.form['email']
#     phone = request.form['phone']
#     grade = request.form['grade']
#     subject = request.form['subject']
#     date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#     conn = sqlite3.connect('admin.db')
#     cursor = conn.cursor()
#     cursor.execute('INSERT INTO teachers (username, email, phone, grade, subject, date) VALUES (?, ?, ?, ?, ?, ?)',
#                    (username, email, phone, grade, subject, date))
#     conn.commit()
#     cursor.execute('INSERT INTO logins(position, password) VALUES(?, ?)',(username, password))
#     conn.commit()
#     cursor.execute(
#     'INSERT INTO admin_data (position, f_name, m_name, l_name, gender, age, id_number) VALUES (?, ?, ?, ?, ?, ?, ?)',
#     (username, f_name, m_name, l_name, gender, age, id_number))

#     conn.commit()
#     conn.close()
#     sender_email = "richardkeith233@gmail.com"
#     sender_password = "mnoj wsox aumw tkrs"  # Use App Password if 2FA is enabled
#     recipient_email = email
#     password2 = l_name

#     subject = "Crimsons portal"
#     body = f"Welcome teacher {f_name} {l_name} and feel at home your last name will be your default password: {password2} and Username: {username}"

#     send_mail1.send_email(sender_email,recipient_email, sender_password, password2, subject, body)

#     return "Teacher Signup Successful!"

# @app.route('/delete_students', methods=['GET','POST'])
# def delete_students():
#     return render_template('students.html')

# @app.route('/delete_teachers', methods=['GET','POST'])
# def delete_teachers():
#     return render_template('teachers.html')

# @app.route('/forgot_password1')
# def forgot_password1():
#     return render_template("forgot_password.html")
# @app.route('/forgot_password', methods=['GET', 'POST'])
# def forgot_password():

#     email = request.form['email']
#     student_email = database.get_emails('student.db','students','email')
#     admin_email = database.get_emails('manager.db', 'manager', 'email')
#     teacher_email = database.get_emails('admin.db','teachers', 'email' )
#     users = student_email + admin_email + teacher_email
#     default_password = None
#     if email in users:
#         if email in student_email:
#             default_password = database.get_password_s('student.db', email)
#         elif email in admin_email:
#             default_password = database.get_password_m('manager.db', email)
#         elif email in teacher_email:
#             default_password = database.get_password_t('admin.db', email)

#              # You can generate a random one

#         sender_email = "richardkeith233@gmail.com"
#         sender_password = "mnoj wsox aumw tkrs"
#         subject = "Password Reset"

#         body = f"Your new password is: {default_password}. Please log in and change it."

#         send_mail1.forgot_m_pass(sender_email,sender_password, email, subject, body)
#             # Send email

#     return redirect(url_for('password_reset'))
# @app.route("/password_reset")
# def password_reset():
#     return render_template("password_reset.html")

# if __name__ == '__main__':
#     if not os.path.exists('static/uploads'):
#         os.makedirs('static/uploads')
#     database.add_all_tables()
#     app.run(debug=True)
