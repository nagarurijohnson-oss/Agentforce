// S18: run a YAML test spec through the Agentforce evaluation API (real multi-turn sessions)
// pinned to a specific BotVersion. Same translation/normalisation as `sf agent test run-eval`,
// but with the named-user JWT the preview commands use. Read-only: it only sends utterances.
const base='/usr/local/lib/node_modules/@salesforce/cli/node_modules/@salesforce/';
const core=require(base+'core'); const ag=require(base+'agents/lib/index.js');
const utils=require(base+'agents/lib/utils.js'); const fs=require('fs');
(async()=>{
  const [specPath,versionId,outPath]=process.argv.slice(2);
  const org=await core.Org.create({aliasOrUsername:'orgfarm-232477b490-dev-ed'});
  const conn=org.getConnection();
  const ui=await conn.request(`${conn.instanceUrl}/services/oauth2/userinfo`);
  const bot=(await conn.query("SELECT Id FROM BotDefinition WHERE DeveloperName='Contact_Read_Agent'")).records[0].Id;
  const ver=(await conn.query(`SELECT Id,VersionNumber,Status FROM BotVersion WHERE Id='${versionId}'`)).records[0];
  if(!ver) throw new Error('version not found');
  const spec=ag.parseTestSpec(fs.readFileSync(specPath,'utf8'));
  let payload=ag.translateTestSpec(spec);
  for(const t of payload.tests) for(const s of t.steps) if(s.type==='agent.create_session'){s.agent_id=bot;s.agent_version_id=versionId;}
  payload=ag.normalizePayload(payload);
  const c2=await core.Connection.create({authInfo:await core.AuthInfo.create({username:conn.getUsername()})});
  await utils.useNamedUserJwt(c2);
  const batches=ag.splitIntoBatches(payload.tests,5); const results=[];
  for(const b of batches){
    const r=await utils.requestWithEndpointFallback(c2,{url:'https://api.salesforce.com/einstein/evaluation/v1/tests',method:'POST',
      headers:{'Content-Type':'application/json','x-sfdc-core-tenant-id':`core/prod/${org.getOrgId()}`,'x-org-id':org.getOrgId(),
      'x-sfdc-core-instance-url':conn.instanceUrl,'x-sfdc-user-id':ui.user_id,'x-client-feature-id':'AIPlatformEvaluation','x-sfdc-app-context':'EinsteinGPT'},
      body:JSON.stringify({tests:b})},{retry:{maxRetries:3}});
    results.push(...(r.results||[])); process.stderr.write(`batch done ${results.length}/${payload.tests.length}\n`);
  }
  fs.writeFileSync(outPath,JSON.stringify({version:ver,payload,results},null,1));
  console.log(JSON.stringify(ag.buildResultSummary({results}).summary));
})().catch(e=>{console.error('ERR',e.message,e.data||'');process.exit(1)});
