# encoding: utf-8
from werkzeug.security import check_password_hash, generate_password_hash
from . import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from collections import OrderedDict

roles_permissions = db.Table('roles_permissions',
                             db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
                             db.Column('permission_id', db.Integer, db.ForeignKey('permission.id')))

projects_users = db.Table('projects_users',
                          db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
                          db.Column('user_id', db.Integer, db.ForeignKey('users.id')))


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True, comment='主键，自增')
    name = db.Column(db.String(30), unique=True, comment='角色名称')
    auth = db.Column(db.Text(), comment='权限配置')
    users = db.relationship('User', back_populates='role')
    permission = db.relationship('Permission', secondary=roles_permissions, back_populates='role')

    @staticmethod
    def init_role():
        roles_permissions_map = OrderedDict()
        roles_permissions_map[u'测试人员'] = ['COMMON']
        roles_permissions_map[u'管理员'] = ['COMMON', 'ADMINISTER']
        for role_name in roles_permissions_map:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
                db.session.add(role)
                role.permission = []
            for permission_name in roles_permissions_map[role_name]:
                permission = Permission.query.filter_by(name=permission_name).first()
                if permission is None:
                    permission = Permission(name=permission_name)
                    db.session.add(permission)
                role.permission.append(permission)
                db.session.commit()
        print('Role and permission created successfully')


class Permission(db.Model):
    __tablename__ = 'permission'
    id = db.Column(db.Integer, primary_key=True, comment='主键，自增')
    name = db.Column(db.String(30), unique=True, comment='权限名称')
    role = db.relationship('Role', secondary=roles_permissions, back_populates='permission')


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, comment='主键，自增')
    account = db.Column(db.String(64), unique=True, index=True, comment='账号')
    password_hash = db.Column(db.String(128), comment='密码')
    name = db.Column(db.String(64), comment='姓名')
    status = db.Column(db.Integer, comment='状态，1为启用，2为冻结')
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), comment='所属的角色id')
    role = db.relationship('Role', back_populates='users')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now)
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)
    projects = db.relationship('Project', secondary=projects_users, back_populates='users')

    @staticmethod
    def init_user():
        user = User.query.filter_by(name='管理员').first()
        if user:
            print('The administrator account already exists')
            print('--' * 30)
            return
        else:
            user = User(name=u'管理员', account='admin', password='123456', status=1, role_id=2)
            db.session.add(user)
            db.session.commit()
            print('Administrator account created successfully')
            print('--' * 30)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def can(self, permission_name):
        permission = Permission.query.filter_by(name=permission_name).first()
        return permission is not None and self.role is not None and permission in self.role.permission


class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    user_id = db.Column(db.Integer(), nullable=True, comment='所属的用户id')
    name = db.Column(db.String(64), nullable=True, unique=True, comment='项目名称')
    host = db.Column(db.Text(), nullable=True, comment='测试环境')
    environment_choice = db.Column(db.String(16), comment='环境选择，testPre为测试预发，以此类推')
    principal = db.Column(db.String(16), nullable=True)
    variables = db.Column(db.String(2048), comment='项目的公共变量')
    headers = db.Column(db.String(1024), comment='项目的公共头部信息')
    func_file = db.Column(db.String(64), nullable=True, unique=True, comment='函数文件')
    modules = db.relationship('Module', order_by='Module.num.asc()', lazy='dynamic')
    configs = db.relationship('Config', order_by='Config.num.asc()', lazy='dynamic')
    case_sets = db.relationship('CaseSet', order_by='CaseSet.num.asc()', lazy='dynamic')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)
    users = db.relationship('User', secondary=projects_users, back_populates='projects')


class Module(db.Model):
    __tablename__ = 'module'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    name = db.Column(db.String(64), nullable=True, comment='接口模块')
    num = db.Column(db.Integer(), nullable=True, comment='模块序号')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), comment='所属的项目id')
    api_msg = db.relationship('ApiMsg', order_by='ApiMsg.num.asc()', lazy='dynamic')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class Config(db.Model):
    __tablename__ = 'config'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    num = db.Column(db.Integer(), nullable=True, comment='配置序号')
    name = db.Column(db.String(128), comment='配置名称')
    variables = db.Column(db.String(21000), comment='配置参数')
    func_address = db.Column(db.String(128), comment='配置函数')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), comment='所属的项目id')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class CaseSet(db.Model):
    __tablename__ = 'case_set'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    num = db.Column(db.Integer(), nullable=True, comment='用例集合序号')
    name = db.Column(db.String(256), nullable=True, comment='用例集名称')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), comment='所属的项目id')
    cases = db.relationship('Case', order_by='Case.num.asc()', lazy='dynamic')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class Case(db.Model):
    __tablename__ = 'case'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    num = db.Column(db.Integer(), nullable=True, comment='用例序号')
    name = db.Column(db.String(128), nullable=True, comment='用例名称')
    desc = db.Column(db.String(256), comment='用例描述')
    func_address = db.Column(db.String(256), comment='用例需要引用的函数')
    variable = db.Column(db.Text(), comment='用例公共参数')
    times = db.Column(db.Integer(), nullable=True, comment='执行次数')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), comment='所属的项目id')
    case_set_id = db.Column(db.Integer, db.ForeignKey('case_set.id'), comment='所属的用例集id')
    client = db.Column(db.String(10), comment='选择的租户id')
    environment = db.Column(db.String(10), comment='环境类型')
    status_url = db.Column(db.String(32), nullable=True, comment='基础url,序号对应项目的环境')
    gm = db.Column(db.String(256), nullable=True, comment='待替换的gm_url')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class ApiMsg(db.Model):
    __tablename__ = 'api_msg'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    num = db.Column(db.Integer(), nullable=True, comment='接口序号')
    name = db.Column(db.String(128), nullable=True, comment='接口名称')
    desc = db.Column(db.String(256), nullable=True, comment='接口描述')
    variable_type = db.Column(db.String(32), nullable=True, comment='参数类型选择')
    environment = db.Column(db.String(10), comment='环境类型')
    status_url = db.Column(db.String(32), nullable=True, comment='基础url,序号对应项目的环境')
    up_func = db.Column(db.String(128), comment='接口执行前的函数')
    down_func = db.Column(db.String(128), comment='接口执行后的函数')
    method = db.Column(db.String(32), nullable=True, comment='请求方式')
    variable = db.Column(db.Text(), comment='form-data形式的参数')
    json_variable = db.Column(db.Text(), comment='json形式的参数')
    param = db.Column(db.Text(), comment='url上面所带的参数')
    url = db.Column(db.String(256), nullable=True, comment='接口地址')
    skip = db.Column(db.String(256), comment='跳过判断')
    extract = db.Column(db.String(2048), comment='提取信息')
    validate = db.Column(db.String(2048), comment='断言信息')
    header = db.Column(db.String(2048), comment='头部信息')
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), comment='所属的接口模块id')
    project_id = db.Column(db.Integer, nullable=True, comment='所属的项目id')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now)
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)
    client = db.Column(db.String(10), comment='选择的租户id')
    sig = db.Column(db.Integer(), nullable=True, default=0, comment='加签方式')


class CaseData(db.Model):
    __tablename__ = 'case_data'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    num = db.Column(db.Integer(), nullable=True, comment='步骤序号，执行顺序按序号来')
    status = db.Column(db.String(16), comment='状态，true表示执行，false表示不执行')
    name = db.Column(db.String(128), comment='步骤名称')
    up_func = db.Column(db.String(256), comment='步骤执行前的函数')
    down_func = db.Column(db.String(256), comment='步骤执行后的函数')
    skip = db.Column(db.String(64), comment='跳过判断函数')
    time = db.Column(db.Integer(), default=1, comment='执行次数')
    param = db.Column(db.Text(), default=u'[]')
    status_param = db.Column(db.String(64), default=u'[true, true]')
    variable = db.Column(db.Text())
    json_variable = db.Column(db.Text())
    status_variables = db.Column(db.String(64))
    extract = db.Column(db.String(2048))
    status_extract = db.Column(db.String(64))
    validate = db.Column(db.String(2048))
    status_validate = db.Column(db.String(64))
    header = db.Column(db.String(2048))
    status_header = db.Column(db.String(64))
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'))
    api_msg_id = db.Column(db.Integer, db.ForeignKey('api_msg.id'))
    created_time = db.Column(db.DateTime, index=True, default=datetime.now)
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class Report(db.Model):
    __tablename__ = 'report'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    case_names = db.Column(db.String(128), nullable=True, comment='用例的名称集合')
    read_status = db.Column(db.String(16), nullable=True, comment='阅读状态')
    performer = db.Column(db.String(16), nullable=True, comment='执行者')
    project_id = db.Column(db.String(16), nullable=True)
    create_time = db.Column(db.DateTime(), index=True, default=datetime.now)


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True, comment='主键，自增')
    num = db.Column(db.Integer(), comment='任务序号')
    task_name = db.Column(db.String(64), comment='任务名称')
    task_config_time = db.Column(db.String(256), nullable=True, comment='cron表达式')
    set_id = db.Column(db.String(2048))
    case_id = db.Column(db.String(2048))
    task_type = db.Column(db.String(16))
    task_to_email_address = db.Column(db.String(256), comment='收件人邮箱')
    task_send_email_address = db.Column(db.String(256), comment='发件人邮箱')
    email_password = db.Column(db.String(256), comment='发件人邮箱密码')
    status = db.Column(db.String(16), default=u'创建', comment='任务的运行状态，默认是创建')
    project_id = db.Column(db.String(16), nullable=True)
    environment = db.Column(db.String(10), comment='环境类型')
    url_index = db.Column(db.Integer(), comment='选择的url的index')
    status_url = db.Column(db.String(100), comment='基础url')
    gm = db.Column(db.String(256), nullable=True, comment='待替换的gm_url')
    json_variable = db.Column(db.Text(), comment='json形式的参数')
    client = db.Column(db.String(10), comment='租户id')
    created_time = db.Column(db.DateTime(), default=datetime.now, comment='任务的创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class TestCaseFile(db.Model):
    __tablename__ = 'test_case_file'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    num = db.Column(db.Integer(), nullable=True, comment='测试用例文件序号')
    name = db.Column(db.String(128), nullable=True, comment='测试用例文件名称')

    status = db.Column(db.Integer(), comment='0代表文件夹；1代表用例文件')
    higher_id = db.Column(db.Integer(), comment='上级id，父级为0')
    user_id = db.Column(db.Integer(), comment='创建人id')
    file_type = db.Column(db.String(1), comment='x代表脑图，m代表excel')
    operator_id = db.Column(db.Integer(), default=0, comment='此时打开人')

    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class DocLib(db.Model):
    __tablename__ = 'doc_lib'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    name = db.Column(db.String(64), nullable=True, comment='文档库')
    num = db.Column(db.Integer(), nullable=True, comment='库序号')
    project_id = db.Column(db.Integer(), nullable=True, comment='所属的项目id')
    wiki = db.relationship('Wiki', order_by='Wiki.num.asc()', lazy='dynamic')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class Wiki(db.Model):
    __tablename__ = 'wiki'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    num = db.Column(db.Integer(), nullable=True, comment='文档序号')
    module_id = db.Column(db.Integer(), db.ForeignKey('doc_lib.id'), comment='所属的文档库id')
    user_id = db.Column(db.Integer(), comment='创建人id')
    name = db.Column(db.String(50), comment='文档名称')
    annex_name = db.Column(db.Text(), comment='附件名称')
    auth = db.Column(db.Integer(), comment='开放程度0公开，1人员，2预留')
    team = db.Column(db.String(50), comment='人员名单')
    desc = db.Column(db.String(100), comment='描述')

    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class ManualSet(db.Model):
    __tablename__ = 'manual_set'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    name = db.Column(db.String(64), nullable=True, comment='测试集')
    num = db.Column(db.Integer(), nullable=True, comment='集序号')
    project_id = db.Column(db.Integer(), nullable=True, comment='所属的项目id')
    manual_case = db.relationship('ManualCase', order_by='ManualCase.case_type.asc()', lazy='dynamic')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class ManualCase(db.Model):
    __tablename__ = 'manual_case'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    module_id = db.Column(db.Integer(), db.ForeignKey('manual_set.id'), comment='所属的测试集id')
    user_id = db.Column(db.Integer(), comment='创建人id')
    name = db.Column(db.String(50), comment='用例名称')
    desc = db.Column(db.String(100), comment='用例描述')
    case_type = db.Column(db.Integer(), nullable=True, comment='用例类型')
    precondition = db.Column(db.Text(), comment='前提条件')
    steps = db.Column(db.Text(), comment='执行步骤')
    expect = db.Column(db.Text(), comment='期望结果')
    case_from = db.Column(db.String(10), comment='用例来源')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class ManualTask(db.Model):
    __tablename__ = 'manual_task'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    name = db.Column(db.String(64), nullable=True, comment='测试任务')
    num = db.Column(db.Integer(), nullable=True, comment='任务号')
    project_id = db.Column(db.Integer(), nullable=True, comment='所属的项目id')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class ManualTasksCases(db.Model):
    __tablename__ = 'manual_tasks_cases'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    task_id = db.Column(db.Integer(), db.ForeignKey('manual_task.id'), comment='测试任务id')
    case_id = db.Column(db.Integer(), db.ForeignKey('manual_case.id'), comment='测试用例id')
    last_by = db.Column(db.String(50), comment='最后执行人')
    last_res = db.Column(db.Integer(), comment='执行结果')
    count = db.Column(db.Integer(), comment='测试执行次数')
    desc = db.Column(db.String(200), comment='执行描述')
    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class CommonConfig(db.Model):
    __tablename__ = 'common_config'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    c_type = db.Column(db.String(10), comment='设置类型')
    c_key = db.Column(db.String(20), comment='一般为key，如服务id')
    c_value = db.Column(db.String(100), comment='一般为value，如服务密钥')
    desc = db.Column(db.String(200), comment='备注')

    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class GanttData(db.Model):
    __tablename__ = 'gantt_data'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    text = db.Column(db.String(50), comment='任务名称')
    start_date = db.Column(db.String(30), comment='开始时间')
    duration = db.Column(db.Integer(), comment='持续时间')
    end_date = db.Column(db.String(30), comment='结束时间')
    progress = db.Column(db.Integer(), comment='执行百分比')
    parent = db.Column(db.Integer(), comment='甘特父id')

    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class GanttLink(db.Model):
    __tablename__ = 'gantt_link'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    source = db.Column(db.Integer(), comment='上一节点id')
    target = db.Column(db.Integer(), comment='下一节点id')
    type = db.Column(db.String(1), comment='样式')

    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


class TestResource(db.Model):
    __tablename__ = 'test_resource'
    id = db.Column(db.Integer(), primary_key=True, comment='主键，自增')
    name = db.Column(db.String(30), comment='型号/名称')
    desc = db.Column(db.String(200), comment='描述')
    version = db.Column(db.String(50), comment='版本')
    borrower = db.Column(db.String(10), comment='借用人')
    type = db.Column(db.Integer(), comment='资源类型')

    created_time = db.Column(db.DateTime, index=True, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, index=True, default=datetime.now, onupdate=datetime.now)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
