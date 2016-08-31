#!/usr/bin/env bash

export TZ='US/Eastern'


export PIPELINE="$GO_PIPELINE_NAME/$GO_PIPELINE_LABEL/$GO_STAGE_NAME/$GO_STAGE_COUNTER"
export PIPELINE_URL="http://scheduler.r2.v-lad.org/go/pipelines/${PIPELINE}"


reset="\033[0m"
bold="\033[1m"
red="\033[31m"
blue="\033[34m"

warn () {
    echo -e "${bold}${red}WARNING${reset}"
    echo -en "${red}"
    echo -en "$@"
    echo -en "${reset}"
}

error () {
    echo -e "${bold}${red}ERROR${reset}"
    echo -en "${red}"
    echo -en "$@"
    echo -en "${reset}"
    exit 1
}

log () {
    echo -e "${blue}$@${reset}"
}



if [ ! -x /usr/bin/virtualenv ]; then
    warn "Virtual ENV not found... installing"
    pip3.4 install virtualenv
fi

if [ ! -x env ]; then
  virtualenv -p python3.4 env
fi

. env/bin/activate


if [[ $GO_JOB_NAME == *"AWS"* ]]
then
  log "Remove AWS ARN and Friends";
  unset AWS_ROLE_ARN
  unset AWS_ACCESS_KEY_ID
  unset AWS_SECRET_ACCESS_KEY
fi

set -u

log "Start!"
log "Pipeline : ${PIPELINE_URL}"
