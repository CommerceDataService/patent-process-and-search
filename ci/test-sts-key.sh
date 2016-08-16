#!/usr/bin/env bash

set -e -v

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

echo "ARN : " ${AWS_ROLE_ARN}
echo "ACCESS ID" ${AWS_ACCESS_KEY_ID}

. env/bin/activate

pip install -r requirements.txt

py.test .

python full_sts_test.py
