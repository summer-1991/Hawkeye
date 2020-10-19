import ast
import json
import types
import time
import hashlib
from app.models import *
from .httprunner.api import HttpRunner
from ..util.global_variable import *
from ..util.utils import encode_object
import importlib
from app import scheduler
from flask.json import JSONEncoder


class RunCase(object):
    def __init__(self, project_ids=None):
        self.project_ids = project_ids
        self.pro_environment = None
        self.pro_base_url = None
        self.new_report_id = None
        self.TEST_DATA = {'testcases': [], 'project_mapping': {'functions': {}, 'variables': {}}}
        self.init_project_data()

    def init_project_data(self):
        pro_data = Project.query.filter_by(id=self.project_ids).first()
        self.pro_base_url = [json.loads(pro_data.host), json.loads(pro_data.host_two), json.loads(pro_data.host_three),
                             json.loads(pro_data.host_four)]
        # for pro_data in Project.query.all():
        if pro_data.environment_choice == 'first':
            self.pro_environment = json.loads(pro_data.host)
        elif pro_data.environment_choice == 'second':
            self.pro_environment = json.loads(pro_data.host_two)
        if pro_data.environment_choice == 'third':
            self.pro_environment = json.loads(pro_data.host_three)
        if pro_data.environment_choice == 'fourth':
            self.pro_environment = json.loads(pro_data.host_four)
        # self.pro_base_url = pro_base_url
        self.pro_config(Project.query.filter_by(id=self.project_ids).first())

    def pro_config(self, project_data):
        """
        把project的配置数据解析出来
        :param project_data:
        :return:
        """
        self.TEST_DATA['project_mapping']['variables'] = {h['key']: h['value'] for h in
                                                          json.loads(project_data.variables) if h.get('key')}
        if project_data.func_file:
            self.extract_func([project_data.func_file.replace('.py', '')])

    def extract_func(self, func_list):
        for f in func_list:
            func_list = importlib.reload(importlib.import_module('func_list.{}'.format(f)))
            module_functions_dict = {name: item for name, item in vars(func_list).items()
                                     if isinstance(item, types.FunctionType)}
            self.TEST_DATA['project_mapping']['functions'].update(module_functions_dict)

    def assemble_step(self, api_id=None, step_data=None, pro_base_url=None, status=False, case_url_flag=None):
        """
        :param api_id:
        :param step_data:
        :param pro_base_url:
        :param status: 判断是接口调试(false)or业务用例执行(true)
        :return:
        """
        if status:
            # 为true，获取api基础信息；case只包含可改变部分所以还需要api基础信息组合成全新的用例
            api_data = ApiMsg.query.filter_by(id=step_data.api_msg_id).first()
        else:
            # 为false，基础信息和参数信息都在api里面，所以api_case = case_data，直接赋值覆盖
            api_data = ApiMsg.query.filter_by(id=api_id).first()
            step_data = api_data
            # api_data = case_data

        _data = {'name': step_data.name,
                 'request': {'method': api_data.method,

                             'files': {},
                             'data': {}}}

        # _data['request']['headers'] = {h['key']: h['value'] for h in json.loads(api_data.header)
        #                                if h['key']} if json.loads(api_data.header) else {}

        if api_data.status_url != '-1':
            if case_url_flag == 1 or case_url_flag == None:
                pro_env_url = pro_base_url[api_data.environment]
                _data['request']['url'] = pro_env_url[int(api_data.status_url)] + api_data.url.split('?')[0]
            else:
                pro_env_url = pro_base_url
                _data['request']['url'] = pro_env_url + api_data.url.split('?')[0]
        else:
            _data['request']['url'] = api_data.url

        if 'https' in _data['request']['url']:
            _data['request']['verify'] = False

        if step_data.up_func:
            # _data['setup_hooks'] = [step_data.up_func]
            setup_hooks_list = []
            setup_hooks_str = step_data.up_func
            for temp_str in setup_hooks_str.split(','):
                if ":" in temp_str:
                    setup_hooks_list.append(eval(temp_str))
                else:
                    setup_hooks_list.append(temp_str)
            _data['setup_hooks'] = setup_hooks_list

        if step_data.down_func:
            # _data['teardown_hooks'] = [step_data.down_func]
            teardown_hooks_list = []
            teardown_hooks_str = step_data.down_func
            for temp_str in teardown_hooks_str.split(','):
                if ":" in temp_str:
                    teardown_hooks_list.append(eval(temp_str))
                else:
                    teardown_hooks_list.append(temp_str)
            _data['teardown_hooks'] = teardown_hooks_list

        if step_data.skip:
            _data['skipIf'] = step_data.skip
        if status:
            _data['times'] = step_data.time
            if json.loads(step_data.status_param)[0]:
                if json.loads(step_data.status_param)[1]:
                    _param = json.loads(step_data.param)
                else:
                    _param = json.loads(api_data.param)
            else:
                _param = None

            if json.loads(step_data.status_variables)[0]:
                if json.loads(step_data.status_variables)[1]:
                    _json_variables = step_data.json_variable
                    _variables = json.loads(step_data.variable)
                else:
                    _json_variables = api_data.json_variable
                    _variables = json.loads(api_data.variable)
            else:
                _json_variables = None
                _variables = None

            if json.loads(step_data.status_extract)[0]:
                if json.loads(step_data.status_extract)[1]:
                    _extract = step_data.extract
                else:
                    _extract = api_data.extract
            else:
                _extract = None

            if json.loads(step_data.status_validate)[0]:
                if json.loads(step_data.status_validate)[1]:
                    _validate = step_data.validate
                else:
                    _validate = api_data.validate
            else:
                _validate = None

            if json.loads(step_data.status_header)[0]:
                if json.loads(step_data.status_header)[1]:
                    _header = json.loads(step_data.header)
                else:
                    _header = json.loads(api_data.header)
            else:
                _header = None

        else:
            _param = json.loads(api_data.param)
            _json_variables = api_data.json_variable
            _variables = json.loads(api_data.variable)
            _header = json.loads(api_data.header)
            _extract = api_data.extract
            _validate = api_data.validate

        _data['request']['params'] = {param['key']: param['value'].replace('%', '&') for param in
                                      _param if param.get('key')} if _param else {}

        if api_data.sig != -1:
            _data['request']['params'] = self.param_md5(_data['request']['params'])

        _data['request']['headers'] = {headers['key']: headers['value'].replace('%', '&') for headers in
                                       _header if headers.get('key')} if _header else {}

        _data['extract'] = [{ext['key']: ext['value']} for ext in json.loads(_extract) if
                            ext.get('key')] if _extract else []

        _data['validate'] = [{val['comparator']: [val['key'], ast.literal_eval(val['value'])]} for val in
                             json.loads(_validate) if val.get('key')] if _validate else []

        if api_data.method == 'GET':

            pass
        # elif _variables:
        #     print(_variables)
        #     print(111)
        elif api_data.variable_type == 'text' and _variables:
            for variable in _variables:
                if variable['param_type'] == 'string' and variable.get('key'):
                    _data['request']['files'].update({variable['key']: (None, variable['value'])})
                elif variable['param_type'] == 'file' and variable.get('key'):
                    _data['request']['files'].update({variable['key']: (
                        variable['value'].split('/')[-1], open(variable['value'], 'rb'),
                        CONTENT_TYPE['.{}'.format(variable['value'].split('.')[-1])])})

        elif api_data.variable_type == 'data' and _variables:
            for variable in _variables:
                if variable['param_type'] == 'string' and variable.get('key'):
                    _data['request']['data'].update({variable['key']: variable['value']})
                elif variable['param_type'] == 'file' and variable.get('key'):
                    _data['request']['files'].update({variable['key']: (
                        variable['value'].split('/')[-1], open(variable['value'], 'rb'),
                        CONTENT_TYPE['.{}'.format(variable['value'].split('.')[-1])])})

        elif api_data.variable_type == 'json':
            if _json_variables:
                _data['request']['json'] = json.loads(_json_variables)

        return _data

    def get_api_test(self, api_ids, config_id):
        scheduler.app.logger.info('本次测试的接口id：{}'.format(api_ids))
        _steps = {'teststeps': [], 'config': {'variables': {}}}

        if config_id:
            config_data = Config.query.filter_by(id=config_id).first()
            _config = json.loads(config_data.variables) if config_id else []
            _steps['config']['variables'].update({v['key']: v['value'] for v in _config if v['key']})
            self.extract_func(['{}'.format(f.replace('.py', '')) for f in json.loads(config_data.func_address)])

        _steps['teststeps'] = [self.assemble_step(api_id, None, self.pro_base_url, False, None) for api_id in api_ids]
        self.TEST_DATA['testcases'].append(_steps)

    def get_case_test(self, case_ids):
        scheduler.app.logger.info('本次测试的用例id：{}'.format(case_ids))
        for case_id in case_ids:
            case_data = Case.query.filter_by(id=case_id).first()
            case_times = case_data.times if case_data.times else 1

            if case_data.environment == -1 or case_data.environment == None:
                url_environment = self.pro_base_url
                case_url_flag = 1
            else:
                url_environment = self.pro_base_url[case_data.environment][int(case_data.status_url)]
                case_url_flag = 2
            for s in range(case_times):
                _steps = {'teststeps': [], 'config': {'variables': {}, 'name': ''}}
                _steps['config']['name'] = case_data.name

                # 获取业务集合的配置数据
                _config = json.loads(case_data.variable) if case_data.variable else []
                _steps['config']['variables'].update({v['key']: v['value'] for v in _config if v['key']})

                # # 获取需要导入的函数
                self.extract_func(['{}'.format(f.replace('.py', '')) for f in json.loads(case_data.func_address)])

                for _step in CaseData.query.filter_by(case_id=case_id).order_by(CaseData.num.asc()).all():
                    if _step.status == 'true':  # 判断用例状态，是否执行
                        _steps['teststeps'].append(
                            self.assemble_step(None, _step, url_environment, True, case_url_flag))
                self.TEST_DATA['testcases'].append(_steps)

    def build_report(self, jump_res, case_ids, performer):
        # if self.run_type and self.make_report:
        new_report = Report(performer=performer,
                            case_names=','.join(
                                [Case.query.filter_by(id=scene_id).first().name for scene_id in case_ids]),
                            project_id=self.project_ids, read_status='待阅')
        db.session.add(new_report)
        db.session.commit()

        self.new_report_id = new_report.id
        with open('{}{}.txt'.format(REPORT_ADDRESS, self.new_report_id), 'w') as f:
            f.write(jump_res)

    def run_case(self):
        scheduler.app.logger.info('测试数据：{}'.format(self.TEST_DATA))
        # res = main_ate(self.TEST_DATA)
        runner = HttpRunner()
        # self.TEST_DATA['testcases'][0]['config']['parameters'] = {'passwords': [123456, 12345, 1234]}
        # self.TEST_DATA['config'] = {}
        # self.TEST_DATA['config']['parameters'] = {'password': [123456, 12345, 1234]}
        # self.TEST_DATA = {'testsuites': [self.TEST_DATA], 'parameters': [123456, 12345, 1234]}

        runner.run(self.TEST_DATA)
        jump_res = json.dumps(runner._summary, ensure_ascii=False, default=encode_object, cls=JSONEncoder)
        # scheduler.app.logger.info('返回数据：{}'.format(jump_res))
        return jump_res

    def param_md5(self, param):
        if not param:
            param = {}

        if not param.get('clientid'):
            clientid = ""
        else:
            clientid = param['clientid']

        if not param.get('timestamp'):
            timestamp = int(time.time())
            param['timestamp'] = str(timestamp)
        else:
            timestamp = param['timestamp']

        client_key = ''
        client_enum = CommonConfig.query.filter_by(c_key=clientid, c_type='client').first()
        if client_enum:
            client_key = client_enum.c_value
        original_str = client_key + str(timestamp)

        md5 = hashlib.md5()
        b = original_str.encode(encoding='UTF-8')
        md5.update(b)
        str_md5 = md5.hexdigest()

        param['sig'] = str_md5
        return param
