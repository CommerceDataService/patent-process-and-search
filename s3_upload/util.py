import json
import math
import os
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
    def reprocess_document(cls, doc, src_url, metadata={}):

        obj = Util.parse_json(doc)

        obj['s3_url'] = src_url

        objkeys = list(obj.keys())
        for k in objkeys:
            # Remove all float fields with value of NaN
            if k == 'textdata':
                obj['body_tx'] = obj[k]
                del obj[k]
                continue
            elif k == 'file_dt':
                if type(obj[k]) != float and '-' in obj[k]:
                    obj[k] = '{:.0f}'.format(Util.convertToUTC(obj[k]))
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

            # Add back text formatted date fields

            if k[-3:] == "_dt" and k in obj:
                obj[k + "_tx"] = Util.convertUTCtoText(obj[k])

            if k == 'doc_date' and k in obj:
                obj["doc_dt_tx"] = Util.convertUTCtoText(obj[k])
                obj["doc_dt"] = obj[k]

        # Add unique_id field   appid + ifnum
        obj['uniq_id'] = obj['appid'] + '-' + obj['ifwnumber']

        # Add text field with 32K-1
        obj['body_short_tx'] = obj['body_tx'][0:31000]

        metadata['appid'] = obj['appid']
        metadata['ifwnumber'] = obj['ifwnumber']
        metadata['type'] = 'OA'
        metadata['series'] = obj['appid'][0:2]
        metadata['documentcode'] = obj['documentcode']
        metadata['format'] = 'json'

        # Delete old doc_date field
        if 'doc_date' in obj:
            del obj['doc_date']

        # Add PROV Record wasDerivedFrom("S3URL",".","JOBURL")
        if 'PIPELINE_URL' in os.environ:
            pipeline_url = os.environ['PIPELINE_URL']
        else:
            pipeline_url = "unknown"

        obj['prov'] = 'wasDerivedFrom(%s,.,%s)' % (src_url, pipeline_url)

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

    @classmethod
    # convert day-month-year to UTC timestamp
    def convertToUTC(cls, date, format='%d-%b-%y'):
        if date != '' and date != None:
            dt = datetime.strptime(date, format)
            dt = time.mktime(dt.timetuple())
        else:
            dt = ''
        return dt


    @classmethod
    # convert day-month-year to UTC timestamp
    def convertUTCtoText(cls, date, format='%m/%d/%Y'):
        if type(date) is str:
            date = int(date)
        dt = datetime.utcfromtimestamp(date)
        txt = dt.strftime(format)
        return txt

    @classmethod
    def get_store_url(cls, meta):

        return meta['type'] + '/' + meta['series'] + '/' + meta['appid'] + '_' + \
               meta['ifwnumber'] + '_' + meta['documentcode'] + '.' + meta['format']
