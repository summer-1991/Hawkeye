from flask import jsonify, request
from app.models import *
from . import api, login_required


@api.route('/resource/add', methods=['POST'])
@login_required
def add_resource():
    """ 增加、编辑 """
    data = request.json
    resource_id = data.get('resourceId')
    resource_type = data.get('resourceType')
    name = data.get('name')
    desc = data.get('desc')
    version = data.get('version')
    borrower = data.get('borrower')

    if not name:
        return jsonify({'msg': '资源型号/账号不能为空', 'status': 0})

    if resource_id:
        old_data = TestResource.query.filter_by(id=resource_id).first()
        old_data.name = name
        old_data.desc = desc
        old_data.version = version
        old_data.borrower = borrower
        db.session.commit()
        return jsonify({'msg': '修改成功', 'status': 1, 'resource_id': resource_id})
    else:
        new_resource = TestResource(name=name,
                                    desc=desc,
                                    version=version,
                                    borrower=borrower,
                                    type=resource_type)
        db.session.add(new_resource)
        db.session.commit()
        return jsonify({'msg': '添加成功', 'status': 1, 'resource_id': new_resource.id})


@api.route('/resource/edit', methods=['POST'])
@login_required
def edit_resource():
    """ 返回待编辑 """
    data = request.json
    resource_id = data.get('resourceId')
    _edit = TestResource.query.filter_by(id=resource_id).first()
    print(_edit)
    _data = {'id': _edit.id, 'name': _edit.name, 'desc': _edit.desc, 'version': _edit.version,
             'borrower': _edit.borrower}
    return jsonify({'data': _data, 'status': 1})


@api.route('/resource/find', methods=['POST'])
@login_required
def find_resource():
    """ 查 """
    data = request.json
    name = data.get('name')
    resource_type = data.get('type')
    page = data.get('page') if data.get('page') else 1
    per_page = data.get('sizePage') if data.get('sizePage') else 20

    if name:
        _data = TestResource.query.filter(TestResource.name.like('%{}%'.format(name)),
                                          TestResource.type == resource_type)
        # total = len(api_data)
        if not _data:
            return jsonify({'msg': '没有该接口信息', 'status': 0})
    else:
        _data = TestResource.query.filter(TestResource.type == resource_type)

    pagination = _data.order_by(TestResource.id.asc()).paginate(page, per_page=per_page, error_out=False)
    items = pagination.items
    total = pagination.total
    end_data = [{'id': c.id,
                 'name': c.name,
                 'desc': c.desc,
                 'version': c.version,
                 'borrower': c.borrower}
                for c in items]
    return jsonify({'data': end_data, 'total': total, 'status': 1})


@api.route('/resource/del', methods=['POST'])
@login_required
def del_resource():
    """ 删除 """
    data = request.json
    resource_id = data.get('resourceId')
    _data = TestResource.query.filter_by(id=resource_id).first()
    db.session.delete(_data)

    return jsonify({'msg': '删除成功', 'status': 1})
