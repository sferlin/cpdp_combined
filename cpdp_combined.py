import re
import subprocess
import threading
import csv
import os

#NB: Crucible runs have to last longer than kube-burner-ocp runs.
START_CRUCIBLE_SCRIPT = './test/dummy-crucible.sh'
START_KUBEBURNEROCP_SCRIPT = './test/dummy-kubeburnerocp.sh'
FILE_CSV = "/root/sferlin/cpdp_combine_run/CPCDP_COMBINED.csv"

# Roadblock: Fri Apr 11 07:30:02 UTC 2025 role: leader attempt number: 1 uuid: 1:df668962-5f49-421b-a35c-767dc78996f0:1-1-1:client-start-end
crucible_start_message_regex = re.compile(r"uuid: \d+:(.*):\d+-\d+-\d+:client-start-end")
# Roadblock: Fri Apr 11 07:40:07 UTC 2025 role: leader attempt number: 1 uuid: 1:df668962-5f49-421b-a35c-767dc78996f0:1-1-1:client-stop-begin
crucible_end_message_regex = re.compile(r"uuid: \d+:(.*):\d+-\d+-\d+:client-stop-begin")
# time="2025-04-11 07:48:05" level=info msg="👋 kube-burner run completed with rc 3 for UUID e6eec0ed-2302-40f7-bc0d-9c641fafc0d9" file="helpers.go:86"
kubeburnerocp_completed_message_regex = re.compile(r'kube-burner run completed with rc \d+ for UUID (.*)" file="helpers.go:86"')

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
    try:
        while True:
            line = p.stdout.readline()
            if line:
                print(line, end='')
                line_handler(line)
            elif p.poll() is not None:
                break
    finally:
        if p.returncode is None: p.terminate()
        p.wait()

def _kubeburnerocp_thread_main(lines):
    def handler(line):
        lines.append(line)
    _follow('kubeburnerocp', ['/bin/bash', START_KUBEBURNEROCP_SCRIPT], handler)

crucible_uuid = None
kubeburnerocp_uuid = None
kubeburnerocp_lines = None
kubeburnerocp_thread = None

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
        if kubeburnerocp_thread.is_alive():
            # Crucible runs have to last longer than kube-burner-ocp runs
            raise Exception("kubeburnerocp has not finished!")
        kubeburnerocp_thread.join()
        kubeburnerocp_thread = None
        kubeburnerocp_uuid = _get_kubeburnerocp_uuid(kubeburnerocp_lines)

def measure():
    global crucible_uuid
    global kubeburnerocp_uuid
    crucible_uuid = None
    kubeburnerocp_uuid = None

    _follow('crucible', ['/bin/bash', START_CRUCIBLE_SCRIPT], _crucible_handler)

    if not crucible_uuid:
        raise Exception("Did not get a UUID from crucible!")
    if not kubeburnerocp_uuid:
        raise Exception("Did not get a UUID from kubeburnerocp!")
    
    # Let's put this now in a file and keep UUID pairs together
    with open(FILE_CSV,'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow([os.environ['PPN'], os.environ['CHURN_PERCENT'], os.environ['CHURN_DURATION'], 'crucible: ', crucible_uuid, 'kube-burner-ocp: ', kubeburnerocp_uuid])

    return crucible_uuid, kubeburnerocp_uuid


crucible_uuid, kubeburnerocp_uuid = measure()
print(f'crucible: {crucible_uuid}')
print(f'kubeburnerocp: {kubeburnerocp_uuid}')
