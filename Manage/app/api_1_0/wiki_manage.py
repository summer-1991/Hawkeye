from flask import jsonify, request
from . import api, login_required
from app.models import *
from ..util.global_variable import *
from ..util.utils import *
from flask_login import current_user
from sqlalchemy import or_


@api.route('/wiki/find', methods=['POST'])
@login_required
def find_wiki():
    """ 查接口信息 """
    data = request.json
    module_id = data.get('moduleId')
    wiki_name = data.get('wikiName')
    page = data.get('page') if data.get('page') else 1
    per_page = data.get('sizePage') if data.get('sizePage') else 20

    if not module_id:
        return jsonify({'msg': '请先在创建文档库', 'status': 0})

    if wiki_name:
        _data = Wiki.query.filter_by(module_id=module_id).filter(Wiki.name.like('%{}%'.format(wiki_name)))
        # total = len(api_data)
        if not _data:
            return jsonify({'msg': '没有查到文档', 'status': 0})
    else:
        _data = Wiki.query.filter_by(module_id=module_id)

    if current_user.role_id != 2:
        _data = _data.filter(
            or_(Wiki.auth == 0, Wiki.user_id == current_user.id, Wiki.team.like('%,{},%'.format(current_user.id))))

    pagination = _data.order_by(Wiki.num.asc()).paginate(page, per_page=per_page, error_out=False)
    items = pagination.items
    total = pagination.total
    end_data = [{'num': c.num,
                 'name': c.name,
                 'desc': c.desc,
                 'user_id': c.user_id,
                 'update_time': str(c.update_time),
                 'create_by': User.query.filter_by(id=c.user_id).first().name,
                 'annex_name': c.annex_name,
                 'auth': c.auth,
                 'team': c.team,
                 'wikiId': c.id}
                for c in items]

    user_data = [{'user_id': u.id, 'user_name': u.name} for u in User.query.all()]
    return jsonify({'data': end_data, 'total': total, 'status': 1, 'user_data': user_data})


@api.route('/wiki/edit', methods=['POST'])
@login_required
def edit_wiki():
    """ 返回待编辑 """
    data = request.json
    wiki_id = data.get('wikiId')
    _edit = Wiki.query.filter_by(id=wiki_id).first()
    annex_list = json.loads(_edit.annex_name)
    with open('{}/{}.txt'.format(WIKI_FILE_ADDRESS, wiki_id), 'r', encoding='utf8') as f:
        content = f.read()

    team_ids = []
    if _edit.team:
        for user_id in _edit.team.split(','):
            if user_id and user_id != 'null':
                team_ids.append(int(user_id))
    _data = {'name': _edit.name, 'num': _edit.num, 'desc': _edit.desc, 'module_id': _edit.module_id,
             'auth': str(_edit.auth), 'team': team_ids, 'annex_name': annex_list, 'content': content}
    return jsonify({'data': _data, 'status': 1})


@api.route('/wiki/add', methods=['POST'])
@login_required
def add_wiki():
    """ 保存文档 """
    data = request.form
    wiki_id = data.get('wikiId')
    name = data.get('name')
    desc = data.get('desc')
    auth = int(data.get('auth'))
    team = ',{},'.format(data.get('team'))
    module_id = data.get('moduleId')
    content = data.get('content')

    if request.files:
        files = dict(request.files)['files']
        for file in files:
            file.save(os.path.join(FILE_ADDRESS, file.filename))

    temp_num = data.get('num')
    if temp_num == 'null':
        temp_num = ''

    num = auto_num(temp_num, Wiki, module_id=module_id)
    if isinstance(num, str):
        num = int(num)

    file_list = json.loads(data.get('annex_name'))
    for old_file in file_list:
        old_file['status'] = "success"
        old_file['url'] = "/files/" + old_file['name']

    annex_name = json.dumps(file_list)

    if wiki_id != 'null' and wiki_id:
        old_data = Wiki.query.filter_by(id=wiki_id).first()
        old_num = old_data.num
        if Wiki.query.filter_by(name=name, module_id=module_id).first() and name != old_data.name:
            return jsonify({'msg': '接口名字重复', 'status': 0})

        list_data = DocLib.query.filter_by(id=module_id).first().wiki.all()
        num_sort(num, old_num, list_data, old_data)
        old_data.name = name
        old_data.desc = desc
        old_data.auth = auth
        old_data.team = team
        old_data.module_id = module_id
        old_data.annex_name = annex_name
        db.session.commit()

        with open('{}/{}.txt'.format(WIKI_FILE_ADDRESS, wiki_id), 'w', encoding='utf8') as f:
            f.write(content)
        return jsonify({'msg': '修改成功', 'status': 1, 'wiki_id': wiki_id, 'num': num, "file_list": file_list})
    else:
        user_id = current_user.id
        if Wiki.query.filter_by(name=name, module_id=module_id).first():
            return jsonify({'msg': '接口名字重复', 'status': 0})
        else:
            new_wiki = Wiki(name=name,
                            num=num,
                            desc=desc,
                            auth=auth,
                            team=team,
                            module_id=module_id,
                            user_id=user_id,
                            annex_name=annex_name)
            db.session.add(new_wiki)
            db.session.commit()

            with open('{}/{}.txt'.format(WIKI_FILE_ADDRESS, new_wiki.id), 'w', encoding='utf8') as f:
                f.write(content)

            return jsonify(
                {'msg': '新建成功', 'status': 1, 'wiki_id': new_wiki.id, 'num': new_wiki.num, "file_list": file_list})


@api.route('/wiki/del', methods=['POST'])
@login_required
def del_wiki():
    """ 删除接口信息 """
    data = request.json
    wiki_id = data.get('wikiId')
    _data = Wiki.query.filter_by(id=wiki_id).first()
    if current_user.id != _data.user_id:
        return jsonify({'msg': '不能删除别人项目下的接口', 'status': 0})

    annex_list = json.loads(_data.annex_name)
    for annex in annex_list:
        file_name = annex['name']
        if os.path.exists(os.path.join(FILE_ADDRESS, file_name)):
            os.remove(os.path.join(FILE_ADDRESS, file_name))

    wiki_name = str(_data.id) + ".txt"
    if os.path.exists(os.path.join(WIKI_FILE_ADDRESS, wiki_name)):
        os.remove(os.path.join(WIKI_FILE_ADDRESS, wiki_name))
    db.session.delete(_data)
    return jsonify({'msg': '删除成功', 'status': 1})

@api.route('/wiki/moveUp', methods=['POST'])
@login_required
def moveUp_wiki():
    """向上移动"""
    data = request.json
    cur_wiki_id = data.get('curWikiId')
    pre_wiki_id = data.get('preWikiId')
    cur_data = Wiki.query.filter_by(id=cur_wiki_id).first()
    pre_data = Wiki.query.filter_by(id=pre_wiki_id).first()
    cur_data.num, pre_data.num = pre_data.num, cur_data.num
    db.session.commit()
    return jsonify({'msg': '上移成功', 'status': 1})

@api.route('/wiki/moveDown',methods=['POST'])
@login_required
def moveDown_wiki():
    """向下移动"""
    data = request.json
    cur_wiki_id = data.get('curWikiId')
    after_wiki_id = data.get('afterWikiId')
    cur_data = Wiki.query.filter_by(id=cur_wiki_id).first()
    after_data = Wiki.query.filter_by(id=after_wiki_id).first()
    cur_data.num,after_data.num = after_data.num,cur_data.num
    db.session.commit()
    return jsonify({'msg': '下移成功', 'status': 1})

@api.route('/wiki/annex', methods=['POST'])
@login_required
def del_annex():
    data = request.json
    wiki_id = data.get('wikiId')
    file_name = data.get('file_name')
    annex_name = json.dumps(data.get('annex_name'))

    if os.path.exists(os.path.join(FILE_ADDRESS, file_name)):
        os.remove(os.path.join(FILE_ADDRESS, file_name))

    old_data = Wiki.query.filter_by(id=wiki_id).first()
    old_data.annex_name = annex_name
    db.session.commit()
    return jsonify({"msg": "删除成功", "status": 1})


@api.route('/wiki/check', methods=['POST'])
@login_required
def check_annex():
    data = request.json
    file_name = data.get('file_name')
    if os.path.exists(os.path.join(FILE_ADDRESS, file_name)):
        return jsonify({"msg": "同名文件已存在，请修改名称后重试!", "status": 0})

    return jsonify({"msg": "可以上传", "status": 1})
