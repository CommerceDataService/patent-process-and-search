#!/usr/bin/env bash

set -e

export TZ='US/Eastern'

echo "Testing S3 with STS key"

if [ ! -x /usr/bin/virtualenv ]; then
    echo "Virtual ENV not found... installing"
    pip3.4 install virtualenv
fi

if [ ! -x env ]; then
  virtualenv -p python3.4 env
fi

if [[ $GO_JOB_NAME == *"AWS"* ]]
then
  echo "Remove AWS ARN and Friends";
  unset AWS_ROLE_ARN
  unset AWS_ACCESS_KEY_ID
  unset AWS_SECRET_ACCESS_KEY
fi


. env/bin/activate

pip install -r requirements.txt

py.test .

rm -f run-list.txt


python reprocess_create_run_list.py

find . | grep -v ./env/ | grep -v ./.git/




