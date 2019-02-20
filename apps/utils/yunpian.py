import requests
import json


class YunPian(object):
    def __init__(self):
        self.account = 'C26029744'
        self.api_key = '0129b3d4b1bdc50b39ffbf27923cb3a6'
        self.single_send_url = 'http://106.ihuyi.com/webservice/sms.php?method=Submit'

    def send_sms(self, code, mobile):
        params = {
            'account': self.account,
            'password': self.api_key,
            'mobile': mobile,
            'content': '您的验证码是：{code}。请不要把验证码泄露给其他人。'.format(code=code)
        }
        response = requests.post(self.single_send_url, data=params)
        print('进入前',response.content)
        # re_dict = json.loads(response.content)
        # print('进入后')
        text = response.content.decode(encoding='utf-8')
        if '<code>2</code>' in text:
            re_dict = {'code': 2}
        else:
            re_dict = {'code': 0}

        return re_dict

# if __name__ == '__main__':
#     yun_pian = YunPian('C26029744', '0129b3d4b1bdc50b39ffbf27923cb3a6')
#     yun_pian.send_sms('1234', '13135657008')


# class YunPian(object):
#     def __init__(self, account, api_key):
#         self.account = account
#         self.api_key = api_key
#         self.single_send_url = 'http://106.ihuyi.com/webservice/sms.php?method=Submit'
#
#     def send_sms(self, code, mobile):
#         params = {
#             'account': self.account,
#             'password': self.api_key,
#             'mobile': mobile,
#             'content': '【互亿无线】您的验证码是：{code}。请不要把验证码泄露给其他人。'.format(code=code)
#         }
#         response = requests.post(self.single_send_url, data=params)
#         re_dict = json.loads(response.text)
#
#
# if __name__ == '__main__':
#     yun_pian = YunPian('C26029744', '0129b3d4b1bdc50b39ffbf27923cb3a6')
#     yun_pian.send_sms('1234', '13135657008')