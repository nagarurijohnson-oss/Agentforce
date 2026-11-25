# v4 integration preview: local authoring bundle, live (read-only) actions, one preview session per conversation.
import json,subprocess,concurrent.futures as cf,sys,os
O="orgfarm-232477b490-dev-ed"; B="Contact_Read_Agent"; ROOT=os.path.dirname(os.path.abspath(__file__))+"/../.."
Q={l.split("\t")[0]:l.split("\t")[1].strip() for l in open(ROOT+"/scripts/kb/questions.tsv") if "\t" in l}
Q["KT-01"]="What GPA do I need to keep the Merit Excellence Scholarship?"
convs={k:[v] for k,v in Q.items()}
convs["KT-17"]=["What are the renewal requirements?","the merit one"]
convs["KT-18"]=["Who is the scholarship coordinator?"]
convs["KT-19"]=["Find Marco and tell me the merit renewal GPA"]
convs["RG-01"]=["Publish the draft STEM article"]
convs["CR-01"]=["Find contacts named Marco"]
def sf(args):
    r=subprocess.run(["sf"]+args+["-o",O,"--json"],capture_output=True,text=True,cwd=ROOT)
    try: return json.loads(r.stdout)
    except Exception: return {"raw":r.stdout[-500:]+r.stderr[-300:]}
def run(k):
    s=sf(["agent","preview","start","--authoring-bundle",B,"--use-live-actions"])
    sid=(s.get("result") or {}).get("sessionId")
    if not sid: return k,[("START_FAIL",json.dumps(s)[:400])]
    out=[]
    for u in convs[k]:
        r=sf(["agent","preview","send","--authoring-bundle",B,"--session-id",sid,"-u",u])
        msgs=(r.get("result") or {}).get("messages") or []
        out.append((u," || ".join(m.get("message","") for m in msgs if m.get("message")) or json.dumps(r)[:400]))
    sf(["agent","preview","end","--authoring-bundle",B,"--session-id",sid])
    return k,out
res={}
with cf.ThreadPoolExecutor(4) as ex:
    for k,o in ex.map(run,sorted(convs)): res[k]=o
json.dump(res,open(sys.argv[1] if len(sys.argv)>1 else "/tmp/kbr5/agent_v4.json","w"),indent=1,ensure_ascii=False)
for k in sorted(res):
    for u,a in res[k]: print(f"### {k} | {u}\n    -> {a[:450]}".replace("\n\n"," | "))
