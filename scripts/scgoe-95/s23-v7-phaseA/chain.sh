cd /tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work && . ./env.sh; export SF_DISABLE_LOG_FILE=true SF_SKIP_NEW_VERSION_CHECK=true BATCH=5 PAUSE=20
V=0X9jV000001DkAvSAK; R=s20/run_eval_uat.js
node $R s19/kb23.json $V s23/a1-kb23.json > s23/a1.log 2>&1; sleep 60
node $R Agentforce-kb/scripts/scgoe-95/s19-v6-paging/CRA_S19_v5_testSpec.yaml $V s23/a2-suite.json > s23/a2.log 2>&1; sleep 60
node $R s23/sec.json $V s23/a4-sec.json > s23/a4.log 2>&1; sleep 60
node $R s23/page10.json $V s23/a3-page.json > s23/a3p.log 2>&1; sleep 60
node $R s19/edge.json $V s23/a3-edge.json > s23/a3e.log 2>&1; sleep 60
node $R Agentforce-kb/scripts/scgoe-95/s19-v6-paging/after2.json $V s23/a3-after2.json > s23/a3n.log 2>&1
touch s23/done
