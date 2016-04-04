#/bin/bash
#set -x

###################################################################################################################
#
#Script to download,extract, and parse PTAB pdf files from USPTO bulk data site. 
#
#argument options:
#           (1) pass -d OR --date AND YYYYMMDD to download files from a specific date on
#           (2) pass -a OR --all to download all files
#           (3) pass -n OR --none to skip downloading of files and execute unzipping process
#
###################################################################################################################

#create lock file
function lock ( ) {
  if "$1" == true
  then
    if [ -f ${lockFile} ]
    then
      echo
      echo "${lockFile} exits."
      echo "Looks like a copy of $scriptName is already running... "
      echo "Abort"
      log "ERR" " Already running, please check logs for reason... "
      exit 0
    else
      touch ${lockFile}
    fi
  else
    if [ -f $lockFile ] ; then
      rm $lockFile
    fi
  fi
}

function usage
{
    echo "usage: ./retrieve_files.sh [[-d YYYMMDD]| [-a] | [-n]]"
}

function log()
{
  type=$1
  message=$2

  if [ $type = "WARN" -o $type = "ERR" ]
  then
    echo >> $statusDirectory/err-$processingTime
    echo -e "$type: `date +%Y.%m.%d-%H:%M:%S` -- $scriptName -- $message" >> $statusDirectory/err-$processingTime
  fi
  #
  # always write into log file
  #
  echo
  echo -e "$type: `date +%Y.%m.%d-%H:%M:%S` -- $scriptName -- $message"
  echo >> $statusDirectory/log-$processingTime
  echo -e "$type: `date +%Y.%m.%d-%H:%M:%S` -- $scriptName -- $message" >> $statusDirectory/log-$processingTime
}

#=============================== MAIN BODY OF SCRIPT ===============================

##### Constants
processingTime=`date +%Y%m%d-%H%M%S`
scriptName=$0
statusDirectory=logs
baseURL="https://bulkdata.uspto.gov/data2/patent/trial/appeal/board/"
dropLocation="files/`date +%Y%m%d`"
declare -i fileDate
retrieveAll=false
retrieveNone=false
lockFile="/tmp/file_download.lck"

touch $statusDirectory/log-$processingTime

lock true

case "$1" in
-d | --date )
  shift
  if date "+%d/%m/%Y" -d $1 >/dev/null 2>&1
  then
    fileDate=$1
  else
    log "ERR" "date passed in is not valid: $1"
    lock false
    exit 1
  fi
  ;;
-a | --all )
  retrieveAll=true
  ;;
-n | --none )
  retrieveNone=true
  ;;
-h | --help )
  usage
  lock false
  exit
  ;;
* )
  usage
  lock false
  log "ERR" "argument passed in is not valid: $1"
  exit 1
esac
     
#create directory for downloaded files(if does not exist already)
mkdir -p $dropLocation

currentdate=$(date +%Y%m%d) 

log "INFO" "-[JOB START] $(date): ------------"
log "INFO" "================= Script starting ================="


if $retrieveAll && ! $retrieveNone 
then
  log "INFO" "Starting file download process"
  wget --directory-prefix=files/`date +%Y%m%d` -e robots=off --cut-dirs=3  --reject="index.html*" --no-parent --recursive --relative --level=1 --no-directories $baseURL
  log "INFO" "File download process complete"
elif ! $retrieveAll && ! $retrieveNone
then
  while [ $fileDate -lt $currentdate ]
  do
    log "INFO" "Starting file download process"
    friDate=$(date '+%C%y%m%d' -d "$fileDate -$(date -d $fileDate +%u) days + 5 day")
    year=$(date -d $friDate +%Y) 
    week=$(date -d $friDate +%V)
    if [ $year -eq  2015 ]
    then
      week="$(printf "%02d" $((10#week-1)))"
    fi
  
    zipFilePath=${baseURL}PTAB_${friDate}_WK${week}.zip
    wget -q --spider $zipFilePath
    if [ $? -eq 0 ]
    then
      wget -nc -P $dropLocation $zipFilePath 
    else 
      log "ERR" "file does not exist: $zipFilePath"
    fi

    fileDate=$(date '+%C%y%m%d' -d "$fileDate+7 days")
  done
  log "INFO" "File download process complete"
else
  log "INFO" "skipping file download process"
fi

#After pulling down the files, unzip each one in the directory
log "INFO" "Starting file unzipping process"

find $dropLocation -type f -name "*.zip" -exec unzip -n {} -d $dropLocation \;

log "INFO" "File unzip process complete"

log "INFO" "Starting file parsing process"

for f in $dropLocation/*
do
  if [[ $f == *.zip ]]
  then
    continue;
  else
    if [ -d "$f/PDF_image" ]
    then
      for i in $f/PDF_image/*.pdf
      do
        fname=$(basename "$i")
        fname="${fname%.*}"
        if [ ! -f "$f/PDF_image/$fname.txt" ]
        then
          log "INFO" "Parsing document: $i to ${i%.*}.txt"
          python parse.py "$i" 2>&1
          # leaving this cURL command in so we can use it for reference or debugging
          # curl -X PUT --data-binary @$i http://192.168.99.100:9998/tika --header "Content-type: application/pdf" > ${i%.*}.txt
         fi
      done
    else
      log "INFO" "No files to parse"
    fi
  fi
done       

log "INFO" "File parsing process complete"

log "INFO" "================= Script exiting ================="
log "INFO" "-[JOB END]-- $(date): ------------"

lock false
