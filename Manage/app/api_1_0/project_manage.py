from flask import jsonify, request
from . import api
from app.models import *
import json
from ..util.custom_decorator import login_required
from flask_login import current_user
from sqlalchemy import text


@api.route('/proGather/list')
@login_required
def get_pro_gather():
    """ 获取基本信息 """
    # if current_user.id == 4:
    # _pros = Project.query.order_by(case((Project.user_id == current_user.id, 1))).all()
    _pros = Project.query.order_by(text('CASE WHEN user_id={} THEN 0 END DESC'.format(current_user.id))).all()
    my_pros = Project.query.filter_by(user_id=current_user.id).first()
    pro = {}
    pro_and_id = []
    scene_config_lists = {}
    set_list = {}
    scene_list = {}
    pro_base_url = {}

    user_pros = False

    if (current_user.role_id != 2):
        _pros_temp = []
        for project_temp in _pros:
            if current_user.id in [team_user.id for team_user in project_temp.users]:
                _pros_temp.append(project_temp)
        _pros = _pros_temp

    for p in _pros:
        # pro_and_id[p.name] = p.id

        pro_and_id.append({'name': p.name, 'id': p.id})

        # 获取每个项目下的接口模块
        pro[p.id] = [{'name': m.name, 'moduleId': m.id} for m in p.modules]

        # 获取每个项目下的配置信息
        scene_config_lists[p.id] = [{'name': c.name, 'configId': c.id} for c in p.configs]

        # 获取每个项目下的用例集
        set_list[p.id] = [{'label': s.name, 'id': s.id} for s in p.case_sets]

        # 获取每个用例集的用例
        for s in p.case_sets:
            scene_list["{}".format(s.id)] = [{'label': scene.name, 'id': scene.id} for scene in
                                             Case.query.filter_by(case_set_id=s.id).all()]

        pro_base_url[p.id] = json.loads(p.host)
    if my_pros:
        # my_pros = {'pro_name': my_pros.name, 'pro_id': my_pros.id, 'model_list': pro[my_pros.name]}
        user_pros = True

    return jsonify(
        {'data': pro, 'baseUrlData': pro_base_url, 'status': 1, 'config_name_list': scene_config_lists,
         'user_pros': user_pros, 'set_list': set_list, 'scene_list': scene_list, 'pro_and_id': pro_and_id})


@api.route('/project/find', methods=['POST'])
@login_required
def find_project():
    """ 查找项目 """
    data = request.json
    project_name = data.get('projectName')

    page = data.get('page') if data.get('page') else 1
    per_page = data.get('sizePage') if data.get('sizePage') else 10
    user_data = [{'user_id': u.id, 'user_name': u.name} for u in User.query.all()]
    if project_name:
        _data = Project.query.filter(Project.name.like('%{}%'.format(project_name)))
        if not _data:
            return jsonify({'msg': '没有该项目', 'status': 0})
    else:
        _data = Project.query.order_by(Project.id.asc())

    pagination = _data.paginate(page, per_page=per_page, error_out=False)
    items = pagination.items
    total = pagination.total

    if (current_user.role_id != 2):
        items_temp = []
        for project_temp in _data:
            if current_user.id in [team_user.id for team_user in project_temp.users]:
                items_temp.append(project_temp)
        items = items_temp

    end_data = [{'id': c.id,
                 'name': c.name,
                 'choice': c.environment_choice,
                 'principal': User.query.filter_by(id=c.user_id).first().name,
                 'team_names': ','.join([user.name for user in c.users])} for
                c in items]
    return jsonify({'data': end_data, 'total': total, 'status': 1, 'userData': user_data})


@api.route('/project/add', methods=['POST'])
@login_required
def add_project():
    """ 项目增加、编辑 """
    data = request.json
    project_name = data.get('projectName')
    if not project_name:
        return jsonify({'msg': '项目名称不能为空', 'status': 0})
    user_id = data.get('userId')
    if not user_id:
        return jsonify({'msg': '请选择负责人', 'status': 0})
    # principal = data.get('principal')
    environment_choice = data.get('environmentChoice')
    host = json.dumps(data.get('host'))
    ids = data.get('id')
    header = data.get('header')
    variable = data.get('variable')
    func_file = data.get('funcFile')
    team_ids = data.get('team_ids')
    team_ids.append(user_id)
    if ids:
        old_project_data = Project.query.filter_by(id=ids).first()
        if Project.query.filter_by(name=project_name).first() and project_name != old_project_data.name:
            return jsonify({'msg': '项目名字重复', 'status': 0})
        else:
            old_project_data.name = project_name
            old_project_data.user_id = user_id
            old_project_data.environment_choice = environment_choice
            old_project_data.host = host
            old_project_data.headers = header
            old_project_data.variables = variable
            old_project_data.func_file = func_file

            old_project_data.users = User.query.filter(User.id.in_(set(team_ids))).all()
            db.session.commit()
            return jsonify({'msg': '修改成功', 'status': 1})
    else:
        if Project.query.filter_by(name=project_name).first():
            return jsonify({'msg': '项目名字重复', 'status': 0})
        else:
            new_project = Project(name=project_name,
                                  host=host,
                                  user_id=user_id,
                                  func_file=func_file,
                                  environment_choice=environment_choice,
                                  headers=header, variables=variable)
            db.session.add(new_project)
            new_project.users = User.query.filter(User.id.in_(set(team_ids))).all()
            db.session.commit()
            return jsonify({'msg': '新建成功', 'status': 1})


@api.route('/project/del', methods=['POST'])
@login_required
def del_project():
    """ 删除项目 """
    data = request.json
    ids = data.get('id')
    pro_data = Project.query.filter_by(id=ids).first()
    if current_user.id != pro_data.user_id:
        return jsonify({'msg': '不能删除别人创建的项目', 'status': 0})
    if pro_data.modules.all():
        return jsonify({'msg': '请先删除项目下的接口模块', 'status': 0})
    if pro_data.case_sets.all():
        return jsonify({'msg': '请先删除项目下的业务集', 'status': 0})
    if pro_data.configs.all():
        return jsonify({'msg': '请先删除项目下的业务配置', 'status': 0})
    db.session.delete(pro_data)
    return jsonify({'msg': '删除成功', 'status': 1})


@api.route('/project/edit', methods=['POST'])
@login_required
def edit_project():
    """ 返回待编辑项目信息 """
    data = request.json
    pro_id = data.get('id')
    _edit = Project.query.filter_by(id=pro_id).first()
    _data = {'pro_name': _edit.name,
             'user_id': _edit.user_id,
             'principal': _edit.principal,
             'func_file': _edit.func_file,
             'host': json.loads(_edit.host),
             'headers': json.loads(_edit.headers),
             'environment_choice': _edit.environment_choice,
             'variables': json.loads(_edit.variables), 'team_ids': [user.id for user in _edit.users]}
    return jsonify({'data': json.dumps(_data), 'status': 1})
