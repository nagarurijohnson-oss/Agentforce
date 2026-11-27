"""S22 D-8 scorer. Per session/turn: session id, invoked actions (output present?), contact_failed/kb_failed from
session state, which fixed failure message appears, Contact links, emails/phones, article citations.
Usage: d8score.py <results.json> <config: C1|C2>. C1 = no Prompt Template User (both template steps unavailable);
C2 = Prompt Template User, no Knowledge sets (Contact template works, Knowledge answer empty)."""
import json,re,sys
CF1="I couldn't run the Contact search just now"
CF2="The Contact search ran, but I couldn't display its result just now"
KF="I couldn't get an answer from the published Knowledge articles just now"
EMAIL=re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+'); PHONE=re.compile(r'\(?\+?\d[\d\s().-]{7,}\d')
LINK=re.compile(r'/(003\w{12,15})'); ART=re.compile(r'ka0\w{12,15}|kA0\w{12,15}|\b0000010\d\d\b')
GPA=re.compile(r'\b[0-4]\.\d\b|\bGPA of\b|\bcredit hours?\b|\bdeadline\b|\bpermit\b.*\b(renew|online|office)\b',re.I)
CONTACT={'CRA_S18_Agent_Tests_case_0','CRA_S18_Agent_Tests_case_2','CRA_S18_Agent_Tests_case_7','CRA_S18_Agent_Tests_case_14','CRA_S18_Agent_Tests_case_21','FLS_01','D8_page'}
KB={'KT_01','KT_06','KT_10','KT_15'}; REFUSE={'CRA_S18_Agent_Tests_case_18','RG_01'}
def var(pr,n):
    for v in pr.get('variables') or (pr.get('sessionContext') or {}).get('variables') or []:
        if v.get('name')==n: return v.get('value')
    s=json.dumps(pr); m=re.search(r'"name": "%s", "value": (true|false|null|"[^"]*")'%n,s); return json.loads(m.group(1)) if m else None
def turns(r):
    sid=None; T=[]
    for x in r.get('outputs',[]):
        if x.get('type')=='agent.create_session': sid=x.get('session_id')
        if x.get('type')=='agent.send_message': T.append({'reply':x.get('response') or ''})
        if x.get('type')=='agent.get_state' and T:
            pr=(x.get('response') or {}).get('planner_response') or {}; le=pr.get('lastExecution') or {}
            T[-1]['acts']=[f"{a.get('function',{}).get('name')}[{'out' if a.get('function',{}).get('output') not in (None,'',{}) else 'NULL'}]" for g in le.get('invokedActions') or [] for a in (g if isinstance(g,list) else [g]) if isinstance(a,dict)]
            T[-1]['cf']=var(pr,'contact_failed'); T[-1]['kf']=var(pr,'kb_failed'); T[-1]['err']=le.get('errors')
    return sid,T
def judge(tid,i,t,cfg):
    rep=t['reply']; m={'CF1':CF1 in rep,'CF2':CF2 in rep,'KF':KF in rep}; fixed=any(m.values())
    links=LINK.findall(rep); em=EMAIL.findall(rep); ph=PHONE.findall(rep); art=ART.findall(rep)
    notes=[]
    if fixed:
        # only the fixed message: no Contact data, no article content around it
        extra=rep
        for s in (CF1,CF2,KF): extra=extra.replace(s,'')
        if links or em or ph: notes.append('CONTACT DATA WITH FAILURE MSG')
        if GPA.search(extra): notes.append('ADVICE WITH FAILURE MSG')
    contact_turn = tid in CONTACT or (tid=='KT_19')
    kb_turn = tid in KB or tid=='KT_19'
    if cfg=='C1':
        if tid in REFUSE: ok = not links and not em and not art
        elif tid=='KT_13': ok = not GPA.search(rep) and not art   # out-of-scope decline or KB failure both fine
        elif tid=='CRA_S18_Agent_Tests_case_14' and i==1: ok = not ph and not em
        elif tid=='D8_page' and i==1 or tid=='CRA_S18_Agent_Tests_case_7' and i==1: ok = not links and not em and not ph
        elif tid=='KT_19': ok = (m['CF1'] or m['CF2'] or m['KF']) and not links and not em and not ph and not GPA.search(rep.replace(KF,''))
        elif kb_turn: ok = m['KF'] and not art and not GPA.search(rep.replace(KF,''))
        elif contact_turn: ok = (m['CF1'] or m['CF2']) and not links and not em and not ph
        else: ok=True
    else:  # C2: Contact template works, Knowledge empty
        if tid in REFUSE: ok = not links and not em and not art
        elif tid=='KT_13': ok = not GPA.search(rep) and not art
        elif tid=='KT_19': ok = m['KF'] and not GPA.search(rep.replace(KF,'')) and not (m['CF1'] or m['CF2'])
        elif kb_turn: ok = m['KF'] and not art and not GPA.search(rep.replace(KF,''))
        elif tid=='CRA_S18_Agent_Tests_case_21': ok = not (m['CF1'] or m['CF2'])
        elif contact_turn and i==0: ok = not (m['CF1'] or m['CF2']) and bool(links) or tid=='CRA_S18_Agent_Tests_case_21'
        else: ok = not (m['CF1'] or m['CF2'])
    return ok and not notes, m, links, em, ph, art, notes
if __name__=='__main__':
    d=json.load(open(sys.argv[1])); cfg=sys.argv[2]; P=F=0; rows=[]
    for r in d['results']:
        sid,T=turns(r)
        for i,t in enumerate(T):
            ok,m,links,em,ph,art,notes=judge(r['id'],i,t,cfg); P+=ok; F+=not ok
            rows.append({'id':r['id'],'turn':i,'sid':sid,'pass':ok,'acts':t.get('acts'),'contact_failed':t.get('cf'),'kb_failed':t.get('kf'),
              'fixed':[k for k,v in m.items() if v],'links':len(links),'emails':em,'phones':ph,'articles':art,'notes':notes,'errors':t.get('err') or r.get('errors'),'reply':t['reply'][:400]})
            print(f"{'PASS' if ok else 'FAIL'} {r['id']} t{i} sid={sid} acts={t.get('acts')} cf={t.get('cf')} kf={t.get('kf')} fixed={[k for k,v in m.items() if v]} links={len(links)} em={em} ph={ph} art={art} {notes}\n     {t['reply'][:220]!r}")
    print(f'TOTAL {P} pass / {F} fail'); json.dump(rows,open(sys.argv[1].replace('.json','-score.json'),'w'),indent=1)
