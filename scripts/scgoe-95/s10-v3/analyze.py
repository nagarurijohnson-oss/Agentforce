"""SCGOE-95 Session 10: per-turn detail from preview traces (contactId used, result Ids, reply). Read-only."""
import json,glob,os,re,sys
B=glob.glob('.sfdx/agents/*/sessions/')
def turns(sid):
    out=[]
    for f in sorted([f for b in B for f in glob.glob(b+sid+'/traces/*.json')],key=os.path.getmtime):
        plan=json.load(open(f))['plan']; t={'user':'','searches':[],'reply':'','tmpl':''}
        for s in plan:
            if s['type']=='UserInputStep': t['user']=s.get('message','')
            if s['type']=='FunctionStep' and s['function']['name']=='search_contacts':
                i=s['function'].get('input') or {}; o=s['function'].get('output') or {}
                t['searches'].append({'contactId':i.get('contactId'),'requestedField':i.get('requestedField'),'showRemaining':i.get('showRemaining'),'ids':o.get('resultContactIds'),'out':o.get('outcomeCode')})
            if s['type']=='FunctionStep' and s['function']['name']=='present_results':
                t['tmpl']=(s['function'].get('output') or {}).get('promptResponse','')
            if s['type']=='PlannerResponseStep': t['reply']=s.get('message','')
        out.append(t)
    return out
if __name__=='__main__':
    for lab in sys.argv[1:]:
        d=json.load(open('scripts/scgoe-95/s10-v3/%s.json'%lab))
        for r in d['runs']:
            print('=====',lab,r['run'])
            for t in turns(r['session']):
                print(' U:',t['user']); print('  S:',t['searches']); print('  R:',t['reply'][:260].replace('\n',' | '))
