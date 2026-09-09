from flask import Flask, jsonify, request
from typing import Dict, List


app = Flask(__name__)
tasks: List[Dict] = [
    {'id': 1, 'title': '学习Python', 'completed': False},
    {'id': 2, 'title': '实践算法', 'completed': True},
]


@app.route('/')
def home():
    return jsonify({'message': '欢迎使用Flask学习项目'})


@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})


@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id: int):
    task = next((task for task in tasks if task['id'] == task_id), None)
    if task:
        return jsonify(task)
    return jsonify({'error': '任务未找到'}), 404


@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': '标题是必需的'}), 400
    
    new_task = {
        'id': len(tasks) + 1,
        'title': data['title'],
        'completed': data.get('completed', False)
    }
    tasks.append(new_task)
    return jsonify(new_task), 201


@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id: int):
    task = next((task for task in tasks if task['id'] == task_id), None)
    if not task:
        return jsonify({'error': '任务未找到'}), 404
    
    data = request.get_json()
    task.update({
        'title': data.get('title', task['title']),
        'completed': data.get('completed', task['completed'])
    })
    return jsonify(task)


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id: int):
    global tasks
    task = next((task for task in tasks if task['id'] == task_id), None)
    if not task:
        return jsonify({'error': '任务未找到'}), 404
    
    tasks = [t for t in tasks if t['id'] != task_id]
    return jsonify({'message': '任务已删除'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)