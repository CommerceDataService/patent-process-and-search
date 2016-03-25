#!/bin/bash
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
    if [ -f ${LOCKFILE} ]
    then
      echo
      echo "${LOCKFILE} exits."
      echo "Looks like a copy of $scriptName is already running... "
      echo "Abort"
      log "ERR" " Already running, please check logs for reason... "
      exit 0
    else
      touch ${LOCKFILE}
    fi
  else
    if [ -f $LOCKFILE ] ; then
      rm $LOCKFILE
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
BASEURL="https://bulkdata.uspto.gov/data2/patent/trial/appeal/board/"
DROP_LOCATION="files/`date +%Y%m%d`"
declare -i filedate
retrieve_all=false
retrieve_none=false
LOCKFILE="/tmp/file_download.lck"

touch $statusDirectory/log-$processingTime

lock true

case "$1" in
-d | --date )
  shift
  echo "$1"
  if date -d $1 >/dev/null 2>&1
  then
    filedate=$1
  else
    log "ERR" "date passed in is not valid: $1"
    lock false
    exit 1
  fi
  ;;
-a | --all )
  retrieve_all=true
  ;;
-n | --none )
  retrieve_none=true
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
mkdir -p $DROP_LOCATION

currentdate=$(date +%Y%m%d) 

DATE="`date`"
log "INFO" "-[JOB START] ${DATE}: ------------"
log "INFO" "================= Script starting ================="

log "INFO" "Starting file download process"

if $retrieve_all && ! $retrieve_none 
then
  wget --directory-prefix=files/`date +%Y%m%d` -e robots=off --cut-dirs=3  --reject="index.html*" --no-parent --recursive --relative --level=1 --no-directories $BASEURL
elif ! $retrieve_all && ! $retrieve_none
then
  while [ $filedate -lt $currentdate ]
  do
    fri_date=$(date '+%C%y%m%d' -d "$filedate -$(date -d $filedate +%u) days + 5 day")
    year=$(date -d $fri_date +%Y) 
    week=$(date -d $fri_date +%V)
    if [ $year -eq  2015 ]
    then
      week=$((10#$week-1))
      if [ $week -lt 10 ]
      then
        week="$(printf "%02d" $week)"
      fi
    fi
  
    zipfilepath=${BASEURL}PTAB_${fri_date}_WK${week}.zip
    wget -q --spider $zipfilepath
    if [ $? -eq 0 ]
    then
      wget -nc -P $DROP_LOCATION $zipfilepath 
    else 
      log "ERR" "file does not exist: $zipfilepath"
    fi

    filedate=$(date '+%C%y%m%d' -d "$filedate+7 days")
  done
fi

log "INFO" "File download process complete"

#After pulling down the files, unzip each one in the directory
log "INFO" "Starting file unzipping process"

find $DROP_LOCATION -type f -name "*.zip" -exec unzip -n {} -d $DROP_LOCATION \;

log "INFO" "File unzip process complete"

log "INFO" "Starting file parsing process"

#find $DROP_LOCATION -type f -name "*pdf" -exec curl -X PUT --data-binary *.pdf http://192.168.99.100:9998/tika --header "Content-type: application/pdf" >> $statusDirectory/log-$processingTime-processfiles.txt \;

log "INFO" "File parsing process complete"

log "INFO" "================= Script exiting ================="
DATE="`date`"
log "INFO" "-[JOB END]-- ${DATE}: ------------"

lock false
