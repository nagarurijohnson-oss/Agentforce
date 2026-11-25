cd /tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work
export PYTHONPATH=$PWD/pylib LD_LIBRARY_PATH=$(cat ldpath.txt) PLAYWRIGHT_BROWSERS_PATH=$PWD/pwbrowsers
for c in L1b-single-unique L2-field L3-threshold-narrow-page L4-duplicates L5-two-to-five L6-over-100 L7-guard L8-coord-11 L9-hostile-1 L9-hostile-2 L9-hostile-3; do
  echo "=== $c $(date -u +%T)"; timeout 900 python3 ui_s12.py s12/cfg/$c.json 2>&1 | grep -v Warning | cut -c1-600
done
echo ALLDONE
