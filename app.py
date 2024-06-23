from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
import pytz

app = Flask(__name__, template_folder='template')
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class TodoForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    desc = TextAreaField('Description')
    submit = SubmitField('Update')


with app.app_context():
    db.create_all()


class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    data_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = Todo(title=title, desc=desc)
        db.session.add(todo)
        db.session.commit()
    allTodo = Todo.query.all()

    # Convert UTC datetime to local timezone (e.g., 'Asia/Kolkata')
    local_timezone = pytz.timezone('Asia/Kolkata')
    for todo in allTodo:
        if todo.data_created:
            todo.data_created = todo.data_created.astimezone(local_timezone)

    return render_template('index.html', allTodo=allTodo)

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    todo = Todo.query.get_or_404(sno)
    form = TodoForm(obj=todo)  # Populate form with current Todo object data

    if form.validate_on_submit():
        todo.title = form.title.data
        todo.desc = form.desc.data

        db.session.commit()
        return redirect('/')

    return render_template('update.html', form=form)


@app.route('/delete/<int:sno>', methods=['GET', 'POST'])
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
