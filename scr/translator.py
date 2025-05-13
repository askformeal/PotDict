import requests
import json

def translate(text, target_lang):
    if target_lang == '':
        return "[Target language not defined]"
    response = requests.get(f'https://translate.appworlds.cn?text={text}&from=auto&to={target_lang}')
    response.encoding = 'utf-8'
    if response.status_code != 200:
        return f'[Connection failed: code {response.status_code}]'
    else:
        result = json.loads(response.text)
        if result['code'] != 200:
            return f'[{result['msg']}]'
        else:
            return result['data']