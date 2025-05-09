# CALL WITH: python3.11 cpdp_fetch.py

import argparse
import csv
from dateutil.parser import isoparse
import json
import os.path
import subprocess
import re
import datetime

GET_CRUCIBLE_METRIC_SCRIPT = './get_crucible_metric.sh'
FILE_CSV = "CPDP_COMBINED.csv"

parser = argparse.ArgumentParser()
parser.add_argument("churn_interval", help="churn interval on(1)/off(0)", type=int)
args = parser.parse_args()

if args.churn_interval < 0 or args.churn_interval > 1:
    raise Exception(f"Invalid churn_interval {args.churn_interval}!")

def _get_churn_intervals(kubeburnerocp_log_filename):
    ts = []
    with open(kubeburnerocp_log_filename, 'rt') as file:
        for line in file:
            log_dict = dict(re.findall(r'(\w+)=["](.*?)["]', line))
            time = datetime.datetime.strptime(log_dict['time'], "%Y-%m-%d %H:%M:%S")
            if log_dict['msg'] == 'Verifying created objects':
                ts.append(time)
            elif log_dict['msg'].startswith('Sleeping for '):
                ts.append(time)
                # Look for churn duration intervals (default : 2m0s/120s)
                churn_int_duration = re.search(r'(\d+)m(\d+)s', log_dict['msg'])
                if not churn_int_duration: raise Exception('Unexpected sleep log line')
                duration_sec = int(churn_int_duration.group(1)) * 60 + int(churn_int_duration.group(2))
                next_time = time + datetime.timedelta(seconds = duration_sec)
                ts.append(next_time)
    # After the last sleep, churning ends with a message 'Reached specified number'
    pairs = []
    for i in range(0, len(ts), 2):
        j = i + 1
        if j < len(ts):
            pairs.append([ts[i], ts[j]])
    return pairs


if args.churn_interval == 0:
    print(f'Considering churn_interval={args.churn_interval} turned off, i.e., look at the whole experiment')
else:
    print(f'Considering churn_interval={args.churn_interval} turned on, i.e., disregard intervals between churns')

with open(FILE_CSV, 'r', newline='') as file:
    reader = csv.reader(file, delimiter='\t')
    for row in reader:
        print(row)

        [dt, churn_cycles, churn_percent, ppn, crucible_uuid, kubeburnerocp_uuid] = row

        kubeburnerocp_results_path = f"collected-metrics-{kubeburnerocp_uuid}"
        with open(os.path.join(kubeburnerocp_results_path, 'jobSummary.json'), 'r') as f:
            summary = json.loads(f.read())[0]

        intervals = []
        if args.churn_interval == 0:
            kubeburnerocp_start = isoparse(summary['churnStartTimestamp'])
            kubeburnerocp_end = isoparse(summary['churnEndTimestamp'])
            intervals.append([kubeburnerocp_start, kubeburnerocp_end])
        else:
            kubeburnerocp_log_path = f"kube-burner-ocp-{kubeburnerocp_uuid}.log"
            intervals = _get_churn_intervals(kubeburnerocp_log_path)

        for interval in intervals:
            # crucible expects timestamps in milliseconds
            begin_ts = int(interval[0].timestamp() * 1000 + 0.5) # round up
            end_ts = int(interval[1].timestamp() * 1000)
            print(f"kubeburnerocp run={kubeburnerocp_uuid} begin={begin_ts} end={end_ts}")
            samples_churn_interval = int((end_ts-begin_ts)/1000)

            crucible_cmd = ['/bin/bash', GET_CRUCIBLE_METRIC_SCRIPT, "get", "metric", "--source", "uperf", "--type", "Gbps", "--run", crucible_uuid, "--begin", str(begin_ts), "--end", str(end_ts), "--output-format", "json", "--resolution", str(samples_churn_interval)]
            print("Running command:", ' '.join(crucible_cmd))
            
            output = subprocess.check_output(crucible_cmd,universal_newlines=True)
            crucible_json_text = output[output.find('{'):]
            crucible_json = json.loads(crucible_json_text)
            crucible_data = crucible_json['values'][''][0]

            # crucible_data looks like { "begin": 1746438618045, "end": 1746439878525, "value": 22.515339753410007 }
            print(crucible_data['value'])

            break
        break
