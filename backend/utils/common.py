import copy
import datetime
import re
import time
import socket

from bson import ObjectId

re_escapes = ['\\', '/', '*', '.', '?', '+', '$', '^', '[', ']', '(', ')', '{', '}', '|']


def format_escapes(input, escapes=re_escapes):
    if not isinstance(input, str):
        return input
    else:
        for escape in escapes:
            input = input.replace(escape, '\\' + escape)
        return input


def get_total_num_and_arranged_data(raw_model, query_res, fuzzy_fields=None):
    query_dict = query_res.to_dict() if query_res.to_dict() else {}
    if fuzzy_fields is not None:
        if not isinstance(fuzzy_fields, list):
            raise TypeError('fuzzy_fields need to be list.')
        for fuzzy_field in fuzzy_fields:
            if not isinstance(fuzzy_field, str):
                raise TypeError('fuzzy_field need to be str')
            if fuzzy_field in query_dict and can_convert_to_str(query_dict[fuzzy_field]):
                pre_compiled_str = format_escapes(str(query_dict[fuzzy_field]))
                query_dict[fuzzy_field] = re.compile(pre_compiled_str)
    query_dic = format_js_dic_to_python_dic(query_dict)
    raw_model_copy = copy.deepcopy(raw_model)
    raw_model_data_copy = []
    if not isinstance(raw_model_copy.find(), list):
        try:
            raw_model_data_copy = list(raw_model_copy.find({'isDeleted': {"$ne": True}}))
        except BaseException as e:
            raise TypeError('raw_data cannot convert to list: %s' % e)
    if not isinstance(query_dic, dict):
        raise TypeError('query_dic must be dict')

    skip = int(query_dic.get('skip')) if can_convert_to_int(query_dic.get('skip')) else 0
    size = int(query_dic.get('size')) if can_convert_to_int(query_dic.get('size')) else None
    sort_by = query_dic.get('sortBy')
    order = query_dic.get('order')

    query_dic.pop('skip') if query_dic.get('skip') else None
    query_dic.pop('size') if query_dic.get('size') else None
    query_dic.pop('sortBy') if query_dic.get('sortBy') else None
    query_dic.pop('order') if query_dic.get('order') else None

    if not query_dic == {}:
        query_dic['isDeleted'] = {"$ne": True}
        total_num = len(list(raw_model_copy.find(query_dic)))
    else:
        total_num = len(raw_model_data_copy)
    if sort_by and order and format_order(order):
        sort_query = [(sort_by, format_order(order))]
    else:
        sort_query = None
    query_dic['isDeleted'] = {"$ne": True}

    if skip is 0 and not size:
        if sort_query:
            arranged_data = raw_model_copy.find(query_dic, sort=sort_query)
        else:
            arranged_data = raw_model_copy.find(query_dic)
    else:
        if sort_query:
            arranged_data = raw_model_copy.find(query_dic).sort(sort_query).skip(skip).limit(size)
        else:
            arranged_data = raw_model_copy.find(query_dic).skip(skip).limit(size)

    return total_num, list(map(format_response_in_dic, map(raw_model_copy.filter_field, arranged_data)))


def format_js_dic_to_python_dic(query_dic):
    if not isinstance(query_dic, dict):
        raise TypeError('query_dic must be dict')
    for key, value in query_dic.items():
        if value == 'true':
            query_dic[key] = True
        if value == 'false':
            query_dic[key] = False
        if str(key)[-2:] == 'Id':
            query_dic[key] = ObjectId(value)
        if str(key) == '_id':
            try:
                query_dic[key] = ObjectId(value)
            except BaseException as e:
                print(e)
    return query_dic


def can_convert_to_int(input):
    try:
        int(input)
        return True
    except BaseException:
        return False


def can_convert_to_str(input):
    try:
        str(input)
        return True
    except BaseException:
        return False


def can_convert_to_float(input):
    try:
        float(input)
        return True
    except BaseException:
        return False


def format_order(raw_order):
    if not isinstance(raw_order, str):
        raise TypeError('raw_order must be str!')
    if 'desc' in raw_order:
        return -1
    elif 'asc' in raw_order:
        return 1
    else:
        return None


def is_valid_email(email):
    re_email = re.compile(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$')
    if re_email.match(email):
        return True
    else:
        return False


def format_response_in_dic(dic, is_format_object_id=True, is_format_datetime=True, is_filter_isDeleted=True,
                           timedelta=None):
    if timedelta is None:
        timedelta = get_offset_between_local_and_utc()
    if not isinstance(dic, dict):
        raise ValueError("input must be a dict!")
    if is_filter_isDeleted:
        if 'isDeleted' in dic and dic["isDeleted"] is True:
            return None
    if is_format_datetime:
        for key, value in dic.items():
            if isinstance(value, dict):
                dic[key] = format_response_in_dic(value)
            if isinstance(value, list):
                for index, value_piece in enumerate(value):
                    if isinstance(value_piece, dict):
                        value_piece = format_response_in_dic(value_piece)
                        value[index] = value_piece
                    elif isinstance(value_piece, datetime.datetime):
                        local_time = (value_piece + datetime.timedelta(hours=timedelta))
                        time_text = local_time.strftime('%Y-%m-%d %H:%M:%S')
                        value[index] = time_text
            if isinstance(value, datetime.datetime):
                local_time = (value + datetime.timedelta(hours=timedelta))
                time_text = local_time.strftime('%Y-%m-%d %H:%M:%S')
                dic[key] = time_text
    if is_format_object_id:
        for key, value in dic.items():
            if isinstance(value, dict):
                dic[key] = format_response_in_dic(value)
            if isinstance(value, list):
                for index, value_piece in enumerate(value):
                    if isinstance(value_piece, dict):
                        value_piece = format_response_in_dic(value_piece)
                        value[index] = value_piece
                    elif isinstance(value_piece, ObjectId):
                        value[index] = str(value_piece)
            if isinstance(value, ObjectId):
                dic[key] = str(value)
    return dic


def get_object_id(from_datetime=None, span_days=0, span_hours=0, span_minutes=0, span_weeks=0):
    '''根据时间手动生成一个objectid，此id不作为存储使用'''
    if not from_datetime:
        from_datetime = datetime.datetime.now()
    from_datetime = from_datetime + datetime.timedelta(days=span_days,
                                                       hours=span_hours,
                                                       minutes=span_minutes,
                                                       weeks=span_weeks)
    return ObjectId.from_datetime(generation_time=from_datetime)


def get_offset_between_local_and_utc():
    ts = time.time()
    utc_offset = int(
        (datetime.datetime.fromtimestamp(ts) - datetime.datetime.utcfromtimestamp(ts)).total_seconds() / 3600)
    return utc_offset


def x2list(expected_len, raw_material):
    new_list = list()
    for i in range(expected_len):
        new_list.append(raw_material)
    return new_list


def is_slice_expression(expression):
    if re.match("(-?\d+)?:(-?\d+)?", expression):
        return True
    else:
        return False


def replace_global_var(init_var_str, global_var_dic, global_var_regex='\${.*?}',
                       match2key_sub_string_start_index=2, match2key_sub_string_end_index=-1):
    """
    :param init_var_str: 准备进行解析的变量<str>
    :param global_var_dic: 全局变量字典<dict>
    :param global_var_regex: 识别全局变量正则表达式<str>
    :param match2key_sub_string_start_index: 全局变量表达式截取成全局变量字典key值字符串的开始索引<int>
    :param match2key_sub_string_end_index: 全局变量表达式截取为成局变量字典key值字符串的结束索引<int>
    :return: 解析后的变量<str>
    """

    if not isinstance(init_var_str, str):
        raise TypeError('init_var_str must be str！')

    if not isinstance(global_var_dic, dict):
        raise TypeError('global_var_dic must be dict！')

    if not isinstance(global_var_regex, str):
        raise TypeError('global_var_regex must be str！')

    if not isinstance(match2key_sub_string_start_index, int):
        raise TypeError('match2key_sub_string_start_index must be int！')

    if not isinstance(match2key_sub_string_end_index, int):
        raise TypeError('match2key_sub_string_end_index must be int！')

    regex_pattern = re.compile(global_var_regex)

    def global_var_repl(match_obj):
        start_index = match2key_sub_string_start_index
        end_index = match2key_sub_string_end_index
        match_value = global_var_dic.get(match_obj.group()[start_index:end_index])
        # 将一些数字类型转成str，否则re.sub会报错, match_value可能是0！
        match_value = str(match_value) if match_value is not None else match_value
        return match_value if match_value else match_obj.group()

    replaced_var = re.sub(pattern=regex_pattern, string=init_var_str, repl=global_var_repl)
    return replaced_var


# {'firstArg': '2', 'operator': '-', 'secondArg': '1', 'judgeCharacter': '<', 'expectResult': '1'}
def get_numbers_compared_result(expression):
    '''

    :param expression: for example: {'firstArg': '2', 'operator': '-', 'secondArg': '1', 'judgeCharacter': '<', 'expectResult': '1'} <dic>
    :return: <boolean>
    '''
    if not isinstance(expression, dict):
        raise TypeError('表达式必须是字典类型!')
    if not can_convert_to_float(expression.get('firstArg')) or not can_convert_to_float(expression.get('secondArg')) \
            or not can_convert_to_float(expression.get('expectResult')):
        raise TypeError('数值一: 「%s」 、 数值二: 「%s」 、 期待结果: 「%s」 必须全部为数字!'
                        % (expression.get('firstArg'), expression.get('secondArg'), expression.get('expectResult')))
    if not expression.get('operator') in ['+', '-', '*', '/']:
        raise TypeError('运算符不合法!')
    if not expression.get('judgeCharacter') in ['<', '>', '<=', '>=', '==']:
        raise TypeError('判断符不合法!')

    first_arg = expression.get('firstArg')
    operator = expression.get('operator')
    second_arg = expression.get('secondArg')
    judge_character = expression.get('judgeCharacter')
    expect_result = expression.get('expectResult')

    expression_str = "{}{}{}{}{}".format(first_arg, operator, second_arg, judge_character, expect_result)
    result = eval(expression_str)
    returned_expression_str = expression_str.replace('==', '=')  # TODO 暂时无任何后遗症

    return returned_expression_str, result


def dict_get(dic, locators, default=None):
    """
    :param dic: 输入需要在其中取值的原始字典 <dict>
    :param locators: 输入取值定位器, 如:['result', 'msg', '-1', 'status'] <list>
    :param return_str: 是否将返回值转化成str类型 <bool>
    :param default: 进行取值中报错时所返回的默认值 (default: None)
    :return: 返回根据参数locators找出的值
    """
    if not isinstance(dic, dict):
        if isinstance(dic, str) and len(locators) == 1 and is_slice_expression(locators[0]):
            slice_indexes = locators[0].split(':')
            start_index = int(slice_indexes[0]) if slice_indexes[0] else None
            end_index = int(slice_indexes[-1]) if slice_indexes[-1] else None
            value = dic[start_index:end_index]
            return value
        return default

    if dic == {} or len(locators) < 1:
        return str(dic)  # 用于后续 re.search
    value = None

    for locator in locators:
        locator = locator.replace(' ', '').replace('\n', '').replace('\t', '')
        if not type(value) in [dict, list] and isinstance(locator, str) and not is_slice_expression(locator):
            try:
                value = dic[locator]
            except KeyError:
                return default
            continue
        if isinstance(value, str) and is_slice_expression(locator):
            try:
                slice_indexes = locator.split(':')
                start_index = int(slice_indexes[0]) if slice_indexes[0] else None
                end_index = int(slice_indexes[-1]) if slice_indexes[-1] else None
                value = value[start_index:end_index]
            except KeyError:
                return default
            continue
        if isinstance(value, dict):
            try:
                value = dict_get(value, [locator])
            except KeyError:
                return default
            continue
        if isinstance(value, list) and len(value) > 0:
            if can_convert_to_int(locator):
                try:
                    value = value[int(locator)]
                except IndexError:
                    return default
                continue
            elif is_specific_search_by_dict_value(locator) and all([isinstance(v, dict) for v in value]):
                first_equal_index = locator.index('=')
                last_dot_index = locator.rindex('.')
                matched_key_re = locator[:first_equal_index]  # 字典中存在满足的正则条件的键
                matched_value_re = locator[first_equal_index + 1:last_dot_index]  # matched_key对应的值需要满足的正则条件
                needed_value_key = locator[last_dot_index + 1:]  # 满足正则条件的字典中待取的值的键

                for dic in value:
                    for k, v in dic.items():
                        if re.match(matched_key_re, str(k)) and re.match(matched_value_re, str(v)):
                            needed_value = dic.get(needed_value_key)
                            value = needed_value
                            break
                    else:
                        continue
                    break
                else:
                    return default

                continue
            elif locator == 'random':
                try:
                    value = value[random.randint(0, len(value) - 1)]
                except IndexError:
                    return default
                continue

    return value


def time_stamp2str(time_stamp, timedelta=None):
    if timedelta is None:
        timedelta = get_offset_between_local_and_utc()
    try:
        if not time_stamp:
            return ''
        local_time = datetime.datetime.utcfromtimestamp(int(time_stamp)) + datetime.timedelta(hours=timedelta)
        time_stamp_str = local_time.strftime('%Y-%m-%d %H:%M:%S')
        return time_stamp_str
    except BaseException as e:
        print('时间戳转字符串格式失败！ : %s' % e)
        return ''


def frontend_date_str2datetime(input_str, timedelta=None):
    if timedelta is None:
        timedelta = get_offset_between_local_and_utc()
    pre_date_str = input_str
    #  2019-04-23T16:00:00.000Z  ->  2019-04-23T16:00:00
    if '.' in input_str:
        pre_date_str = pre_date_str[0:input_str.rindex('.')]
    #  input_str -> datetime
    try:
        try:
            date_time = datetime.datetime.strptime(pre_date_str, "%Y-%m-%dT%H:%M:%S") + \
                        datetime.timedelta(hours=timedelta)
            return date_time
        except BaseException:
            date_time = datetime.datetime.strptime(pre_date_str, "%Y-%m-%d %H:%M:%S") + \
                        datetime.timedelta(hours=timedelta)
            return date_time
    except BaseException as e:
        raise TypeError('字符串转日期格式失败！ : %s' % e)


# get current system ip
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except BaseException as e1:
        try:
            hostname = socket.getfqdn(socket.gethostname())
            ip = socket.gethostbyname(hostname)
            print(hostname, ip)
        except BaseException as e2:
            print(e1, e2)
    finally:
        s.close()
    return ip
