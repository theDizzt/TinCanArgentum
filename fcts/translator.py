import json
from typing import Any, MutableSequence
from urllib.parse import quote, quote_plus
from urllib.request import Request, urlopen
"""
DataDictionary = {
    prefix + "ke": ["ko", "Korean", "en", "English"],
    prefix + "ek": ["en", "English", "ko", "Korean"],
    prefix + "ec": ["en", "English", "zh-CN", "Chinese"],
    prefix + "ce": ["zh-CN", "Chinese", "en", "English"],
    prefix + "kc": ["ko", "Korean", "zh-CN", "Chinese"],
    prefix + "ck": ["zh-CN", "Korean", "ko", "Korean"]
}
"""


class dataProcessStream(object):

    def __init__(self, client_id, client_secret):
        self.baseurl = "https://openapi.naver.com/v1/papago/n2mt"
        self.client_id = client_id
        self.client_secret = client_secret

    def returnQuery(self, lan1, lan2, text):
        needTranslate = text
        basicQuery = f"source={lan1}&target={lan2}&text={quote_plus(text)}"
        return self.buildRequestInstane(basicQuery, needTranslate)

    def buildRequestInstane(self, Query, needTranslate):
        req = Request(self.baseurl)
        req.add_header("X-Naver-Client-Id", self.client_id)
        req.add_header("X-Naver-Client-Secret", self.client_secret)
        response = urlopen(req, data=Query.encode("utf-8"))
        return self.checkResponseReturnDataBox(response, needTranslate)

    def checkResponseReturnDataBox(self, response, needTranslate):
        dataBox = {
            "status": {
                "code": None
            },
            "data": {
                "ntl": {
                    "text": needTranslate,
                },
                "tl": {
                    "text": None,
                }
            }
        }
        if response.getcode() < 300:
            dataBox["status"]["code"] = response.getcode()
            response = response.read()
            apiResult = response.decode('utf-8')
            apiResult = json.loads(apiResult)
            translated = apiResult['message']['result']["translatedText"]
            dataBox["data"]["tl"]["text"] = translated
            return dataBox
        else:
            dataBox["status"]["code"] = response.getcode()
            return dataBox
