import sqlite3

DB_NAME = "manager.db"

# def clear_tables():
#     try:
#         conn = sqlite3.connect(DB_NAME)
#         cursor = conn.cursor()

#         # Delete all records
#         cursor.execute("DELETE FROM logins;")
#         cursor.execute("DELETE FROM manager;")

        
        
#         conn.commit()
#         print("✅ All data cleared from logins and managers tables.")

#     except sqlite3.Error as e:
#         print("❌ Database error:", e)

#     finally:
#         if conn:
#             conn.close()

# if __name__ == "__main__":
#     confirm = input(
#         "⚠️ This will permanently delete ALL data from logins and managers tables.\n"
#         "Type YES to continue: "
#     )

#     if confirm == "YES":
#         clear_tables()
#     else:
#         print("❎ Operation cancelled.")
# def clear_students():
#     try:
#         conn = sqlite3.connect(DB_NAME)
#         cursor = conn.cursor()

#         # Delete all records
#         cursor.execute("DELETE FROM students;")
#         cursor.execute("DELETE FROM attendance;")
#         cursor.execute("DELETE FROM ill_students;")
#         cursor.execute("DELETE FROM marks;")
#         cursor.execute("DELETE FROM assignments;")
#         cursor.execute("DELETE FROM fees;")
#         cursor.execute("DELETE FROM rest;")
#         cursor.execute("DELETE FROM logins;")
#         cursor.execute("DELETE FROM average;")
#         cursor.execute("DELETE FROM Examinations;")
#         cursor.execute("DELETE FROM fees_student;")
#         cursor.execute("DELETE FROM non_compliant;")
#         cursor.execute("DELETE FROM student_subject_enrollment;")  
#         cursor.execute("DELETE FROM subjects;")  
#         cursor.execute("UPDATE sqlite_sequence SET seq = 0;")

        

#         conn.commit()
#         print("✅ All data cleared from students table.")

#     except sqlite3.Error as e:
#         print("❌ Database error:", e)

#     finally:
#         if conn:
#             conn.close()
# def clear_teachers():
#     try:
#         conn = sqlite3.connect(DB_NAME)
#         cursor = conn.cursor()

#         # Delete all records
#         cursor.execute("DELETE FROM teachers;")
#         cursor.execute("DELETE FROM logins;")
#         cursor.execute("DELETE FROM data_admin;")
#         cursor.execute("DELETE FROM admin_data;")
        

        

#         conn.commit()
#         print("✅ All data cleared from teachers table.")

#     except sqlite3.Error as e:
#         print("❌ Database error:", e)

#     finally:
#         if conn:
#             conn.close()
def clear_fees():
    try:
        conn = sqlite3.connect("fees.db")
        cursor = conn.cursor()

        # Delete all records
        cursor.execute("DELETE FROM fees;")
        cursor.execute("DELETE FROM payment_history;")
        cursor.execute("DELETE FROM students;")
        
        

        conn.commit()
        print("✅ All data cleared from fees tables.")

    except sqlite3.Error as e:
        print("❌ Database error:", e)

       
clear_fees()
