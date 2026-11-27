# Scores KT-19-family runs from the preview reply plus the session trace (preview strips Markdown links).
import json,glob,re,sys
ROOT="/tmp/build-ce359a3b-1cb6-4793-8e80-9ee87d147500/work/Agentforce"
ART={a["Id"]:a for a in json.load(open(ROOT+"/scripts/kb/articles_live.json"))}
ONLINE={i for i,a in ART.items() if a["PublishStatus"]=="Online"}
EXP={ # key: (expected article Id or None for clarification, required facts)
 "KT-19":("ka0jV000000nIDXQA2",["3.3","24"]),
 "KT-19b":("ka0jV000000nIDXQA2",["3.3","24"]),
 "KT-19c":("ka0jV000000nIDZQA2",["15 February"]),
 "KT-19d":(None,["Merit Excellence Scholarship","Graduate Research Scholarship"]),
 "KT-19e":("ka0jV000000nIDXQA2",["3.3","24"]),
}
d=json.load(open(sys.argv[1])); ok=0; rows=[]
for k,v in sorted(d.items()):
    base=k.split("#")[0]; art,facts=EXP[base]; a=v["turns"][0][1]; probs=[]
    tr="".join(json.dumps(json.load(open(f))) for f in glob.glob(f"{ROOT}/.sfdx/agents/Contact_Read_Agent/sessions/{v['sid']}/traces/*.json"))
    topics=re.findall(r'"topic": "(\w+)"',tr)
    if "contact_and_knowledge" not in topics: probs.append("route="+",".join(topics))
    if "Marco Blankfield" not in a: probs.append("no contact")
    for f in facts:
        if f not in a: probs.append("missing "+f)
    links=set(re.findall(r'\(/lightning/r/Knowledge__kav/([A-Za-z0-9]{18})/view\)',tr))
    if art:
        if links!={art}: probs.append(f"links={links}")
        if "1 March" in a: probs.append("draft fact")
        if "Which one" in a: probs.append("asked which one")
    else:
        if "Which one" not in a: probs.append("no clarification")
        if "3.3" in a or "3.5" in a: probs.append("figures in clarification")
    if links-ONLINE: probs.append("non-online link")
    if re.search(r"https?://",a): probs.append("absolute url")
    if base=="KT-19e":
        a2=v["turns"][1][1]
        if "Synthetic Auditor" not in a2: probs.append("follow-up title missing")
    rows.append((k,not probs,probs)); ok+= not probs
for r in rows: print(r[0],"PASS" if r[1] else "FAIL",r[2])
print(f"{ok}/{len(rows)}")
