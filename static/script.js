const taskList = document.getElementById('taskList');
const taskInput = document.getElementById('taskInput');
const taskDeadline = document.getElementById('taskDeadline');
const taskPriority = document.getElementById('taskPriority');
const searchInput = document.getElementById('searchInput');
const stats = document.getElementById('stats');

function loadTasks() {
    fetch('/api/tasks')
        .then(res => res.json())
        .then(tasks => {
            const query = searchInput.value.toLowerCase();
            taskList.innerHTML = '';
            let doneCount = 0;

            function priorityColor(priority) {
                switch(priority) {
                    case 'high': return '#ff9999';
                    case 'medium': return '#fff799';
                    case 'low': return '#99ff99';
                    default: return '#eee';
                }
            }

            tasks.filter(task => task.title.toLowerCase().includes(query)).forEach(task => {
                const li = document.createElement('li');
                li.setAttribute('data-id', task.id);

                const expired = task.deadline && new Date(task.deadline) < new Date() && !task.done;
                li.style.background = expired ? '#ffcccc' : priorityColor(task.priority);

                li.innerHTML = `
                    <span class="${task.done ? 'done' : ''}" onclick="toggleDone(${task.id})">${task.title}</span>
                    <small>Пріоритет: ${task.priority || 'medium'} | Дедлайн: ${task.deadline || '—'}</small>
                    <div>
                        <button onclick="editTask(${task.id})">✏️</button>
                        <button onclick="deleteTask(${task.id})">🗑️</button>
                    </div>
                `;
                taskList.appendChild(li);
                if (task.done) doneCount++;
            });

            stats.innerText = `Всього: ${tasks.length}, Виконано: ${doneCount}, Залишилось: ${tasks.length - doneCount}`;
        });
}

function addTask() {
    const title = taskInput.value.trim();
    const deadline = taskDeadline.value;
    const priority = taskPriority.value;
    if (!title) return;
    fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, deadline, priority })
    }).then(() => {
        taskInput.value = '';
        taskDeadline.value = '';
        taskPriority.value = 'medium';
        loadTasks();
    });
}

function toggleDone(id) {
    fetch(`/api/tasks/${id}`, { method: 'PUT' })
        .then(() => loadTasks());
}

function deleteTask(id) {
    fetch(`/api/tasks/${id}`, { method: 'DELETE' })
        .then(() => loadTasks());
}

function editTask(id) {
    const li = taskList.querySelector(`li[data-id='${id}']`);
    if (!li) return;
    const span = li.querySelector('span');
    const newTitle = prompt("Редагувати завдання:", span.innerText);
    if (newTitle !== null && newTitle.trim()) {
        fetch(`/api/tasks/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: newTitle.trim() })
        }).then(() => loadTasks());
    }
}

function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
}

window.onload = () => {
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-theme');
    }
    loadTasks();
};
