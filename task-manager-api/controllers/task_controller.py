from sqlalchemy.orm import joinedload
from database import db
from models.task import Task, VALID_STATUSES
from models.user import User
from models.category import Category
from datetime import datetime
from utils.helpers import MIN_TITLE_LENGTH, MAX_TITLE_LENGTH
import logging

logger = logging.getLogger(__name__)


def _serialize(task, with_names=False):
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    if with_names:
        data['user_name'] = task.user.name if task.user else None
        data['category_name'] = task.category.name if task.category else None
    return data


def _validate(data, partial=False):
    """Retorna mensagem de erro ou None. partial=True ignora campos ausentes (update)."""
    if not partial or 'title' in data:
        title = data.get('title')
        if not title:
            return 'Título é obrigatório'
        if len(title) < MIN_TITLE_LENGTH:
            return 'Título muito curto'
        if len(title) > MAX_TITLE_LENGTH:
            return 'Título muito longo'
    if 'status' in data and data['status'] not in VALID_STATUSES:
        return 'Status inválido'
    if 'priority' in data and (data['priority'] < 1 or data['priority'] > 5):
        return 'Prioridade deve ser entre 1 e 5'
    return None


def _check_refs(data):
    """Valida existência de user_id/category_id. Retorna (mensagem, status) ou None."""
    if data.get('user_id') and not db.session.get(User, data['user_id']):
        return 'Usuário não encontrado', 404
    if data.get('category_id') and not db.session.get(Category, data['category_id']):
        return 'Categoria não encontrada', 404
    return None


def list_tasks():
    tasks = Task.query.options(
        joinedload(Task.user), joinedload(Task.category)
    ).all()
    return [_serialize(t, with_names=True) for t in tasks], 200


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404
    return _serialize(task), 200


def create_task(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400

    error = _validate(data)
    if error:
        return {'error': error}, 400

    ref_error = _check_refs(data)
    if ref_error:
        return {'error': ref_error[0]}, ref_error[1]

    task = Task()
    task.title = data['title']
    task.description = data.get('description', '')
    task.status = data.get('status', 'pending')
    task.priority = data.get('priority', 3)
    task.user_id = data.get('user_id')
    task.category_id = data.get('category_id')

    if data.get('due_date'):
        try:
            task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
        except ValueError:
            return {'error': 'Formato de data inválido. Use YYYY-MM-DD'}, 400

    tags = data.get('tags')
    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    db.session.add(task)
    db.session.commit()
    logger.info('Task criada: %s - %s', task.id, task.title)
    return task.to_dict(), 201


def update_task(task_id, data):
    task = db.session.get(Task, task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404
    if not data:
        return {'error': 'Dados inválidos'}, 400

    error = _validate(data, partial=True)
    if error:
        return {'error': error}, 400

    ref_error = _check_refs(data)
    if ref_error:
        return {'error': ref_error[0]}, ref_error[1]

    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = data['status']
    if 'priority' in data:
        task.priority = data['priority']
    if 'user_id' in data:
        task.user_id = data['user_id']
    if 'category_id' in data:
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
            except ValueError:
                return {'error': 'Formato de data inválido'}, 400
        else:
            task.due_date = None

    if 'tags' in data:
        tags = data['tags']
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    db.session.commit()
    logger.info('Task atualizada: %s', task.id)
    return task.to_dict(), 200


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404
    db.session.delete(task)
    db.session.commit()
    logger.info('Task deletada: %s', task_id)
    return {'message': 'Task deletada com sucesso'}, 200


def search_tasks(args):
    query = Task.query
    if args.get('q'):
        term = args['q']
        query = query.filter(
            db.or_(Task.title.like(f'%{term}%'), Task.description.like(f'%{term}%'))
        )
    if args.get('status'):
        query = query.filter(Task.status == args['status'])
    if args.get('priority'):
        query = query.filter(Task.priority == int(args['priority']))
    if args.get('user_id'):
        query = query.filter(Task.user_id == int(args['user_id']))
    return [t.to_dict() for t in query.all()], 200


def task_stats():
    all_tasks = Task.query.all()
    by_status = {'pending': 0, 'in_progress': 0, 'done': 0, 'cancelled': 0}
    overdue = 0
    for t in all_tasks:
        if t.status in by_status:
            by_status[t.status] += 1
        if t.is_overdue():
            overdue += 1
    total = len(all_tasks)
    stats = {
        'total': total,
        'pending': by_status['pending'],
        'in_progress': by_status['in_progress'],
        'done': by_status['done'],
        'cancelled': by_status['cancelled'],
        'overdue': overdue,
        'completion_rate': round((by_status['done'] / total) * 100, 2) if total > 0 else 0,
    }
    return stats, 200
