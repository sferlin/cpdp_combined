#!/bin/bash

crucible_uuid=$1
begin_ts=$2
end_ts=$3
$samples_churn_interval=$4

crucible get metric --source uperf --type Gbps --run $crucible_uuid --begin $begin_ts --end $end_ts --output-format json --resolution $samples_churn_interval