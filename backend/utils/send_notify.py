import requests


def send_wxwork_notify_markdown(content, api_key, headers=None):
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    hook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}".format(api_key)
    data = {"msgtype": "markdown", "markdown": {
        "content": "{}".format(content)
    }}
    text_notify_res = requests.post(url=hook_url, json=data, headers=headers)
    return text_notify_res


def send_wxwork_notify_text(content, mentioned_mobile_list, api_key, headers=None):
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    hook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}".format(api_key)
    data = {"msgtype": "text", "text": {
        "content": "{}".format(content),
        "mentioned_mobile_list": mentioned_mobile_list
    }}
    text_notify_res = requests.post(url=hook_url, json=data, headers=headers)
    return text_notify_res


if __name__ == "__main__":
    res = send_wxwork_notify("Test 企业微信通知", "企业微信通知内容", "3704f5f7-716a-419b-b140-98d8257cb8cb")
    print(res.status_code)
