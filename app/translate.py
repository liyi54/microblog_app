import json
from flask_babel import _
from flask import current_app
import requests, uuid

def translate(text, from_lang, to_lang):
    if not current_app.config['MS_TRANSLATOR_KEY'] or 'MS_TRANSLATOR_KEY' not in current_app.config:
        return _('Error: The translator service is not configured')

    headers = {'Ocp-Apim-Subscription-Key': current_app.config['MS_TRANSLATOR_KEY'],
               'Ocp-Apim-Subscription-Region': "eastasia",
               'Content-type': "application/json",
               'X-ClientTraceId': str(uuid.uuid4())}

    body = [{
        'text': text
    }]
    r = requests.post('https://api.cognitive.microsofttranslator.com/translate'
                     '?api-version=3.0&from={0}&to={1}'.format(from_lang, to_lang),
                      json=body, headers=headers)

    # response = r.json()

    # print(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
    if r.status_code == 200:
        resp_obj = json.loads(r.content.decode('utf-8-sig'))
        value = resp_obj[0]['translations'][0]['text']
        return value
    return _('Error: The translation service failed')
