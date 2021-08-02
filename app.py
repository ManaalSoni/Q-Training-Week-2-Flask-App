from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self): #used to represent a class’s objects as a string
        return '<Task %r>' % self.id

@app.route('/', methods=['POST', 'GET']) #sets the page url.
#the two methods that the route can accept: POST, GET. default is GET
def index():
    if request.method == 'POST': # the form action in index.html is post. on clicking submit we enter this if block
        print(request.form)
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)

#user stays on the page as the item gets deleted
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

# when update is initiated the route is from main page to the update page of that task id.
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('update.html', task=task)

#endpoint for search
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        search_content = request.form['tasks']
        # search by author or book
        db.execute("SELECT id, content from todo WHERE content LIKE %s OR id LIKE %s", (search_content, search_content))
        db.commit()
        data = db.fetchall()
        # all in the search box will return all the tuples
        if len(data) == 0 and search_content == 'all': 
            db.execute("SELECT id, content, date_created from todo")
            db.commit()
            data = db.fetchall()
        return render_template('index.html', data=data)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True) # so we can see errors on the webpage