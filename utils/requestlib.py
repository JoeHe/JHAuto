import requests
import urllib3

from utils import utils

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RequestLib:
    def __init__(self, timeout=45, verify_certificate=False, silence=False):
        utils.log("init a session...")
        self.session = requests.session()
        self.timeout = timeout
        self.verify_cert = verify_certificate
        self.cookie = None
        self.silence = silence

    def __action(self, url, headers, method='Get', **kwargs):
        if not self.silence:
            utils.log(".....................................................")
            utils.log("sending request...")
            utils.log("request parameters:")
            utils.log("url: {}".format(url))
            utils.log("method: {}".format(method))
            utils.log("headers: {}".format(headers))
            if kwargs:
                for k, v in kwargs.items():
                    utils.log("{}: {}".format(k, v))
            else:
                utils.log("request parameters is none.")

        try:
            if method == 'Post':
                resp = self.session.post(url, headers=headers, timeout=self.timeout, verify=self.verify_cert, **kwargs)
            elif method == 'Put':
                resp = self.session.put(url, headers=headers, timeout=self.timeout, verify=self.verify_cert, **kwargs)
            elif method == 'Delete':
                resp = self.session.delete(url, headers=headers, timeout=self.timeout, verify=self.verify_cert, **kwargs)
            else:
                resp = self.session.get(url, headers=headers, timeout=self.timeout, verify=self.verify_cert, **kwargs)
            resp.raise_for_status()
        except Exception as e:
            utils.error("HTTP请求异常，异常信息：{}".format(e))
        return resp

    def get(self, url, headers=None, **kwargs):
        return self.__action(url, headers=headers, **kwargs)

    def post(self, url, headers=None, **kwargs):
        """
        params=None, data=None, json=None, cookies=None, files=None
        """
        return self.__action(url, headers=headers, method='Post', **kwargs)

    def put(self, url, headers=None, **kwargs):
        return self.__action(url, headers=headers, method='Put', **kwargs)

    def delete(self, url, headers=None, **kwargs):
        return self.__action(url, headers=headers, method='Delete', **kwargs)

    def close_session(self):
        if self.session:
            utils.log("close session.")
            self.session.close()

    def set_cookie(self, cookie):
        """
        set or update session cookie
        """
        self.session.cookies = cookie



    

