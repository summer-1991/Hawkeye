from flask import jsonify, request
from . import api, login_required
from app.models import *
import time


@api.route('/gantt/find', methods=['POST'])
@login_required
def find_gantt_tasks():
    """ 查信息 """
    _data = GanttData.query.order_by(GanttData.id.asc())
    _link = GanttLink.query.order_by(GanttLink.id.asc())

    end_data = [{'id': item.id,
                 'text': item.text,
                 'start_date': item.start_date,
                 'end_date': item.end_date,
                 'duration': item.duration,
                 'progress': (item.progress) / 100,
                 'parent': item.parent}
                for item in _data]
    end_link = [{'id': item.id,
                 'source': item.source,
                 'target': item.target,
                 'type': item.type}
                for item in _link]
    return jsonify({'data': end_data, 'link': end_link, 'status': 1})


@api.route('/gantt/update', methods=['POST'])
@login_required
def update_gantt_tasks():
    """ 保存 """
    data = request.json
    item = data.get('item')
    features = data.get('update_by')

    if 'id' in item:
        item_id = item['id']
        _data = globals()[features].query.filter_by(id=item_id).first()
        if features == 'GanttData':
            _data.text = item['text']
            _data.start_date = str(time.strftime("%d-%m-%Y", time.localtime(item['start_date'])))
            _data.end_date = str(time.strftime("%d-%m-%Y", time.localtime(item['end_date'])))
            _data.duration = item['duration']
            _data.progress = round(item['progress'] * 100)
            _data.parent = item['parent']
        else:
            _data.source = item['source']
            _data.target = item['target']
            _data.type = item['type']

        db.session.commit()
        return jsonify({'msg': '更新成功', 'status': 1})
    else:
        if features == 'GanttData':
            text = item['text']
            start_date = time.strftime("%d-%m-%Y", time.localtime(item['start_date']))
            end_date = time.strftime("%d-%m-%Y", time.localtime(item['end_date']))
            duration = item['duration']
            progress = round(item['progress'] * 100)
            parent = item['parent']

            new_item = GanttData(text=text,
                                 start_date=str(start_date),
                                 duration=duration,
                                 end_date=str(end_date),
                                 progress=progress,
                                 parent=parent)
        else:
            source = item['source']
            target = item['target']
            item_type = item['type']

            new_item = GanttLink(source=source,
                                 target=target,
                                 type=item_type)

        db.session.add(new_item)
        db.session.commit()
        return jsonify({'msg': '新建成功', 'status': 1, 'id': new_item.id})


@api.route('/gantt/del', methods=['POST'])
@login_required
def del_gantt_tasks():
    """ 删除 """
    data = request.json
    item_id = data.get('id')
    features = data.get('update_by')
    _data = globals()[features].query.filter_by(id=item_id).first()
    if _data:
        db.session.delete(_data)
        return jsonify({'msg': '删除成功', 'status': 1})

    return jsonify({'msg': '已被删除', 'status': 0})
