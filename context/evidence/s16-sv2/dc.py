import json,subprocess,sys
O="orgfarm-232477b490-dev-ed"
def sql(s):
    json.dump({"sql":s},open("/tmp/dcq.json","w"))
    r=subprocess.run(["sf","api","request","rest","/services/data/v68.0/ssot/query-sql","-X","POST","-b","@/tmp/dcq.json","-o",O],capture_output=True,text=True)
    d=json.loads(r.stdout); cols=[c["name"] for c in d["metadata"]]
    return [dict(zip(cols,row)) for row in d["data"]]
def snap():
    kav=sql("SELECT ssot__Id__c, ssot__ArticleNumber__c, ssot__VersionNumber__c, ssot__KnowledgePublicationStatus__c, ssot__IsLatestVersion__c, ssot__Name__c, ssot__LastModifiedDate__c FROM ssot__KnowledgeArticleVersion__dlm ORDER BY ssot__ArticleNumber__c")
    ch=sql("SELECT SourceRecordId__c, COUNT(*) AS n FROM KA_CRA_Scholarship_Knowledge_chunk__dlm GROUP BY SourceRecordId__c")
    return {"dmo":kav,"chunks":{c["SourceRecordId__c"]:c["n"] for c in ch}}
if __name__=="__main__":
    s=snap(); json.dump(s,open(sys.argv[1],"w"),indent=1,default=str) if len(sys.argv)>1 else None
    for r in s["dmo"]: print(r["ssot__ArticleNumber__c"],r["ssot__VersionNumber__c"],r["ssot__KnowledgePublicationStatus__c"],r["ssot__IsLatestVersion__c"],r["ssot__Id__c"],s["chunks"].get(r["ssot__Id__c"]),r["ssot__Name__c"][:40],r["ssot__LastModifiedDate__c"])
    print("chunk sources",len(s["chunks"]),"total",sum(s["chunks"].values()))
