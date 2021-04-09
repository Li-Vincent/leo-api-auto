# -*- coding: utf-8 -*-
__author__ = 'Li-Vincent'

import re
from faker import Faker


def resolve_faker_var(init_faker_var, faker_var_regex=r'\$faker{([a-z]{2}_[A-Z]{2})?\.?(.*?)(\(.*?\))}'):
    re_global_var = re.compile(faker_var_regex)

    def faker_var_repl(match_obj):
        locale_index = match_obj.group(1)
        method_name = match_obj.group(2)
        _args = match_obj.group(3)
        _faker = Faker(locale_index)
        _kwargs = str_args_2_dict(_args) if '=' in _args else {}
        match_value = getattr(_faker, method_name)(**_kwargs)
        # 将一些数字类型转成str，否则re.sub会报错, match_value可能是0！
        match_value = str(match_value) if match_value is not None else match_value
        return match_value if match_value else match_obj.group()

    resolved_var = re.sub(pattern=re_global_var, string=init_faker_var, repl=faker_var_repl)
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


if __name__ == "__main__":
    test_str = '''
    {
        "expired":"$faker{credit_card_expire(start=now, end=+10y, date_format=%m/%y)}",
        "name":"$faker{zh_CN.name()}",
        "phone":$faker{zh_CN.phone_number()},
        "phone_code":$faker{zh_CN.country_calling_code()},
        "bool":$faker{boolean(chance_of_getting_true=<int>50)}
    }'''
    val = resolve_faker_var(test_str)
    print(val)
