from flask import jsonify, request
from . import api, login_required
from app.models import *
from flask_login import current_user
from ..util.utils import *
from ..util.global_variable import *
from ..util.tool_func import *


@api.route('/testCaseFile/add', methods=['POST'])
@login_required
def add_test_case_file():
    """ 添加用例集合 """
    data = request.json
    name = data.get('name')
    higher_id = data.get('higherId')
    status = data.get('status')
    ids = data.get('id')

    file_type = 'x'
    if data.get('fileType'):
        file_type = data.get('fileType')

    if not name:
        return jsonify({'msg': '名称不能为空', 'status': 0})
    num = auto_num(data.get('num'), CaseSet)
    if ids:
        old_data = TestCaseFile.query.filter_by(id=ids).first()
        old_data.name = name
        old_data.num = num
        old_data.higher_id = higher_id
        old_data.file_type = file_type
        db.session.commit()
        return jsonify({'msg': '修改成功', 'status': 1})
    else:
        _new = TestCaseFile(name=name, higher_id=higher_id, num=num, status=status, user_id=current_user.id,
                            file_type=file_type)
        db.session.add(_new)
        db.session.commit()
        if status == 1:
            with open('{}{}.txt'.format(TEST_FILE_ADDRESS, _new.id), 'w', encoding='utf-8') as f:
                if file_type == 'x':
                    f.write(
                        """{"root":{"data":{"id":"byqb16f7t8o0","created":1574819812654,"text":"中心主题",
                        "priority":null,"font-family":"黑体, SimHei","font-size":32,"progress":null},"children":[]},
                        "template":"right","theme":"fresh-blue","version":"1.4.43"}""")
                else:
                    f.write(
                        """[{"name": "Sheet1", "color": "", "index": 1, "status": 1, "order": 1, "celldata": [], 
                        "config": {}}]""")
        return jsonify({'msg': '新建成功', 'status': 1, 'id': _new.id, 'higher_id': _new.higher_id, })


#
@api.route('/testCaseFile/find', methods=['POST'])
@login_required
def find_test_case_file():
    """ 查找所有测试用例 """
    data = request.json
    privates = data.get('privates')

    file_type = 'x'
    if data.get('fileType'):
        file_type = data.get('fileType')

    kwargs = {'higher_id': 0, 'file_type': file_type}
    if privates:
        kwargs['user_id'] = current_user.id

    def get_data(all_data):
        if isinstance(all_data, list):
            if all_data:
                _t = []
                for d in all_data:
                    _t.append(get_data(d))
                return _t
            else:
                return []
        else:
            _d = {'id': all_data.id, 'num': all_data.num, 'name': all_data.name, 'status': all_data.status,
                  'higher_id': all_data.higher_id}
            if all_data.status == 0:
                kwargs['higher_id'] = all_data.id
                _d['children'] = get_data(
                    TestCaseFile.query.filter_by(**kwargs).order_by(TestCaseFile.num.asc()).all())
            return _d

    end_data = get_data(TestCaseFile.query.filter_by(**kwargs).order_by(TestCaseFile.num.asc()).all())

    return jsonify({'status': 1, 'data': end_data, 'msg': 1})


@api.route('/testCaseFile/get', methods=['POST'])
@login_required
def get_test_case_file():
    """ 返回待编辑用例集合 """
    data = request.json
    ids = data.get('id')
    with open('{}{}.txt'.format(TEST_FILE_ADDRESS, ids), 'r', encoding='utf-8') as f:
        _data = f.read()
    return jsonify({'data': _data, 'status': 1})


@api.route('/testCaseFile/save', methods=['POST'])
@login_required
def save_test_case_file():
    """ 返回待编辑用例集合 """
    data = request.json
    _data = data.get('data')
    show = data.get('show')
    ids = data.get('ids')

    old_data = TestCaseFile.query.filter_by(id=ids).first()
    if old_data.operator_id != 0 and old_data.operator_id != current_user.id:
        user_data = User.query.filter_by(id=old_data.operator_id).first()
        return jsonify({'status': 0, 'msg': '{} 正在编辑，请稍后...'.format(user_data.name)})

    if _data is None or _data == '':
        return jsonify({'status': 0, 'msg': '保存内容为空'})

    with open('{}{}.txt'.format(TEST_FILE_ADDRESS, ids), 'w', encoding='utf-8') as f:
        f.write(_data)
    if show:
        return jsonify({'status': 1, 'msg': '保存成功'})
    else:
        return jsonify({'status': 1})


#
@api.route('/testCaseFile/del', methods=['POST'])
@login_required
def del_test_case_file():
    """ 删除用例集合 """
    data = request.json
    ids = data.get('id')
    _edit = TestCaseFile.query.filter_by(id=ids).first()
    case = TestCaseFile.query.filter_by(higher_id=ids).first()
    if current_user.id != _edit.user_id:
        return jsonify({'msg': '不能删除别人创建的', 'status': 0})
    if case:
        return jsonify({'msg': '请先删除该文件的下级内容', 'status': 0})

    if _edit.status == 1:
        if not os.path.exists('{}{}.txt'.format(TEST_FILE_ADDRESS, ids)):
            return jsonify({'msg': '文件名不存在', 'status': 0})
        else:
            os.remove('{}{}.txt'.format(TEST_FILE_ADDRESS, ids))

    db.session.delete(_edit)
    return jsonify({'msg': '删除成功', 'status': 1})


@api.route('/testCaseFile/update', methods=['POST'])
@login_required
def update_test_case_file_operator():
    """ 更新此时文件操作者 """
    data = request.json
    old_id = data.get('oldId')
    new_id = data.get('newId')

    if old_id != 0:
        _old_data = TestCaseFile.query.filter_by(id=old_id).first()
        if _old_data.operator_id == current_user.id:
            _old_data.operator_id = 0

    if new_id != 0:
        _new_data = TestCaseFile.query.filter_by(id=new_id).first()
        if _new_data.status == 1 and _new_data.operator_id == 0:
            _new_data.operator_id = current_user.id

    db.session.commit()
    return jsonify({'msg': '更新成功', 'status': 1})


@api.route('/testCaseFile/uploadFile', methods=['POST'])
@login_required
def upload_mind_file():
    """ 上传mind文件 """
    id_data = request.form
    id = id_data.get('id')

    data = request.files
    file = data['file']
    suffix = file.filename.split(".")[1]
    file.save(os.path.join(TEST_FILE_ADDRESS, "{}.{}".format(id, suffix)))
    res = open_xmind_to_json(id)

    with open('{}{}.txt'.format(TEST_FILE_ADDRESS, id), 'w', encoding='utf-8') as f:
        f.write(res)

    os.remove('{}{}.xmind'.format(TEST_FILE_ADDRESS, id))
    os.remove('{}{}.json'.format(TEST_FILE_ADDRESS, id))
    return jsonify({"msg": "上传成功", "status": 1})
