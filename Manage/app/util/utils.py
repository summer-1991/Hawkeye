# encoding: utf-8
import ast
import importlib
import json
import re
import types
import xlrd
import datetime
from .httprunner.parser import variable_regexp, function_regexp, function_regexp_compile


def auto_num(num, model, **kwargs):
    """自动返回编号的最大值"""
    if not num:
        if not model.query.filter_by(**kwargs).all():
            return 1
        else:
            return model.query.filter_by(**kwargs).order_by(model.num.desc()).first().num + 1
    return num


def num_sort(new_num, old_num, list_data, old_data):
    """修改排序,自动按新旧序号重新排列"""
    if old_data not in list_data:
        old_data.num = len(list_data) + 1
    else:
        _temp_data = list_data.pop(list_data.index(old_data))
        list_data.insert(new_num - 1, _temp_data)
        if old_num == new_num:
            pass
        elif old_num > new_num:
            for n, m in enumerate(list_data[new_num - 1:old_num + 1]):
                m.num = new_num + n

        elif old_data.num < new_num:
            for n, m in enumerate(list_data[old_num - 1:new_num + 1]):
                m.num = old_num + n


# variable_regexp = r"\$([\w_]+)"
# function_regexp = r"\$\{([\w_]+\([\$\w\.\-_ =,]*\))\}"
# function_regexp_compile = re.compile(r"^([\w_]+)\(([\$\w\.\-/_ =,]*)\)$")
# function_regexp_compile = re.compile(r"^([\w_]+)\(([\$\w\W\.\-/_ =,]*)\)$")


def extract_variables(content):
    """ extract all variable names from content, which is in format $variable
    @param (str) content
    @return (list) variable name list

    e.g. $variable => ["variable"]
         /blog/$postid => ["postid"]
         /$var1/$var2 => ["var1", "var2"]
         abc => []
    """
    try:
        return re.findall(variable_regexp, content)
    except TypeError:
        return []


def extract_functions(content):
    """ extract all functions from string content, which are in format ${fun()}
    @param (str) content
    @return (list) functions list

    e.g. ${func(5)} => ["func(5)"]
         ${func(a=1, b=2)} => ["func(a=1, b=2)"]
         /api_1_0/1000?_t=${get_timestamp()} => ["get_timestamp()"]
         /api_1_0/${add(1, 2)} => ["add(1, 2)"]
         "/api_1_0/${add(1, 2)}?_t=${get_timestamp()}" => ["add(1, 2)", "get_timestamp()"]
    """
    try:
        return re.findall(function_regexp, content)
    except TypeError:
        return []


def check_case(case_data, func_address):
    module_functions_dict = {}
    if func_address:
        for f in json.loads(func_address):
            import_path = 'func_list.{}'.format(f.replace('.py', ''))
            func_list = importlib.reload(importlib.import_module(import_path))
            module_functions_dict.update({name: item for name, item in vars(func_list).items() if
                                          isinstance(item, types.FunctionType)})
            # module_functions_dict = dict(filter(is_function, vars(func_list).items()))

    if isinstance(case_data, list):
        for c in case_data:
            json_c = json.dumps(c)
            num = json_c.count('$')
            variable_num = len(extract_variables(json_c))
            func_num = len(extract_functions(json_c))
            if not c['case_name']:
                return '存在没有命名的用例，请检查'
            if num != (variable_num + func_num):
                return '‘{}’用例存在格式错误的引用参数或函数'.format(c['case_name'])
            if func_address:
                for func in extract_functions(json_c):
                    func = func.split('(')[0]
                    if func not in module_functions_dict:
                        return '{}用例中的函数“{}”在文件引用中没有定义'.format(c['case_name'], func)

    else:
        num = case_data.count('$')
        variable_num = len(extract_variables(case_data))
        func_num = len(extract_functions(case_data))
        if num != (variable_num + func_num):
            return '‘业务变量’存在格式错误的引用参数或函数'
        if func_address:
            for func in extract_functions(case_data):
                func = func.split('(')[0]
                if func not in module_functions_dict:
                    return '函数“{}”在文件引用中没有定义'.format(func)


def convert(variable):
    """ 同层次参数中，存在引用关系就先赋值
    eg:
        phone:123
        name:$phone
        => phone:123
           name:123
    """
    _temp = json.dumps(variable)
    content = {v['key']: v['value'] for v in variable if v['key'] != ''}
    for variable_name in extract_variables(_temp):
        if content.get(variable_name):
            # content contains one or several variables
            _temp = _temp.replace(
                "${}".format(variable_name),
                str(content.get(variable_name)), 1
            )
            content = {v['key']: v['value'] for v in json.loads(_temp) if v['key'] != ''}

    return _temp


def change_cron(expression):
    args = {}
    expression = expression.split(' ')
    if expression[0] != '?':
        args['second'] = expression[0]
    if expression[1] != '?':
        args['minute'] = expression[1]
    if expression[2] != '?':
        args['hour'] = expression[2]
    if expression[3] != '?':
        args['day'] = expression[3]
    if expression[4] != '?':
        args['month'] = expression[4]
    if expression[5] != '?':
        args['day_of_week'] = expression[5]
    return args


def parse_string_value(str_value):
    """ parse string to number if possible
    e.g. "123" => 123
         "12.2" => 12.3
         "abc" => "abc"
         "$var" => "$var"
    """
    try:
        return ast.literal_eval(str_value)
    except ValueError:
        return str_value
    except SyntaxError:
        # e.g. $var, ${func}
        return str_value


def parse_function(content):
    """ parse function name and args from string content.

    Args:
        content (str): string content

    Returns:
        dict: function meta dict

            {
                "func_name": "xxx",
                "args": [],
                "kwargs": {}
            }

    Examples:
        >>> parse_function("func()")
        {'func_name': 'func', 'args': [], 'kwargs': {}}

        >>> parse_function("func(5)")
        {'func_name': 'func', 'args': [5], 'kwargs': {}}

        >>> parse_function("func(1, 2)")
        {'func_name': 'func', 'args': [1, 2], 'kwargs': {}}

        >>> parse_function("func(a=1, b=2)")
        {'func_name': 'func', 'args': [], 'kwargs': {'a': 1, 'b': 2}}

        >>> parse_function("func(1, 2, a=3, b=4)")
        {'func_name': 'func', 'args': [1, 2], 'kwargs': {'a':3, 'b':4}}

    """
    matched = function_regexp_compile.match(content)
    function_meta = {
        "func_name": matched.group(1),
        "args": [],
        "kwargs": {}
    }

    args_str = matched.group(2).strip()
    if args_str == "":
        return function_meta

    args_list = args_str.split(',')
    for arg in args_list:
        arg = arg.strip()
        if '=' in arg:
            key, value = arg.split('=')
            function_meta["kwargs"][key.strip()] = parse_string_value(value.strip())
        else:
            function_meta["args"].append(parse_string_value(arg))

    return function_meta


def encode_object(obj):
    """ json.dumps转化时，先把属于bytes类型的解码，若解码失败返回str类型，和其他对象属性统一转化成str"""
    if isinstance(obj, bytes):
        try:
            return bytes.decode(obj)
        except Exception as e:
            return str(obj)
    else:
        return str(obj)

    # raise TypeError("{} is not JSON serializable".format(obj))


def read_excel(file_path):
    data = xlrd.open_workbook(file_path)
    # 根据工作表的名称获取工作表中的内容（方式①）
    table = data.sheet_by_index(0)
    # 获取第一行所有内容,如果括号中1就是第二行，这点跟列表索引类似
    keys = table.row_values(0)
    # 获取工作表的有效行数
    row_num = table.nrows
    # 获取工作表的有效列数
    col_num = table.ncols

    _data = []
    for i in range(1, row_num):
        # 定义一个空字典
        sheet_data = {}
        for j in range(col_num):
            # 获取单元格数据类型
            c_type = table.cell(i, j).ctype
            # 获取单元格数据
            c_cell = table.cell_value(i, j)
            if c_type == 2 and c_cell % 1 == 0:  # 如果是整形
                c_cell = int(c_cell)
            elif c_type == 3:
                # 转成datetime对象
                date = datetime.datetime(xlrd.xldate_as_tuple(c_cell, 0))
                c_cell = date.strftime('%Y/%d/%m %H:%M:%S')
            elif c_type == 4:
                c_cell = True if c_cell == 1 else False
            sheet_data[keys[j]] = c_cell
            # 循环每一个有效的单元格，将字段与值对应存储到字典中
            # 字典的key就是excel表中每列第一行的字段
            # sheet_data[self.keys[j]] = self.table.row_values(i)[j]
        # 再将字典追加到列表中
        _data.append(sheet_data)
    # 返回从excel中获取到的数据：以列表存字典的形式返回
    return {'key': keys, 'value': _data}


if __name__ == '__main__':
    # func_list = importlib.reload(importlib.import_module(r"func_list.abuild_in_fun.py"))
    # module_functions_dict = {name: item for name, item in vars(func_list).items() if
    #                          isinstance(item, types.FunctionType)}
    # print(module_functions_dict)
    a = '${func({"birthday": "199-02-02"; "expire_age": "65周岁"; "sex": "2"},123,3245)}'
    b = '${func([123],123)}'
    print(extract_functions(a))
    # matched = parse_function(extract_functions(b)[0])
    #
    # print(matched)
