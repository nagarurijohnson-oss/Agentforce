cd <work> && . ./env.sh; export SF_DISABLE_LOG_FILE=true SF_SKIP_NEW_VERSION_CHECK=true
V=0X9jV000001DkAvSAK
node Agentforce-kb/scripts/scgoe-95/s18-agent-tests/run_eval_pinned.js Agentforce-kb/scripts/scgoe-95/s19-v6-paging/CRA_S19_v5_testSpec.yaml $V s22/suite.json > s22/suite.log 2>&1; sleep 60
node s18/eval_json.js s19/kb23.json $V s22/kb23.json > s22/kb23.log 2>&1; sleep 60
node s18/eval_json.js s19/edge.json $V s22/edge.json > s22/edge.log 2>&1; sleep 45
node s18/eval_json.js Agentforce-kb/scripts/scgoe-95/s19-v6-paging/after2.json $V s22/after2.json > s22/after2.log 2>&1; sleep 60
for p in 0 1 2; do node s18/eval_json.js s19/page$p.json $V s22/page$p.json > s22/page$p.log 2>&1; sleep 90; done
touch s22/done
