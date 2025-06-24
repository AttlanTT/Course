from flask import Flask, request, jsonify, render_template, redirect, session, url_for, send_file
import json, os, hashlib
from functools import wraps
from io import StringIO
from utils import generators, memoization, priority_queue, async_array, large_data, reactive
from utils.memoization import memoize
from utils.priority_queue import BiPriorityQueue

app = Flask(__name__)
app.secret_key = 'supersecretkey'

DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    with open(USERS_FILE, 'w') as f:
        json.dump({}, f)

def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def get_tasks_file(username):
    return os.path.join(DATA_DIR, f'{username}_tasks.json')

def load_tasks(username):
    path = get_tasks_file(username)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return []

def save_tasks(username, tasks):
    with open(get_tasks_file(username), 'w') as f:
        json.dump(tasks, f)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper

@app.route('/')
@login_required
def index():
    return render_template('index.html', username=session['user'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        users = load_users()
        if username in users:
            return 'Користувач вже існує'
        users[username] = password
        save_users(users)
        save_tasks(username, [])
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        users = load_users()
        if users.get(username) == password:
            session['user'] = username
            return redirect('/')
        return 'Невірні дані'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user')
    return redirect('/login')

@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    return jsonify(load_tasks(session['user']))

@app.route('/api/tasks', methods=['POST'])
@login_required
def add_task():
    tasks = load_tasks(session['user'])
    new_task = request.get_json()
    new_task['id'] = max([t['id'] for t in tasks], default=0) + 1
    new_task['done'] = False
    tasks.append(new_task)
    save_tasks(session['user'], tasks)
    return jsonify(new_task), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    tasks = load_tasks(session['user'])
    data = request.get_json()
    for task in tasks:
        if task['id'] == task_id:
            if 'title' in data:
                task['title'] = data['title']
            elif 'priority' in data:
                task['priority'] = data['priority']
            else:
                task['done'] = not task['done']
            save_tasks(session['user'], tasks)
            return jsonify(task)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    tasks = load_tasks(session['user'])
    tasks = [t for t in tasks if t['id'] != task_id]
    save_tasks(session['user'], tasks)
    return '', 204

@app.route('/demo/reactive')
def demo_reactive():
    logs = []
    emitter = reactive.EventEmitter()
    emitter.subscribe("message", lambda msg: logs.append(f"📩 {msg}"))
    emitter.emit("message", "Привіт від EventEmitter!")
    return "<br>".join(logs)

@memoize(max_size=10)
def get_stats(user):
    tasks = load_tasks(user)
    total = len(tasks)
    done = len([t for t in tasks if t['done']])
    return {'total': total, 'done': done, 'remaining': total - done}

@app.route('/api/stats')
@login_required
def stats():
    return jsonify(get_stats(session['user']))

@app.route('/api/tasks/sorted')
@login_required
def get_tasks_sorted():
    tasks = load_tasks(session['user'])
    pq = BiPriorityQueue()
    for t in tasks:
        p = {'low': 1, 'medium': 2, 'high': 3}.get(t.get('priority', 'medium'), 2)
        pq.enqueue(t, p)
    sorted_tasks = []
    while True:
        try:
            sorted_tasks.append(pq.dequeue('highest'))
        except IndexError:
            break
    return jsonify(sorted_tasks)

@app.route('/export/stream')
@login_required
def export_stream():
    tasks = load_tasks(session['user'])
    output = StringIO()
    output.write("id,title,priority,done,deadline\n")
    for task in tasks:
        output.write(f"{task['id']},{task['title']},{task.get('priority','medium')},{task['done']},{task.get('deadline','')}\n")
    output.seek(0)
    return send_file(output, mimetype='text/csv', download_name='tasks.csv', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
