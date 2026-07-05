from database import db
from models.task import Task
from models.user import User
from models.category import Category
from datetime import timedelta
from utils.helpers import utcnow, calculate_percentage
import logging

logger = logging.getLogger(__name__)


def summary_report():
    users = User.query.all()
    tasks = Task.query.all()  # carrega uma vez, agrega em memória (evita N+1)
    now = utcnow()
    seven_days_ago = now - timedelta(days=7)

    status_counts = {'pending': 0, 'in_progress': 0, 'done': 0, 'cancelled': 0}
    priority_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    overdue_list = []
    recent_created = 0
    recent_done = 0
    per_user = {u.id: {'name': u.name, 'total': 0, 'done': 0} for u in users}

    for t in tasks:
        if t.status in status_counts:
            status_counts[t.status] += 1
        if t.priority in priority_counts:
            priority_counts[t.priority] += 1
        if t.is_overdue():
            overdue_list.append({
                'id': t.id,
                'title': t.title,
                'due_date': str(t.due_date),
                'days_overdue': (now - t.due_date).days,
            })
        if t.created_at and t.created_at >= seven_days_ago:
            recent_created += 1
        if t.status == 'done' and t.updated_at and t.updated_at >= seven_days_ago:
            recent_done += 1
        if t.user_id in per_user:
            per_user[t.user_id]['total'] += 1
            if t.status == 'done':
                per_user[t.user_id]['done'] += 1

    user_stats = [{
        'user_id': uid,
        'user_name': u['name'],
        'total_tasks': u['total'],
        'completed_tasks': u['done'],
        'completion_rate': calculate_percentage(u['done'], u['total']),
    } for uid, u in per_user.items()]

    report = {
        'generated_at': str(now),
        'overview': {
            'total_tasks': len(tasks),
            'total_users': len(users),
            'total_categories': Category.query.count(),
        },
        'tasks_by_status': status_counts,
        'tasks_by_priority': {
            'critical': priority_counts[1],
            'high': priority_counts[2],
            'medium': priority_counts[3],
            'low': priority_counts[4],
            'minimal': priority_counts[5],
        },
        'overdue': {'count': len(overdue_list), 'tasks': overdue_list},
        'recent_activity': {
            'tasks_created_last_7_days': recent_created,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }
    return report, 200


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    tasks = user.tasks
    counts = {'done': 0, 'pending': 0, 'in_progress': 0, 'cancelled': 0}
    overdue = 0
    high_priority = 0
    for t in tasks:
        if t.status in counts:
            counts[t.status] += 1
        if t.priority <= 2:
            high_priority += 1
        if t.is_overdue():
            overdue += 1

    total = len(tasks)
    return {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            'done': counts['done'],
            'pending': counts['pending'],
            'in_progress': counts['in_progress'],
            'cancelled': counts['cancelled'],
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': calculate_percentage(counts['done'], total),
        },
    }, 200


def list_categories():
    categories = Category.query.all()
    result = []
    for c in categories:
        data = c.to_dict()
        data['task_count'] = Task.query.filter_by(category_id=c.id).count()
        result.append(data)
    return result, 200


def create_category(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400
    if not data.get('name'):
        return {'error': 'Nome é obrigatório'}, 400

    category = Category()
    category.name = data['name']
    category.description = data.get('description', '')
    category.color = data.get('color', '#000000')
    db.session.add(category)
    db.session.commit()
    return category.to_dict(), 201


def update_category(cat_id, data):
    cat = db.session.get(Category, cat_id)
    if not cat:
        return {'error': 'Categoria não encontrada'}, 404
    if 'name' in data:
        cat.name = data['name']
    if 'description' in data:
        cat.description = data['description']
    if 'color' in data:
        cat.color = data['color']
    db.session.commit()
    return cat.to_dict(), 200


def delete_category(cat_id):
    cat = db.session.get(Category, cat_id)
    if not cat:
        return {'error': 'Categoria não encontrada'}, 404
    db.session.delete(cat)
    db.session.commit()
    return {'message': 'Categoria deletada'}, 200
