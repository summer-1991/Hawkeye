from flask import jsonify, request
from . import api, login_required
from app.models import *
from flask_login import current_user
from ..util.global_variable import *
from ..util.utils import *


@api.route('/manual/findBySet', methods=['POST'])
@login_required
def find_manual_by_set():
    """ 查用例信息 """
    data = request.json
    module_id = data.get('moduleId')
    case_name = data.get('caseName')
    page = data.get('page') if data.get('page') else 1
    per_page = data.get('sizePage') if data.get('sizePage') else 20

    if not module_id:
        return jsonify({'msg': '请先在创建测试集', 'status': 0})

    manual_task = [{'task_id': t.id, 'task_name': t.name} for t in ManualTask.query.all()]
    if case_name:
        _data = ManualCase.query.filter_by(module_id=module_id).filter(ManualCase.name.like('%{}%'.format(case_name)))
        # total = len(api_data)
        if not _data:
            return jsonify({'msg': '没有查到用例', 'status': 0})
    else:
        _data = ManualCase.query.filter_by(module_id=module_id)

    pagination = _data.order_by(ManualCase.id.asc()).paginate(page, per_page=per_page, error_out=False)
    items = pagination.items
    total = pagination.total
    end_data = [{'id': c.id,
                 'name': c.name,
                 'create_by': User.query.filter_by(id=c.user_id).first().name,
                 'case_type': c.case_type,
                 'desc': c.desc,
                 'precondition': c.precondition,
                 'steps': c.steps,
                 'expect': c.expect} for c in items]
    return jsonify({'data': end_data, 'total': total, 'status': 1, 'manual_task': manual_task})


@api.route('/manual/edit', methods=['POST'])
@login_required
def edit_manual():
    """ 返回待编辑 """
    data = request.json
    case_id = data.get('caseId')
    set_id = data.get('setId')
    _edit = ManualCase.query.filter_by(id=case_id).first()

    _previous_edit = ManualCase.query.filter(ManualCase.id < case_id, ManualCase.module_id == set_id).order_by(
        ManualCase.id.desc()).first()
    _next_edit = ManualCase.query.filter(ManualCase.id > case_id, ManualCase.module_id == set_id).order_by(
        ManualCase.id.asc()).first()
    previous_id = 0
    next_id = 0
    if _next_edit:
        next_id = _next_edit.id
    if _previous_edit:
        previous_id = _previous_edit.id

    _data = {'id': _edit.id, 'name': _edit.name, 'desc': _edit.desc, 'module_id': _edit.module_id,
             'case_type': _edit.case_type, 'precondition': _edit.precondition, 'steps': _edit.steps,
             'expect': _edit.expect}
    return jsonify({'data': _data, 'status': 1, 'previous_id': previous_id, 'next_id': next_id})


@api.route('/manual/add', methods=['POST'])
@login_required
def add_manual():
    """ 保存用例 """
    data = request.json
    case_id = data.get('caseId')
    name = data.get('caseName')
    desc = data.get('desc')
    case_type = data.get('case_type')
    precondition = data.get('precondition')
    steps = data.get('steps')
    expect = data.get('expect')
    module_id = data.get('moduleId')
    case_from = 'add'

    if case_id:
        old_data = ManualCase.query.filter_by(id=case_id).first()
        if ManualCase.query.filter_by(name=name, module_id=module_id).first() and name != old_data.name:
            return jsonify({'msg': '用例名字重复', 'status': 0})

        old_data.name = name
        old_data.desc = desc
        old_data.case_type = case_type
        old_data.precondition = precondition
        old_data.module_id = module_id
        old_data.steps = steps
        old_data.expect = expect
        db.session.commit()

        return jsonify({'msg': '修改成功', 'status': 1, 'case_id': case_id})
    else:
        user_id = current_user.id
        if ManualCase.query.filter_by(name=name, module_id=module_id).first():
            return jsonify({'msg': '用例名字重复', 'status': 0})
        else:
            new_case = ManualCase(name=name,
                                  desc=desc,
                                  case_type=case_type,
                                  module_id=module_id,
                                  user_id=user_id,
                                  precondition=precondition, steps=steps, expect=expect, case_from=case_from)
            db.session.add(new_case)
            db.session.commit()
            return jsonify({'msg': '新建成功', 'status': 1, 'case_id': new_case.id})


@api.route('/manual/del', methods=['POST'])
@login_required
def del_manual():
    """ 删除用例 """
    data = request.json
    case_id = data.get('caseId')
    _data = ManualCase.query.filter_by(id=case_id).first()
    if current_user.id != _data.user_id:
        return jsonify({'msg': '不能删除别人负责的用例', 'status': 0})

    db.session.delete(_data)
    return jsonify({'msg': '删除成功', 'status': 1})


@api.route('/manual/findByTask', methods=['POST'])
@login_required
def find_manual_by_task():
    """ 查任务下的用例信息 """
    data = request.json
    module_id = data.get('moduleId')
    case_name = data.get('caseName')
    page = data.get('page') if data.get('page') else 1
    per_page = data.get('sizePage') if data.get('sizePage') else 20

    if not module_id:
        return jsonify({'msg': '请先在创建测试任务', 'status': 0})

    user_data = [{'user_id': u.id, 'user_name': u.name} for u in User.query.all()]
    set_data = [{'set_id': s.id, 'set_name': s.name} for s in ManualSet.query.all()]

    if case_name:
        _data = ManualTasksCases.query.join(ManualCase).filter(ManualTasksCases.task_id == module_id).filter(
            ManualCase.name.like('%{}%'.format(case_name)))
        # total = len(api_data)
        if not _data:
            return jsonify({'msg': '没有查到用例', 'status': 0})
    else:
        _data = ManualTasksCases.query.join(ManualCase).filter(ManualTasksCases.task_id == module_id)

    pagination = _data.order_by(ManualTasksCases.id.asc()).paginate(page, per_page=per_page, error_out=False)
    items = pagination.items
    total = pagination.total

    end_data = [{'id': c.id,
                 'name': ManualCase.query.filter_by(id=c.case_id).first().name,
                 'case_type': ManualCase.query.filter_by(id=c.case_id).first().case_type,
                 'count': c.count,
                 'last_by': c.last_by,
                 'last_res': c.last_res,
                 'desc': ManualCase.query.filter_by(id=c.case_id).first().desc,
                 'last_desc': c.desc} for c in items]
    return jsonify({'data': end_data, 'total': total, 'status': 1, 'user_data': user_data, 'set_data': set_data})


@api.route('/manual/delByTask', methods=['POST'])
@login_required
def del_manual_by_task():
    """ 删除任务下的用例 """
    data = request.json
    task_case_id = data.get('taskCaseId')
    _data = ManualTasksCases.query.filter_by(id=task_case_id).first()
    db.session.delete(_data)
    return jsonify({'msg': '删除成功', 'status': 1})


@api.route('/manual/searchCase', methods=['POST'])
@login_required
def find_search_case():
    """ 搜索用例信息 """
    data = request.json
    task_id = data.get('taskId')
    case_name = data.get('caseName')
    case_type = data.get('caseType')
    create_by = data.get('createBy')
    manual_set = data.get('manualSet')
    page = data.get('page') if data.get('page') else 1
    per_page = data.get('sizePage') if data.get('sizePage') else 10

    filters = []
    if case_type:
        filters.append(ManualCase.case_type.in_(set(case_type)))

    if manual_set:
        filters.append(ManualCase.module_id.in_(set(manual_set)))

    if create_by:
        filters.append(ManualCase.user_id.in_(set(create_by)))

    if case_name:
        filters.append(ManualCase.name.like('%{}%'.format(case_name)))

    case_ids = [c.case_id for c in ManualTasksCases.query.filter_by(task_id=task_id)]
    filters.append(ManualCase.id.notin_(set(case_ids)))

    if filters:
        _data = ManualCase.query.filter(*filters)
    else:
        _data = ManualCase.query

    pagination = _data.order_by(ManualCase.id.asc()).paginate(page, per_page=per_page, error_out=False)
    items = pagination.items
    total = pagination.total
    end_data = [{'id': c.id,
                 'name': c.name,
                 'manual_set': ManualSet.query.filter_by(id=c.module_id).first().name,
                 'create_by': User.query.filter_by(id=c.user_id).first().name,
                 'case_type': c.case_type,
                 'desc': c.desc} for c in items]
    return jsonify({'data': end_data, 'total': total, 'status': 1})


@api.route('/manual/addToTask', methods=['POST'])
@login_required
def find_manual_to_task():
    """ 任务增加用例 """
    data = request.json
    module_id = data.get('moduleId')
    case_ids = data.get('caseIds')

    for case_id in case_ids:
        manual_task_case = ManualTasksCases.query.filter_by(task_id=module_id, case_id=case_id).first()
        if not manual_task_case:
            new_case = ManualTasksCases(task_id=module_id,
                                        case_id=case_id,
                                        last_res=0,
                                        count=0)
            db.session.add(new_case)
            db.session.commit()

    return jsonify({'msg': '添加成功', 'status': 1})


@api.route('/manual/runTaskCase', methods=['POST'])
@login_required
def edit_run_task_case():
    """ 执行用例 """
    data = request.json
    task_case_id = data.get('taskCaseId')
    run_desc = data.get('runDesc')
    run_res = data.get('runRes')

    _run = ManualTasksCases.query.filter_by(id=task_case_id).first()

    if not _run:
        return jsonify({'data': {}, 'msg': '没有此用例', 'status': 0})

    if not run_res:
        task_id = data.get('taskId')
        _run_case = ManualCase.query.filter_by(id=_run.case_id).first()

        _previous_run_case = ManualTasksCases.query.filter(ManualTasksCases.id < task_case_id,
                                                           ManualTasksCases.task_id == task_id).order_by(
            ManualTasksCases.id.desc()).first()
        _next_run_case = ManualTasksCases.query.filter(ManualTasksCases.id > task_case_id,
                                                       ManualTasksCases.task_id == task_id).order_by(
            ManualTasksCases.id.asc()).first()
        previous_id = 0
        next_id = 0
        if _previous_run_case:
            previous_id = _previous_run_case.id
        if _next_run_case:
            next_id = _next_run_case.id

        _data = {'precondition': _run_case.precondition, 'steps': _run_case.steps,
                 'expect': _run_case.expect, 'lastRes': _run.last_res, 'runDesc': _run.desc, 'id': _run.id,
                 'name': _run_case.name}
        return jsonify({'data': _data, 'status': 1, 'previous_id': previous_id, 'next_id': next_id})
    else:
        _run.last_by = current_user.name
        _run.last_res = run_res
        _run.desc = run_desc
        _run.count = _run.count + 1
        db.session.commit()
        return jsonify({'msg': '更新成功', 'status': 1})


@api.route('/manual/importCase', methods=['POST'])
@login_required
def import_case():
    data = request.form
    import_steps = data.get('importSteps')

    import_data = {}
    if request.files and import_steps == 'read':
        files = dict(request.files)['files']
        for file in files:
            file_name = file.filename
            file.save(os.path.join(FILE_ADDRESS, file_name))
            import_data = read_excel(os.path.join(FILE_ADDRESS, file_name))
            # os.remove(os.path.join(FILE_ADDRESS, file_name))
    return jsonify({'data': import_data, 'msg': '数据读取成功！', 'status': 1})


@api.route('/manual/doImport', methods=['POST'])
@login_required
def do_import_case():
    data = request.json
    import_cases = data.get('importCases')
    set_id = data.get('moduleId')

    user_id = current_user.id
    db.session.execute(
        ManualCase.__table__.insert(),
        [{"name": case[0], "case_type": case[1], "desc": case[2], "module_id": set_id, "user_id": user_id,
          "precondition": case[3], "steps": case[4], "expect": case[5], "case_from": 'import'} for case in
         import_cases]
    )
    db.session.commit()
    return jsonify({'msg': '外部用例导入成功！', 'status': 1})