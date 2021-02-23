import requests
import time
import hmac
import hashlib
import base64
import urllib.parse


def send_wxwork_notify_markdown(content, api_key, headers=None):
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    hook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}".format(api_key)
    data = {"msgtype": "markdown",
            "markdown": {
                "content": "{}".format(content)
            }}
    notify_res = requests.post(url=hook_url, json=data, headers=headers)
    return notify_res


def send_wxwork_notify_text(content, mentioned_mobile_list, api_key, headers=None):
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    if not mentioned_mobile_list or not isinstance(mentioned_mobile_list, list):
        raise TypeError("mentioned_mobile_list should be a list!")
    hook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}".format(api_key)
    data = {"msgtype": "text",
            "text": {
                "content": "{}".format(content),
                "mentioned_mobile_list": mentioned_mobile_list
            }}
    notify_res = requests.post(url=hook_url, json=data, headers=headers)
    return notify_res


def send_ding_talk_notify_markdown(content_title, content_text, access_token, at_mobiles=[], secret=None, headers=None):
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    hook_url = "https://oapi.dingtalk.com/robot/send?access_token={}".format(access_token)
    if secret:
        timestamp, sign = generate_timestamp_and_sign(secret)
        hook_url = "https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}".format(access_token,
                                                                                                      timestamp, sign)
    data = {
        "msgtype": "markdown",
    }
    if at_mobiles and "@all" in at_mobiles:
        data['markdown'] = {
            "title": "{} @all".format(content_title),
            "text": "{} @all".format(content_text)
        }
        data['at'] = {
            "atMobiles": at_mobiles,
            "isAtAll": True
        }
    elif at_mobiles and "@all" not in at_mobiles:
        if len(at_mobiles) > 1:
            at_mobiles_str = "@".join(at_mobiles)
            at_mobiles_str = "@{}".format(at_mobiles_str)
        else:
            at_mobiles_str = "@{}".format(at_mobiles[0])
        data['markdown'] = {
            "title": "{} {}".format(content_title, at_mobiles_str),
            "text": "{} {}".format(content_text, at_mobiles_str)
        }
        data['at'] = {
            "atMobiles": at_mobiles,
            "isAtAll": False
        }
    notify_res = requests.post(url=hook_url, json=data, headers=headers)
    return notify_res


def generate_timestamp_and_sign(secret):
    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return timestamp, sign


if __name__ == "__main__":
    pass
