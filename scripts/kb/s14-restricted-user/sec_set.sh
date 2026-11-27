#!/bin/bash
# usage: sec_set.sh true|false  -> deploys ONLY enableAdminLoginAsAnyUser
cd /tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work/s14/sec
cat > force-app/main/default/settings/Security.settings-meta.xml <<X
<?xml version="1.0" encoding="UTF-8"?>
<SecuritySettings xmlns="http://soap.sforce.com/2006/04/metadata">
    <enableAdminLoginAsAnyUser>$1</enableAdminLoginAsAnyUser>
</SecuritySettings>
X
export SF_DISABLE_LOG_FILE=true SF_SKIP_NEW_VERSION_CHECK=true
timeout 300 sf project deploy start --source-dir force-app --target-org orgfarm-232477b490-dev-ed --wait 5 --json > ../sec-$1.json 2>&1
python3 -c 'import json;d=json.load(open("../sec-'$1'.json"));r=d.get("result",d);print("SECDEPLOY",r.get("status"),r.get("id"),r.get("numberComponentsDeployed"),d.get("message","")[:200])'
