"""Builds the 18-value rendering case (the feasibility-check values, synthetic) as a v3 payload, runs it once
through the v3 template text with the template's model named explicitly, and saves payload + reply."""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); T = HERE + '/../s5-fix-v3-template-tests/'
sys.path.insert(0, T); sys.path.insert(0, HERE + '/../s5-fix-markdown-feasibility')
import payloads as P
from fixtures import VALUES
rows = [P.row(100 + i, i + 1, v, 'Synthetic Freight Ltd', v, 'case%02d@synthetic.example' % (i + 1), '+1 555 01%02d' % i, P.NA, P.NA)
        for i, (_, v) in enumerate(VALUES)]
p = P.payload('REMAINING_PAGE', 'Here are the other 18 matching Contacts.', rows, '23', summary='Job title: Test')
text = json.dumps(p, ensure_ascii=False, separators=(',', ':'))
tmpl = open(T + 'template-content.txt').read().rstrip('\n')
meta = open(HERE + '/../../../force-app/main/default/genAiPromptTemplates/CRA_Contact_Result_Presentation.genAiPromptTemplate-meta.xml').read()
model = re.search(r'<primaryModel>([^<]+)</primaryModel>', meta).group(1)
body = {'promptTextorId': tmpl.replace('{!$Input:searchResultJson}', text),
        'additionalConfig': {'applicationName': 'PromptTemplateGenerationsInvocable', 'model': model, 'numGenerations': 1}}
json.dump(body, open(HERE + '/.req.json', 'w'), ensure_ascii=False)
o = subprocess.run(['sf', 'api', 'request', 'rest', '/services/data/v68.0/einstein/llm/prompt/generations', '-X', 'POST',
                    '-H', 'Content-Type:application/json', '-b', '@' + HERE + '/.req.json', '-o', 'orgfarm-232477b490-dev-ed'],
                   capture_output=True, text=True).stdout
os.remove(HERE + '/.req.json')
reply = json.loads(o[o.index('{'):])['generations'][0]['text']
json.dump({'model': model, 'payload': p, 'reply': reply}, open(HERE + '/render-case-18.json', 'w'), indent=1, ensure_ascii=False)
print(reply)
