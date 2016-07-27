import json

class Util(object):
    @classmethod
    def log_directory(cls, objkey):
        parts = (objkey[0:2], objkey[3:7], objkey[7:10], objkey[10])

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

        if obj['dn_intppty_cust_no'] == 'NaN':
            del obj['dn_intppty_cust_no']

#TODO: SOLR should handle '\n' properly if they are not removed.
#        obj['textdata'] = obj['textdata'].replace('\n', ' \n ')


        return json.dumps(obj)
