import sqlite3

connection = sqlite3.connect("student.db")

cursor = connection.cursor()

table_info = """ CREATE TABLE STUDENT(NAME VARCHAR(25), CLASS VARCHAR(10), SECTION VARCHAR(5), MARKS INT) """
cursor.execute("DROP TABLE IF EXISTS STUDENT")
cursor.execute(table_info)

student_records = [
    ('Krish', 'Data Science', 'A', 90),
    ('John', 'Data Science', 'B', 100),
    ('Mukesh', 'Data Science', 'A', 86),
    ('Jacob', 'DevOps', 'A', 50),
    ('Dipesh', 'DevOps', 'A', 35),
    ('Ananya', 'Data Science', 'B', 92),
    ('Rahul', 'Web Dev', 'A', 78),
    ('Priya', 'Web Dev', 'B', 85),
    ('Amit', 'Data Science', 'A', 65),
    ('Sneha', 'DevOps', 'B', 74),
    ('Vikram', 'Cyber Security', 'A', 88),
    ('Neha', 'Cyber Security', 'B', 91),
    ('Rohan', 'Web Dev', 'A', 42),
    ('Tanvi', 'Data Science', 'B', 95),
    ('Arjun', 'DevOps', 'A', 61),
    ('Meera', 'Web Dev', 'B', 83),
    ('Karan', 'Cyber Security', 'A', 70),
    ('Isha', 'Data Science', 'A', 89),
    ('Aditya', 'DevOps', 'B', 55),
    ('Riya', 'Web Dev', 'A', 67),
    ('Yash', 'Cyber Security', 'B', 80),
    ('Kriti', 'Data Science', 'B', 73),
    ('Vivek', 'DevOps', 'A', 48),
    ('Diya', 'Web Dev', 'B', 96),
    ('Siddharth', 'Cyber Security', 'A', 79)
]

cursor.executemany("INSERT INTO STUDENT VALUES(?,?,?,?)", student_records)

connection.commit()

print("The inserted records are:")
data = cursor.execute("SELECT * FROM STUDENT")
for row in data:
    print(row)

connection.close()