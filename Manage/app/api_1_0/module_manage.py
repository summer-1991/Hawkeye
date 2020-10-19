from flask import jsonify, request
from . import api, login_required
from app.models import *
from flask_login import current_user
from ..util.utils import *


@api.route('/module/find', methods=['POST'])
@login_required
def find_model():
    """ 查找接口模块 """
    data = request.json
    page = data.get('page') if data.get('page') else 1
    per_page = data.get('sizePage') if data.get('sizePage') else 10
    project_id = data.get('projectId')
    features = data.get('features')
    if not project_id:
        return jsonify({'msg': '请先创建属于自己的项目', 'status': 0})

    if not features:
        all_module = Project.query.filter_by(id=project_id).first().modules
    else:
        all_module = globals()[features].query.filter_by(project_id=project_id)

    pagination = all_module.paginate(page, per_page=per_page, error_out=False)
    items = pagination.items
    total = pagination.total
    end_data = [{'name': c.name, 'moduleId': c.id, 'num': c.num} for c in items]

    # 查询出所有的接口模块是为了接口录入的时候可以选所有的模块
    _all_module = [{'name': s.name, 'moduleId': s.id, 'num': s.num} for s in all_module.all()]
    return jsonify(
        {'data': end_data, 'total': total, 'status': 1, 'all_module': _all_module, 'role': current_user.role_id})


@api.route('/module/add', methods=['POST'])
@login_required
def add_model():
    """ 接口模块增加、编辑 """
    data = request.json
    project_id = data.get('projectId')
    if not project_id:
        return jsonify({'msg': '请先创建项目', 'status': 0})
    name = data.get('name')
    if not name:
        return jsonify({'msg': '名称不能为空', 'status': 0})

    ids = data.get('id')
    features = data.get('features')
    if not features:
        features = 'Module'

    db_clazz = globals()[features]
    num = auto_num(data.get('num'), db_clazz, project_id=project_id)
    if ids:
        old_data = db_clazz.query.filter_by(id=ids).first()
        old_num = old_data.num
        if not features:
            list_data = Project.query.filter_by(id=project_id).first().modules.all()
        else:
            list_data = db_clazz.query.filter_by(project_id=project_id).all()
        if db_clazz.query.filter_by(name=name, project_id=project_id).first() and name != old_data.name:
            return jsonify({'msg': '名字重复', 'status': 0})

        num_sort(num, old_num, list_data, old_data)
        old_data.name = name
        old_data.project_id = project_id
        db.session.commit()
        return jsonify({'msg': '修改成功', 'status': 1})
    else:
        if db_clazz.query.filter_by(name=name, project_id=project_id).first():
            return jsonify({'msg': '名字重复', 'status': 0})
        else:
            new_model = db_clazz(name=name, project_id=project_id, num=num)
            db.session.add(new_model)
            db.session.commit()
            return jsonify({'msg': '新建成功', 'status': 1})


@api.route('/module/edit', methods=['POST'])
@login_required
def edit_model():
    """ 返回待编辑模块信息 """
    data = request.json
    model_id = data.get('id')
    features = data.get('features')
    if not features:
        features = 'Module'

    db_clazz = globals()[features]
    _edit = db_clazz.query.filter_by(id=model_id).first()
    _data = {'gatherName': _edit.name, 'num': _edit.num}
    return jsonify({'data': _data, 'status': 1})


@api.route('/module/del', methods=['POST'])
@login_required
def del_model():
    """ 删除模块 """
    data = request.json
    ids = data.get('id')
    features = data.get('features')
    if not features:
        features = 'Module'

    db_clazz = globals()[features]
    _edit = db_clazz.query.filter_by(id=ids).first()
    if features == 'Module':
        if current_user.id != Project.query.filter_by(id=_edit.project_id).first().user_id:
            return jsonify({'msg': '不能删除别人项目下的模块', 'status': 0})
        if _edit.api_msg.all():
            return jsonify({'msg': '请先删除模块下的接口用例', 'status': 0})
    elif features == 'DocLib' and _edit.wiki.all():
        return jsonify({'msg': '请先删除库下的文档', 'status': 0})
    elif features == 'ManualSet' and _edit.manual_case.all():
        return jsonify({'msg': '请先删除测试集下的功能用例', 'status': 0})
    elif features == 'ManualTask' and ManualTasksCases.query.filter_by(task_id=_edit.id).all():
        return jsonify({'msg': '请先删除任务下的功能用例', 'status': 0})

    db.session.delete(_edit)
    return jsonify({'msg': '删除成功', 'status': 1})


@api.route('/module/stick', methods=['POST'])
@login_required
def stick_module():
    """ 置顶模块 """
    data = request.json
    module_id = data.get('id')
    project_id = data.get('projectId')
    old_data = Module.query.filter_by(id=module_id).first()
    old_num = old_data.num
    list_data = Project.query.filter_by(id=project_id).first().modules.all()
    num_sort(1, old_num, list_data, old_data)
    db.session.commit()
    return jsonify({'msg': '置顶完成', 'status': 1})
