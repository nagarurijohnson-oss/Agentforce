import json,subprocess,concurrent.futures as cf
O="orgfarm-232477b490-dev-ed"; A="Contact_Read_Agent"
def sf(a):
    r=subprocess.run(["sf"]+a+["-o",O,"--json"],capture_output=True,text=True)
    try: return json.loads(r.stdout)
    except Exception: return {"raw":r.stdout[-300:]}
def run(i):
    s=sf(["agent","preview","start","--api-name",A]); sid=(s.get("result") or {}).get("sessionId")
    if not sid: return {"run":i,"err":json.dumps(s)[:300]}
    out=[]
    for u in ["Find Synthetic Engineer contacts at CRA-TEST Northwind Synthetic","Yes, show me the other 3"]:
        r=sf(["agent","preview","send","--api-name",A,"--session-id",sid,"-u",u]); m=(r.get("result") or {}).get("messages") or []
        out.append({"u":u,"reply":" || ".join(x.get("message","") for x in m if x.get("message"))})
    sf(["agent","preview","end","--api-name",A,"--session-id",sid]); return {"run":i,"sid":sid,"turns":out}
with cf.ThreadPoolExecutor(3) as ex: res=list(ex.map(run,range(3)))
json.dump(res,open("../s17/r/v3-pagination.json","w"),indent=1,ensure_ascii=False)
import re
for r in res:
    if "err" in r: print(r); continue
    t1,t2=r["turns"][0]["reply"],r["turns"][1]["reply"]
    print(r["run"],"T1 8-match:", "8" in t1, re.findall(r"Eng Mockup0\d",t1)[:8],"| T2:",sorted(set(re.findall(r"Eng Mockup0\d",t2))))
