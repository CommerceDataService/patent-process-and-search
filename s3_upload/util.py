import json
import math
from datetime import datetime
import time


class Util(object):
    @classmethod
    def log_directory(cls, objkey):
        (series, appid ) = objkey.split('/')

        parts = (series, appid[0:4], appid[4:7], appid[7])

        return '/'.join(parts)

    @classmethod
    def doc_id(cls, objkey):
        past_series = objkey.split('/')[1]
        return past_series.split('_')[0] + ', ' + past_series.split('_')[1]

    @classmethod
    def parse_json(cls, obj):
        return json.loads(obj.decode('utf-8'))

    @classmethod
    def reprocess_document(cls, doc, src_url):

        obj = Util.parse_json(doc)

        obj['s3_url'] = src_url

        objkeys = list(obj.keys())
        for k in objkeys:
            # Remove all float fields with value of NaN
            if k == 'textdata':
                continue
            elif k == 'file_dt':
                if type(obj[k]) != float and '-' in obj[k]:
                    obj[k] = '{:.0f}'.format(Util.convertToUTC(obj[k], '%d-%b-%y'))
                else:
                    obj[k] = '{:.0f}'.format(obj[k])
            elif k == 'dn_dw_gau_cd':
                obj['dn_dw_dn_gau_cd'] = obj[k]
                del obj[k]
            elif type(obj[k]) == float:
                if math.isnan(obj[k]):
                    del obj[k]
                else:
                    obj[k] = '{:.0f}'.format(obj[k])
            elif type(obj[k]) == str:
                trimmed = obj[k].strip()
                if len(trimmed) == 0 or trimmed == 'nan':
                    del obj[k]
                else:
                    obj[k] = trimmed


        return json.dumps(obj)

    @classmethod
    def allowed_key(cls, key):

        if key[0:3] == '13/':
            if key[5] in ('2', '3', '6', '7'):
                return True

        return False

    @classmethod
    def secondary_log_directory(cls, key):

        log_dir = Util.log_directory(key)

        return log_dir.replace("13/", "13s/")

        return json.dumps(obj)
