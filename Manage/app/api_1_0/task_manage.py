import json
from flask import jsonify, request
from . import api
from app.models import Task, CaseSet, Case, db, User, CommonConfig
from ..util.custom_decorator import login_required
from app import scheduler
from ..util.http_run import RunCase
from ..util.utils import change_cron, auto_num
from ..util.email.SendEmail import SendEmail
from ..util.report.report import render_html_report
from flask_login import current_user


def aps_test(project_id, case_ids, send_address=None, send_password=None, task_to_address=None, performer='无',
             new_add_args=None):
    # global db
    # db.session.remove()
    # db.create_scoped_session()
    environment = new_add_args['environment']
    url_index = new_add_args['url_index']
    gm_url = new_add_args['gm']
    task_name = new_add_args['task_name']
    flag = new_add_args['flag']
    client_id = new_add_args['client']
    task_variable = new_add_args['json_variable']

    d = RunCase(project_id)
    d.get_case_test(case_ids, environment, url_index, client_id, gm_url, task_variable)
    jump_res = d.run_case()
    res = json.loads(jump_res)

    if flag == 's' or res["success"] is False or res["success"] == 'False':
        d.build_report(jump_res, task_name, performer)

        if send_address:
            task_to_address = task_to_address.split(',')
            file = render_html_report(res)
            s = SendEmail(send_address, send_password, task_to_address, file)
            s.send_email()

    db.session.rollback()  # 把连接放回连接池，不知道为什么定时任务跑完不会自动放回去，导致下次跑的时候，mysql连接超时断开报错
    return d.new_report_id


def get_case_id(pro_id, set_id, case_id):
    case_ids = []
    if len(case_id) != 0:
        case_ids += [i['id'] for i in case_id]
    else:
        if len(case_id) == 0 and len(set_id) != 0:
            _set_ids = [i['id'] for i in set_id]
        else:
            _set_ids = [_set.id for _set in
                        CaseSet.query.filter_by(project_id=pro_id).order_by(CaseSet.num.asc()).all()]

        for set_id in _set_ids:
            for case_data in Case.query.filter_by(case_set_id=set_id).order_by(Case.num.asc()).all():
                case_ids.append(case_data.id)
    return case_ids


@api.route('/task/run', methods=['GET', 'POST'])
@login_required
def run_task():
    """ 单次运行任务 """
    data = request.json
    ids = data.get('id')
    _data = Task.query.filter_by(id=ids).first()
    cases_id = get_case_id(_data.project_id, json.loads(_data.set_id), json.loads(_data.case_id))
    new_add_args = {'environment': _data.environment, 'url_index': _data.url_index, 'gm': _data.gm,
                    'task_name': _data.task_name, 'flag': 's', 'client': _data.client,
                    'json_variable': _data.json_variable}
    new_report_id = aps_test(_data.project_id, cases_id,
                             performer=User.query.filter_by(id=current_user.id).first().name,
                             new_add_args=new_add_args)

    return jsonify({'msg': '测试成功', 'status': 1, 'data': {'report_id': new_report_id}})


@api.route('/task/start', methods=['GET', 'POST'])
@login_required
def start_task():
    """ 任务开启 """
    data = request.json
    ids = data.get('id')
    _data = Task.query.filter_by(id=ids).first()
    config_time = change_cron(_data.task_config_time)
    cases_id = get_case_id(_data.project_id, json.loads(_data.set_id), json.loads(_data.case_id))
    new_add_args = {'environment': _data.environment, 'url_index': _data.url_index, 'gm': _data.gm,
                    'task_name': _data.task_name, 'flag': 'c', 'client': _data.client,
                    'json_variable': _data.json_variable}
    scheduler.add_job(func=aps_test, trigger='cron', misfire_grace_time=60, coalesce=False,
                      args=[_data.project_id, cases_id, _data.task_send_email_address, _data.email_password,
                            _data.task_to_email_address, User.query.filter_by(id=current_user.id).first().name,
                            new_add_args],
                      id=str(ids), **config_time)  # 添加任务
    _data.status = '启动'
    db.session.commit()

    return jsonify({'msg': '启动成功', 'status': 1})


@api.route('/task/add', methods=['POST'])
@login_required
def add_task():
    """ 任务添加、修改 """
    data = request.json
    project_id = data.get('projectId')
    if not project_id:
        return jsonify({'msg': '请选择项目', 'status': 0})
    set_ids = data.get('setIds')
    case_ids = data.get('caseIds')
    task_id = data.get('id')
    num = auto_num(data.get('num'), Task, project_id=project_id)
    name = data.get('name')
    task_type = 'cron'
    to_email = data.get('toEmail')
    send_email = data.get('sendEmail')
    password = data.get('password')
    url_index = data.get('url_index')
    status_url = data.get('status_url')
    environment = data.get('environment')
    gm = data.get('gm')
    json_variable = data.get('json_variable')
    client_id = data.get('clientId')

    if gm is not None and len(gm) > 0 and 'http' not in gm:
        return jsonify({'msg': '待替换的gm_url必须是正确的url格式！', 'status': 0})

    # 0 0 1 * * *
    if not (not to_email and not send_email and not password) and not (to_email and send_email and password):
        return jsonify({'msg': '发件人、收件人、密码3个必须都为空，或者都必须有值', 'status': 0})

    time_config = data.get('timeConfig')
    if len(time_config.strip().split(' ')) != 6:
        return jsonify({'msg': 'cron格式错误', 'status': 0})

    if task_id:
        old_task_data = Task.query.filter_by(id=task_id).first()
        if Task.query.filter_by(task_name=name).first() and name != old_task_data.task_name:
            return jsonify({'msg': '任务名字重复', 'status': 0})
        else:
            old_task_data.project_id = project_id
            old_task_data.set_id = json.dumps(set_ids)
            old_task_data.case_id = json.dumps(case_ids)
            old_task_data.task_name = name
            old_task_data.task_type = task_type
            old_task_data.task_to_email_address = to_email
            old_task_data.task_send_email_address = send_email
            old_task_data.email_password = password
            old_task_data.num = num
            old_task_data.url_index = url_index
            old_task_data.status_url = status_url
            old_task_data.environment = environment
            old_task_data.gm = gm
            old_task_data.json_variable = json_variable
            old_task_data.client = client_id

            if old_task_data.status != '创建' and old_task_data.task_config_time != time_config:
                scheduler.reschedule_job(str(task_id), trigger='cron', **change_cron(time_config))  # 修改任务
                old_task_data.status = '启动'

            old_task_data.task_config_time = time_config
            db.session.commit()
            return jsonify({'msg': '修改成功', 'status': 1})
    else:

        if Task.query.filter_by(task_name=name).first():
            return jsonify({'msg': '任务名字重复', 'status': 0})
        else:
            new_task = Task(task_name=name,
                            project_id=project_id,
                            set_id=json.dumps(set_ids),
                            case_id=json.dumps(case_ids),
                            email_password=password,
                            task_type=task_type,
                            task_to_email_address=to_email,
                            task_send_email_address=send_email,
                            task_config_time=time_config,
                            num=num,
                            url_index=url_index,
                            status_url=status_url,
                            environment=environment, gm=gm, json_variable=json_variable, client=client_id)
            db.session.add(new_task)
            db.session.commit()
            return jsonify({'msg': '新建成功', 'status': 1})


@api.route('/task/edit', methods=['POST'])
@login_required
def edit_task():
    """ 返回待编辑任务信息 """
    data = request.json
    task_id = data.get('id')
    c = Task.query.filter_by(id=task_id).first()
    _data = {'num': c.num, 'task_name': c.task_name, 'task_config_time': c.task_config_time, 'task_type': c.task_type,
             'set_ids': json.loads(c.set_id), 'case_ids': json.loads(c.case_id), 'client': c.client,
             'task_to_email_address': c.task_to_email_address, 'task_send_email_address': c.task_send_email_address,
             'password': c.email_password, 'environment': c.environment, 'url_index': c.url_index, 'gm': c.gm,
             'json_variable': c.json_variable}

    return jsonify({'data': _data, 'status': 1})


@api.route('/task/find', methods=['POST'])
@login_required
def find_task():
    """ 查找任务信息 """
    data = request.json
    project_id = data.get('projectId')
    task_name = data.get('taskName')
    page = data.get('page') if data.get('page') else 1
    per_page = data.get('sizePage') if data.get('sizePage') else 10
    if task_name:
        _data = Task.query.filter_by(project_id=project_id).filter(Task.task_name.like('%{}%'.format(task_name)))
        if not _data:
            return jsonify({'msg': '没有该任务', 'status': 0})
    else:
        _data = Task.query.filter_by(project_id=project_id)
    pagination = _data.order_by(Task.id.asc()).paginate(page, per_page=per_page, error_out=False)
    items = pagination.items
    total = pagination.total
    end_data = [{'task_name': c.task_name, 'task_config_time': c.task_config_time,
                 'id': c.id, 'task_type': c.task_type, 'status': c.status} for c in items]

    _client_config = CommonConfig.query.filter_by(c_type='client')
    client_config = [c.c_key for c in _client_config]

    return jsonify({'data': end_data, 'clients': client_config, 'total': total, 'status': 1})


@api.route('/task/del', methods=['POST'])
@login_required
def del_task():
    """ 删除任务信息 """
    data = request.json
    ids = data.get('id')
    _edit = Task.query.filter_by(id=ids).first()
    if _edit.status != '创建':
        return jsonify({'msg': '请先移除任务', 'status': 0})

    db.session.delete(_edit)
    return jsonify({'msg': '删除成功', 'status': 1})


@api.route('/task/pause', methods=['POST'])
@login_required
def pause_task():
    """ 暂停任务 """
    data = request.json
    ids = data.get('id')
    _data = Task.query.filter_by(id=ids).first()
    _data.status = '暂停'
    scheduler.pause_job(str(ids))  # 添加任务
    db.session.commit()

    return jsonify({'msg': '暂停成功', 'status': 1})


@api.route('/task/resume', methods=['POST'])
@login_required
def resume_task():
    """ 恢复任务 """
    data = request.json
    ids = data.get('id')
    _data = Task.query.filter_by(id=ids).first()
    _data.status = '启动'
    scheduler.resume_job(str(ids))  # 添加任务
    db.session.commit()
    return jsonify({'msg': '恢复成功', 'status': 1})


@api.route('/task/remove', methods=['POST'])
@login_required
def remove_task():
    """ 移除任务 """
    data = request.json
    ids = data.get('id')
    _data = Task.query.filter_by(id=ids).first()
    _data.status = '创建'
    db.session.commit()
    try:
        scheduler.remove_job(str(ids))  # 移除任务
    except Exception as e:
        print(e)
    return jsonify({'msg': '移除成功', 'status': 1})
