import argparse
import re
import subprocess
import threading
import traceback
import csv
from datetime import datetime

CHURN_CYCLES='5'
PPN='50'

START_CRUCIBLE_SCRIPT = './start_crucible.sh' #'./test/dummy-crucible.sh'
START_KUBEBURNEROCP_SCRIPT = './start_kubeburnerocp.sh' #'./test/dummy-kubeburnerocp.sh'
FILE_CSV = "CPDP_COMBINED.csv"

parser = argparse.ArgumentParser()
parser.add_argument("churn_percent", help="churn percent to use in measurement", type=int)
args = parser.parse_args()

if args.churn_percent < 0 or args.churn_percent > 100:
    raise Exception(f"Invalid churn_percent {args.churn_percent}!")

# Roadblock: Fri Apr 11 07:30:02 UTC 2025 role: leader attempt number: 1 uuid: 1:df668962-5f49-421b-a35c-767dc78996f0:1-1-1:client-start-end
crucible_start_message_regex = re.compile(r"uuid: \d+:(.*):\d+-\d+-\d+:client-start-end")
# Roadblock: Fri Apr 11 07:40:07 UTC 2025 role: leader attempt number: 1 uuid: 1:df668962-5f49-421b-a35c-767dc78996f0:1-1-1:client-stop-begin
crucible_end_message_regex = re.compile(r"uuid: \d+:(.*):\d+-\d+-\d+:client-stop-begin")
# time="2025-04-11 07:48:05" level=info msg="👋 kube-burner run completed with rc 3 for UUID e6eec0ed-2302-40f7-bc0d-9c641fafc0d9" file="helpers.go:86"
kubeburnerocp_completed_message_regex = re.compile(r'kube-burner run completed with rc \d+ for UUID (.*)" file=')

def _is_crucible_start_message(line):
    result = crucible_start_message_regex.search(line)
    return True if result else False

def _is_crucible_end_message(line):
    result = crucible_end_message_regex.search(line)
    return True if result else False

def _get_crucible_uuid(line):
    result = crucible_end_message_regex.search(line)
    return result.group(1)

def _get_kubeburnerocp_uuid(lines):
    for line in reversed(lines):
        result = kubeburnerocp_completed_message_regex.search(line)
        if result:
            return result.group(1)

def _start(cmd):
    # Force started process to line buffering via stdbuf. Avoids data queuing up in STDOUT.
    return subprocess.Popen(['/usr/bin/stdbuf', '-oL'] + cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)

def _follow(name, cmd, line_handler):
    p = _start(cmd)
    print(f"----- STARTED {name}. PID: {p.pid}")
    had_error = None
    try:
        while True:
            line = p.stdout.readline()
            if line:
                print(line, end='')
                try:
                    if not had_error:
                        line_handler(line)
                except Exception as e:
                    had_error = e
                    traceback.print_exc()
            elif p.poll() is not None:
                break
    finally:
        if p.returncode is None: p.terminate()
        p.wait()
        if had_error: raise had_error

def _kubeburnerocp_thread_main(lines):
    def handler(line):
        lines.append(line)
    _follow('kubeburnerocp', ['/bin/bash', START_KUBEBURNEROCP_SCRIPT, CHURN_CYCLES, str(args.churn_percent), PPN], handler)

crucible_uuid = None
kubeburnerocp_uuid = None
kubeburnerocp_lines = None
kubeburnerocp_thread = None

def _has_kubeburnerocp_ended(lines):
    for line in lines:
        if 'Stopping measurement:' in line:
            return True
    return False

def _crucible_handler(line):
    global crucible_uuid
    global kubeburnerocp_lines
    global kubeburnerocp_thread
    global kubeburnerocp_uuid
    if _is_crucible_start_message(line):
        if kubeburnerocp_thread:
            raise Exception("kubeburnerocp was already started!")
        kubeburnerocp_lines = []
        kubeburnerocp_thread = threading.Thread(target=_kubeburnerocp_thread_main, args=[kubeburnerocp_lines])
        kubeburnerocp_thread.start()
    elif _is_crucible_end_message(line):
        crucible_uuid = _get_crucible_uuid(line)
        if not kubeburnerocp_thread:
            raise Exception("kubeburnerocp was not started!")
        still_measuring = not _has_kubeburnerocp_ended(kubeburnerocp_lines)
        if kubeburnerocp_thread.is_alive():
            print('Crucible is done, waiting for a running kubeburnerocp')
        kubeburnerocp_thread.join()
        kubeburnerocp_thread = None
        if still_measuring:
            # Crucible runs have to last longer than kube-burner-ocp runs, but kube-burner can take a long time doing GC
            raise Exception("kubeburnerocp has not finished!")
        kubeburnerocp_uuid = _get_kubeburnerocp_uuid(kubeburnerocp_lines)

def measure():
    global crucible_uuid
    global kubeburnerocp_uuid
    crucible_uuid = None
    kubeburnerocp_uuid = None

    print(f'Starting with churn_percent={args.churn_percent}')

    # NB: Crucible runs have to last longer than kube-burner-ocp runs
    _follow('crucible', ['/bin/bash', START_CRUCIBLE_SCRIPT], _crucible_handler)

    if not crucible_uuid:
        raise Exception("Did not get a UUID from crucible!")
    if not kubeburnerocp_uuid:
        raise Exception("Did not get a UUID from kubeburnerocp!")
    
    # Put this now in a file and keep UUID pairs together
    with open(FILE_CSV,'a', newline='') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), CHURN_CYCLES, args.churn_percent, PPN, crucible_uuid, kubeburnerocp_uuid])

    return crucible_uuid, kubeburnerocp_uuid


crucible_uuid, kubeburnerocp_uuid = measure()
print(f'crucible: {crucible_uuid}')
print(f'kubeburnerocp: {kubeburnerocp_uuid}')
