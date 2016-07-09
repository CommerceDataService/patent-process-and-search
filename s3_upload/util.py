class Util(object):
    @classmethod
    def log_directory(cls, objkey):
        parts = (objkey[0:2], objkey[3:7], objkey[7:10], objkey[10])

        return '/'.join(parts)

    @classmethod
    def doc_id(cls, objkey):
        past_series = objkey.split('/')[1]
        return past_series.split('_')[0] + ', ' + past_series.split('_')[1]
