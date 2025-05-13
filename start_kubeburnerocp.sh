#!/bin/bash

export ES_SERVER='https://admin:nKNQ9=vw_bwaSy1@search-perfscale-pro-wxrjvmobqs7gsyi3xvxkqmn7am.us-west-2.es.amazonaws.com:443'
export ES_IDX='ripsaw-kube-burner'

#node-density-cni: old build, added churn for node-density-cni, but wrong churnStart/churnEnd timestamps
#/root/sferlin/kube-burner-node-density-churn/bin/amd64/kube-burner-ocp node-density-cni --gc-metrics=true --gc=true --es-server=$ES_SERVER --es-index=$ES_IDX --churn --churn-cycles $1 --churn-percent $2 --pods-per-node $3 --worker-nodes 2 --local-indexing

#node-density-cni: correct churnStart/churnEnd correct timestamps, without --worker-nodes hack
/root/sferlin/kube-burner-ocp/bin/amd64/kube-burner-ocp node-density-cni --gc-metrics=true --gc=true --es-server=$ES_SERVER --es-index=$ES_IDX --churn --churn-cycles $1 --churn-percent $2 --pods-per-node $3 --local-indexing

#rds
#/root/sferlin/kube-burner-ocp/bin/amd64/kube-burner-ocp rds-core --gc-metrics=true --dpdk-cores=2 --perf-profile=customcnf --gc=false --service-latency=true --churn=false --iterations 99 --es-server=$ES_SERVER --es-index=$ES_IDX
