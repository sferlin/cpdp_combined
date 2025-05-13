#!/bin/bash

#!/bin/bash

crucible_uuid=$1
begin_ts=$2
end_ts=$3
samples_churn_interval=$4

cat <<EOF
*** NOTICE: Crucible is at least 167 commits behind.  See 'crucible repo info' for details. ***

Checking for httpd...appears to be running
Checking for OpenSearch...appears to be running
{
  "values": {
    "": [
      {
        "begin": 1746805406000,
        "end": 1746805406666,
        "value": 741.9292166611694
      },
      {
        "begin": 1746805406667,
        "end": 1746805407333,
        "value": 742.8669684707646
      },
      {
        "begin": 1746805407334,
        "end": 1746805408000,
        "value": 743.3420333718141
      }
    ]
  }
}
EOF
