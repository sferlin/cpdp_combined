#!/bin/bash

echo 'time="2025-04-11 07:48:05" level=error msg="Empty document list in nodeCPUSeconds-Infra-start" file="prometheus.go:225"'
#time="2025-04-11 07:48:05" level=info msg="Indexing [2] documents from metric max-memory-kube-controller-manager" file="prometheus.go:222"
#time="2025-04-11 07:48:05" level=info msg="File collected-metrics-e6eec0ed-2302-40f7-bc0d-9c641fafc0d9/max-memory-kube-controller-manager.json created with 2 documents" file="prometheus.go:227"
#time="2025-04-11 07:48:05" level=info msg="Indexing [2] documents from metric max-memory-openshift-controller-manager" file="prometheus.go:222"
sleep 1
echo 'time="2025-04-11 07:48:05" level=info msg="File collected-metrics-e6eec0ed-2302-40f7-bc0d-9c641fafc0d9/max-memory-openshift-controller-manager.json created with 2 documents" file="prometheus.go:227"'
sleep 1
echo 'time="2025-04-11 07:48:05" level=info msg="Indexing [8] documents from metric max-cpu-multus" file="prometheus.go:222"'
#time="2025-04-11 07:48:05" level=info msg="File collected-metrics-e6eec0ed-2302-40f7-bc0d-9c641fafc0d9/max-cpu-multus.json created with 8 documents" file="prometheus.go:227"
sleep 1
echo 'time="2025-04-11 07:48:05" level=info msg="Finished execution with UUID: e6eec0ed-2302-40f7-bc0d-9c641fafc0d9" file="job.go:220"'
#time="2025-04-11 07:48:05" level=error msg="[alert at 2025-04-11T07:31:03Z: 'Critical prometheus alert. ClusterVersionOperatorDown', alert at 2025-04-11T07:41:39Z: 'Critical prometheus alert. ClusterVersionOperatorDown']" file="helpers.go:84"
sleep 1
echo 'time="2025-04-11 07:48:05" level=info msg="👋 kube-burner run completed with rc 3 for UUID e6eec0ed-2302-40f7-bc0d-9c641fafc0d9" file="helpers.go:86"'
