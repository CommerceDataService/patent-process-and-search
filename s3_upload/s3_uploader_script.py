import os, glob, time, botocore, boto3, logging, argparse
from s3_uploader_new import S3Uploader

def uploader():
    logging.info('-- Connecting to s3')
    return S3Uploader('uspto-bdr')
    logging.info('-- Connected to s3')

def post(filename, fname, series):
    try:
        s3session.post_file(filename, fname, series)
        return True
    except botocore.exceptions.ClientError as e:
        logging.error('Unexpected error %s' % e)
        raise
        return False

#write list of app ID's to specified log file
def writeLogs(logfname,idlist):
    try:
        with open(logfname,'a+') as logfile:
            for appid in idlist:
                logfile.write(appid+"\n")
        logging.info('-- Log entries for: '+logfname+' written to file')
    except IOError as e:
        logging.error('-- Write Log: '+logfname+' I/O error({0}): {1}'.format(e.errno,e.strerror))

if __name__ == '__main__':
    filesaddedtos3 = []

    #logging configuration
    logging.basicConfig(
                        filename='logs/uploadtos3-'+time.strftime('%Y%m%d')+'.txt',
                        level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s -%(message)s',
                        datefmt='%Y%m%d %H:%M:%S'
                       )
    parser = argparse.ArgumentParser()
    parser.add_argument(
                        '-s',
                        '--series',
                        required=True,
                        help='Specify series to process - format ## (separate each additional series with space)',
                        nargs='*',
                        type=str
                       )
    parser.add_argument(
                        '-a',
                        '--startappid',
                        required=False,
                        help='Specify an app ID to start with when uploading the files',
                        type=int,
                        default=0
                       )
    parser.add_argument(
                        '-n',
                        '--numoffiles',
                        required=False,
                        help='Specify number of files to process',
                        type=int,
                        default=100000000
                       )
    parser.add_argument(
                        '-w',
                        '--stagingfiles',
                        required=False,
                        help='Pass this flag to denote loading of staging files',
                        action="store_true",
                        default=False
                       )
    args = parser.parse_args()
    logging.info("-- SCRIPT ARGUMENTS ------------")
    if args.series:
        logging.info("-- Series passed for processing: "+", ".join(args.series))
    logging.info("-- Starting app ID set to: "+str(args.startappid))
    logging.info("-- Number of files to process set to: "+str(args.numoffiles))
    logging.info("-- Staging files flag set to: "+str(args.stagingfiles))
    logging.info("-- [JOB START]  ----------------")

    mainpath = os.path.join('c:'+os.sep, 'scripts', 'uspto_ptab', 'extractedfiles')
    for series in args.series:
        seriespath = os.path.join(mainpath, series, 'staging')
        if args.stagingfiles:
            seriesfolder = series+'s'
        else:
            seriesfolder = series
        startappid = args.startappid
        logging.info('Processing seriespath: '+seriespath)
        filecounter = 0
        s3session = uploader()
        logging.info('Collecting filenames ' + seriespath)
        for filename in glob.glob(os.path.join(seriespath,'*')):
            fpath, fname = os.path.split(filename)
            appid = int(fname.split('_')[0])
            ifwnumber = int(fname.split('_')[1])
            if fname.endswith('.json') and appid >= startappid and filecounter <= args.numoffiles:
                if post(filename, fname, seriesfolder):
                    filecounter += 1
                    logging.info('-- {} - posted file: {}'.format(filecounter,fname))
                    filesaddedtos3.append(appid+','+ifwnumber)
                else:
                    logging.error('-- File upload failed for: {}'.format(fname))
        writeLogs(os.path.join(seriespath,'filesaddedtos3.log'),filesaddedtos3)
