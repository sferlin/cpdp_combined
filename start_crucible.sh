#!/bin/bash

#make clean-lab ; make clean-jobs ; make clean-all
#source ./bootstrap.sh ; make init-lab ; make init-jobs

cd /root/sferlin/regulus

JSON_FILE='/root/sferlin/regulus/1_GROUP/PAO/4IP/INTER-NODE/TCP/2-POD/mv-params.json'
#JSON_FILE='./test/dummy-params.json'

jq --arg new_val "$1" '(.["global-options"][]?.params[]? | select(.arg == "duration") .vals) = [$new_val]' "$JSON_FILE" > tmp.json && mv tmp.json "$JSON_FILE"
  
make run-jobs
