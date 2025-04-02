from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Course model
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique auto-incremented ID
    course_number = db.Column(db.String(10), nullable=False, unique=True)
    course_id = db.Column(db.String(10), nullable=False)  # Shared ID for grouping
    course_name = db.Column(db.String(100), nullable=False)
    group_id = db.Column(db.Integer, nullable=True)  # Removed ForeignKey

    def __repr__(self):
        return f'<Course {self.course_number} - {self.course_name}>'

# Ensure tables are created
with app.app_context():
    db.drop_all()  # Drop existing database (WARNING: This deletes all data!)
    db.create_all()

@app.route('/')
def index():
    courses = Course.query.all()
    grouped_courses = {}

    # Group courses by course_id
    for course in courses:
        if course.course_id not in grouped_courses:
            grouped_courses[course.course_id] = []
        grouped_courses[course.course_id].append(course)

    return render_template('index.html', grouped_courses=grouped_courses)

@app.route('/add', methods=['POST'])
def add_course():
    course_number = request.form['course_number']
    course_id = request.form['course_id']
    course_name = request.form['course_name']

    # Check if there's already a course with the same course_id
    existing_course = Course.query.filter_by(course_id=course_id).first()

    if existing_course:
        group_id = existing_course.id  # Link to the first course with this ID
    else:
        group_id = None  # First entry of this course_id

    new_course = Course(course_number=course_number, course_id=course_id, course_name=course_name, group_id=group_id)
    db.session.add(new_course)
    db.session.commit()

    return redirect('/')

@app.route('/delete/<int:id>')
def delete_course(id):
    course = Course.query.get(id)
    if course:
        db.session.delete(course)
        db.session.commit()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
