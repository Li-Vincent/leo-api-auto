# -*- coding: utf-8 -*-
__author__ = 'Li-Vincent'

import re
import datetime
import time


def resolve_func_var(init_func_var, func_var_regex=r'\$func{([a-zA-Z0-9_]*)(\(.*?\))}'):
    re_global_var = re.compile(func_var_regex)

    def func_var_repl(match_obj):
        method_name = match_obj.group(1)
        _args = match_obj.group(2)
        _func = Func()
        _kwargs = str_args_2_dict(_args) if '=' in _args else {}
        match_value = getattr(_func, method_name)(**_kwargs)
        # 将一些数字类型转成str，否则re.sub会报错, match_value可能是0！
        match_value = str(match_value) if match_value is not None else match_value
        return match_value if match_value else match_obj.group()

    resolved_var = re.sub(pattern=re_global_var, string=init_func_var, repl=func_var_repl)
    return resolved_var


def str_args_2_dict(args: str) -> dict:
    """
        参数必须写成 key=value的格式， 并且value只支持基本类型，不支持 list/dict等复杂类型
        value默认为str，如果为其他类型，需添加标识，<int>,<float>

        :param args: 准备进行转换的参数<str>
        :return: 转换后的字典<dict>
        """

    args = args.replace(' ', '')
    args = args.replace('(', '')
    args = args.replace(')', '')
    args_list = args.split(',')
    dic = {}
    for param in args_list:
        equal_sign_index = param.index('=')
        key = param[:equal_sign_index]
        value = param[equal_sign_index + 1:]
        if '<int>' in value:
            value = int(value[value.find('<int>') + 5:])
        elif '<float>' in value:
            value = float(value[value.find('<float>') + 7:])
        dic[key] = value
    return dic


class Func:

    def __init__(self):
        pass

    def get_milli_second_timestamp(self):
        now_timetuple = time.time()
        return int(round(now_timetuple * 1000))  # 毫秒级时间戳

    def get_micro_second_timestamp(self):
        now_timetuple = time.time()
        return int(round(now_timetuple * 1000000))  # 微秒级时间戳

    def get_second_timestamp(self):
        now_timetuple = time.time()
        return int(now_timetuple)  # 秒级时间戳

    def get_current_time(self, format_str="%Y-%m-%d %H:%M:%S"):
        return datetime.datetime.now().strftime(format_str);


if __name__ == "__main__":
    test_str = '''
        milli_second = $func{get_milli_second_timestamp()}  
        micro_second = $func{get_micro_second_timestamp()}  
        second = $func{get_second_timestamp()}
        current_time = $func{get_current_time("%Y-%m-%d %H:%M:%S")}
    '''
    resolved = resolve_func_var(test_str)
    print(resolved)
    pass
