from flask import jsonify, request
from . import api
from app.models import *
from ..util.custom_decorator import login_required


@api.route('/commonConfig/find', methods=['POST'])
@login_required
def find_common_config():
    """ 查找 """
    data = request.json
    c_key = data.get('c_key')
    c_type = data.get('c_type')

    page = data.get('page') if data.get('page') else 1
    per_page = data.get('sizePage') if data.get('sizePage') else 10

    if c_key:
        _data = CommonConfig.query.filter_by(c_key=c_key, c_type=c_type)
        if not _data:
            return jsonify({'msg': '没有该配置', 'status': 0})
    else:
        _data = CommonConfig.query.order_by(CommonConfig.id.asc())

    pagination = _data.paginate(page, per_page=per_page, error_out=False)
    items = pagination.items
    total = pagination.total

    end_data = [{'id': c.id,
                 'c_key': c.c_key,
                 'c_value': c.c_value,
                 'desc': c.desc} for
                c in items]
    return jsonify({'data': end_data, 'total': total})


@api.route('/commonConfig/add', methods=['POST'])
@login_required
def add_common_config():
    """ 增加、编辑 """
    data = request.json
    c_key = data.get('c_key')

    if not c_key:
        return jsonify({'msg': 'key不能为空', 'status': 0})

    c_value = data.get('c_value')
    if not c_value:
        return jsonify({'msg': 'value不能为空', 'status': 0})

    c_type = data.get('c_type')
    desc = data.get('desc')
    ids = data.get('id')
    if ids:
        old_data = CommonConfig.query.filter_by(id=ids).first()
        if CommonConfig.query.filter_by(c_key=c_key).first() and c_key != old_data.c_key:
            return jsonify({'msg': 'key重复', 'status': 0})
        else:
            old_data.c_key = c_key
            old_data.c_value = c_value
            old_data.desc = desc

            db.session.commit()
            return jsonify({'msg': '修改成功', 'status': 1})
    else:
        if CommonConfig.query.filter_by(c_key=c_key, c_type=c_type).first():
            return jsonify({'msg': 'key重复', 'status': 0})
        else:
            new_client = CommonConfig(c_type=c_type, c_key=c_key, c_value=c_value, desc=desc)
            db.session.add(new_client)
            db.session.commit()
            return jsonify({'msg': '新建成功', 'status': 1})


@api.route('/commonConfig/del', methods=['POST'])
@login_required
def del_common_config():
    """ 删除客户端 """
    data = request.json
    ids = data.get('id')
    _data = CommonConfig.query.filter_by(id=ids).first()
    db.session.delete(_data)
    return jsonify({'msg': '删除成功', 'status': 1})


@api.route('/commonConfig/edit', methods=['POST'])
@login_required
def edit_common_config():
    """ 返回信息 """
    data = request.json
    ids = data.get('id')
    _edit = CommonConfig.query.filter_by(id=ids).first()
    _data = {'c_key': _edit.c_key, 'c_value': _edit.c_value, 'desc': _edit.desc}
    return jsonify({'data': _data, 'status': 1})
