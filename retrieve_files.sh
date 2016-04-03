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
    echo "usage: ./retrieve_files.sh [[-d YYYMMDD YYYYMMDD]| [-a] | [-n]]"
}

function log()
{
  type=$1
  message=$2

  if [ $type = "WARN" -o $type = "ERR" ]
  then
    echo >> $statusDirectory/err-$processingTime
    echo -e "$type: `date +%Y.%m.%d-%H:%M:%S` -- $scriptName -- $message" >> $statusDirectory/retrieve-err-$processingTime
  fi
  #
  # always write into log file
  #
  echo
  echo -e "$type: `date +%Y.%m.%d-%H:%M:%S` -- $scriptName -- $message"
  echo >> $statusDirectory/log-$processingTime
  echo -e "$type: `date +%Y.%m.%d-%H:%M:%S` -- $scriptName -- $message" >> $statusDirectory/retrieve-log-$processingTime
}

#=============================== MAIN BODY OF SCRIPT ===============================

##### Constants
processingTime=`date +%Y%m%d-%H%M%S`
scriptName=$0
statusDirectory=logs
baseURL="https://bulkdata.uspto.gov/data2/patent/trial/appeal/board/"
dropLocation="files"
declare -i startDate
endDate=$(date +%Y%m%d) 
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
    startDate=$1
    if [ ! -z "$2" ]
    then
      echo $2
      if date "+%d/%m/%Y" -d $2 >/dev/null 2>&1 
      then
        endDate=$2
      else
        log "ERR" "end date passed in is not valid: $2"
        lock false
        exit 1
      fi
    fi
    log "INFO" "Date parameters: \n\tStartDate: $startDate \n\tEndDate:   $endDate"
  else
    log "ERR" "start date passed in is not valid: $1"
    lock false
    exit 1
  fi
  ;;
-a | --all )
  retrieveAll=true
  log "INFO" "Retrieve All parameter set to TRUE"
  ;;
-n | --none )
  retrieveNone=true
  log "INFO" "Retrieve None parameter set to TRUE"
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

#create directory for downloaded files and logs(if does not exist already)
mkdir -p $dropLocation
mkdir -p $statusDirectory

log "INFO" "-[JOB START] $(date): ------------"

#if --all flag is set then get all available files from the page
if $retrieveAll && ! $retrieveNone 
then
  log "INFO" "Starting file download process"
  wget --directory-prefix=files -e robots=off --cut-dirs=3  --reject="index.html*" --no-parent --recursive --relative --level=1 --no-directories $baseURL
  log "INFO" "File download process complete"

#use the start and end dates to determine which files to get
elif ! $retrieveAll && ! $retrieveNone
then
  log "INFO" "Starting file download process"
  startDate=$(date '+%C%y%m%d' -d "$startDate -$(date -d $startDate +%u) days + 5 day")
  while [ $startDate -lt $endDate ]
  do
    year=$(date -d $startDate +%Y) 
    week=$(date -d $startDate +%V)
    if [ $year -eq  2015 ]
    then
      week="$(printf "%02d" $((10#$week-1)))"
    fi
    zipFilePath=${baseURL}PTAB_${startDate}_WK${week}.zip
    wget -q --spider $zipFilePath
    if [ $? -eq 0 ]
    then
      log "INFO" "Downloading file: $zipFilePath"
      wget -nc -P $dropLocation $zipFilePath 
    else 
      log "ERR" "file does not exist: $zipFilePath"
    fi
    startDate=$(date '+%C%y%m%d' -d "$startDate+7 days")
  done
  log "INFO" "File download process complete"
#if --none flag is set then skip download process
else
  log "INFO" "skipping file download process"
fi

#unzip all zip files unless they have already been unzipped
log "INFO" "Starting file unzipping process"

find $dropLocation -type f -name "*.zip" -exec unzip -n {} -d $dropLocation \;

log "INFO" "File unzip process complete"

log "INFO" "Starting file parsing process"

#parse all pdf files that have not already been parsed
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
          curl -X PUT --data-binary @$i http://192.168.99.100:9998/tika --header "Content-type: application/pdf" > ${i%.*}.txt
        fi
      done
    else
      log "INFO" "No files to parse"
    fi
  fi
done       

log "INFO" "File parsing process complete"

log "INFO" "-[JOB END]-- $(date): ------------"

lock false
