# Runs KT-01..KT-15 against the ACTIVE CRA_Knowledge_Answer version (v5: retriever bound in the template).
# Only the question is passed; the template's Einstein Search data provider supplies the passages.
import json,subprocess,sys,concurrent.futures as cf,os
O="orgfarm-232477b490-dev-ed"; OUT=sys.argv[2] if len(sys.argv)>2 else "/tmp/kbr5/gen_v5.json"
def gen(q,tag):
    body={"isPreview":False,"inputParams":{"valueMap":{"Input:question":{"value":q}}},"additionalConfig":{"applicationName":"PromptTemplateGenerationsInvocable"}}
    fn=f"/tmp/kbr5/b_{tag}.json"; json.dump(body,open(fn,"w"))
    r=subprocess.run(["sf","api","request","rest","/services/data/v68.0/einstein/prompt-templates/CRA_Knowledge_Answer/generations","-X","POST","-b","@"+fn,"-o",O],capture_output=True,text=True)
    try: d=json.loads(r.stdout); return d["generations"][0]["text"]
    except Exception: return "ERROR "+r.stdout[:400]+r.stderr[-300:]
cases=[(f"KT-{i:02d}",json.load(open(f"retrievals/KT-{i:02d}.json"))["question"]) for i in range(1,16)]
runs=int(sys.argv[1]) if len(sys.argv)>1 else 3
res={}
with cf.ThreadPoolExecutor(6) as ex:
    fut={ex.submit(gen,q,f"{k}_{n}"):(k,n) for k,q in cases for n in range(runs)}
    for f in cf.as_completed(fut): res.setdefault(fut[f][0],{})[fut[f][1]]=f.result()
json.dump(res,open(OUT,"w"),indent=1,ensure_ascii=False)
for k in sorted(res):
    for n in sorted(res[k]): print(f"### {k} run {n+1}: "+res[k][n].replace(chr(10)," | ")[:300])
