import json,subprocess,sys,os,concurrent.futures as cf
O="orgfarm-232477b490-dev-ed"; T="CRA_Knowledge_Answer"; OUT=sys.argv[1]; RUNS=int(sys.argv[2]) if len(sys.argv)>2 else 3
Q={"KT-06":"What documents do I need for an athletic scholarship?","KT-05":"What documents do international students need for their scholarship?","KT-06b":"Do athletic scholarship applicants need an NCAA eligibility certificate?"}
os.makedirs("/tmp/kbs16",exist_ok=True)
def gen(k,q,n):
    fn=f"/tmp/kbs16/{k}_{n}.json"; json.dump({"isPreview":False,"inputParams":{"valueMap":{"Input:question":{"value":q}}},"additionalConfig":{"applicationName":"PromptTemplateGenerationsInvocable"}},open(fn,"w"))
    r=subprocess.run(["sf","api","request","rest",f"/services/data/v68.0/einstein/prompt-templates/{T}/generations","-X","POST","-b","@"+fn,"-o",O],capture_output=True,text=True)
    try: return json.loads(r.stdout)["generations"][0]["text"]
    except Exception: return "ERROR "+r.stdout[:300]
res={}
with cf.ThreadPoolExecutor(6) as ex:
    f={ex.submit(gen,k,q,n):(k,n) for k,q in Q.items() for n in range(RUNS)}
    for x in cf.as_completed(f): res.setdefault(f[x][0],{})[str(f[x][1])]=x.result()
json.dump({"questions":Q,"results":res},open(OUT,"w"),indent=1,ensure_ascii=False)
for k in sorted(res):
    for n,t in sorted(res[k].items()): print(k,n,"|",t.replace("\n"," / ")[:230])
