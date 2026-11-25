import json,glob,sys
for s in sys.argv[1:]:
    print('=====',s)
    for f in sorted(glob.glob(s+'/traces/*.json')):
        d=json.load(open(f))
        for i,st in enumerate(d['plan']):
            t=st['type']; line=f'{i:2} {t}'
            if t=='FunctionStep':
                fn=st['function']; line+=f" {fn.get('name')} in={json.dumps(fn.get('input'),ensure_ascii=False)[:400]}"
            elif t=='LLMStep':
                dd=st.get('data',{}); line+=f" agent={dd.get('agent_name')} tools_offered={[x.get('name') for x in (dd.get('tools') or [])] if isinstance(dd.get('tools'),list) else ''}"
                pr=dd.get('prompt_response','')
                line+=' resp='+str(pr)[:600]
            else:
                line+=' '+json.dumps(st.get('data',st),ensure_ascii=False)[:400]
            print(line)
