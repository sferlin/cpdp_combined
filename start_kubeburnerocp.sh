#!/bin/bash

export ES_SERVER='https://admin:nKNQ9=vw_bwaSy1@search-perfscale-pro-wxrjvmobqs7gsyi3xvxkqmn7am.us-west-2.es.amazonaws.com:443'
export ES_IDX='ripsaw-kube-burner'
export CHURN_DURATION='10m'
export CHURN_PERCENT=10
export PPN=50

/root/sferlin/kube-burner-node-density-churn/bin/amd64/kube-burner-ocp node-density-cni --gc-metrics=true --gc=true --es-server=$ES_SERVER --es-index=$ES_IDX --churn --churn-duration $CHURN_DURATION --churn-percent $CHURN_PERCENT --pods-per-node $PPN --worker-nodes 2 --local-indexing
