"""Session 11: payload v4. Adds nameLinkable to every row of the Session 5 v3 payloads (same rule as
CRA_ContactSearchAction.isLinkSafeName) and adds hostile-name cases from the Lightning panel test. Synthetic data only."""
import json, re, unicodedata, copy
ESC = ['\\', '<', '>', '[', ']', '|', '*', '_', '`', '~', '#', '&']
def esc(v):
    for c in ESC: v = v.replace(c, '\\' + c)
    return v
WEB = re.compile(r'[^\W\d_]{2,}\.[^\W\d_]{2,}', re.U)
def link_safe(name):
    if not name or not name.strip(): return False
    if not all(unicodedata.category(ch)[0] in 'LMN' or ch in " .,'’\"-" for ch in name): return False
    return not WEB.search(name)
d = json.load(open('payloads.json'))
for k, c in d.items():
    p = c['payload']
    if isinstance(p, dict) and 'payloadVersion' in p: p['payloadVersion'] = 4
    for r in (p.get('contacts') or []) if isinstance(p, dict) else []:
        r['nameLinkable'] = bool(r.get('contactPath')) and link_safe(r.get('name'))
HOSTILE = [
 'Zoë "Zed" O\'Brien-Łukasz 李', 'Eve ](https://evil.example/phish) Linkbreaker', '[Pay here](https://evil.example/pay)',
 'Nested [CEO record](/lightning/r/Contact/003jV00000HCVpUQAX/view)', 'Bob) [x](https://evil.example',
 'Zed <b>VIP</b> <img src=https://evil.example/x.png>', '![x](https://evil.example/x.png) Img', '*Bold* _it_ ~~del~~ `code` # Hash',
 'Ana | Pipe | Split', 'Back\\slash \\] Name', 'Visit https://evil.example now', 'www.evil.example', 'mail me@evil.example',
 '&lt;b&gt; &amp; entity', '<https://evil.example>', '[x](javascript:alert(1))', 'Smith & Jones (Contractor)', 'Ann [Finance] Lee',
 'Priya Synthwell', 'J.R. Smith']
def row(i, name, field_only=None):
    rid = '003SYN0000002%02dAAA' % i
    vals = {'accountName': 'CRA-TEST Hostile Names %02d' % i, 'title': 'Synthetic Title %02d' % i, 'email': 'hostile%02d@synthetic.example' % i,
            'phone': '+1 555 07%02d' % i, 'mobilePhone': 'Not available', 'mailingAddress': '%d Example Street, Testville, Testland' % i}
    if field_only: vals = {field_only: vals[field_only]}
    r = {'n': 0, 'id': rid, 'name': name, 'contactUrl': 'https://cra-synthetic-test.my.salesforce.com/lightning/r/Contact/%s/view' % rid}
    r.update(vals); r['contactPath'] = '/lightning/r/Contact/%s/view' % rid
    r['display'] = {k: esc(v) for k, v in [('name', name)] + list(vals.items())}
    r['nameLinkable'] = link_safe(name); return r
base = {'payloadVersion': 4, 'remainingCount': 0, 'canShowRemaining': False, 'refinementRequired': False, 'similarNameCount': 0,
        'criteriaSummary': 'Job title: Synthetic Title'}
for g in range(4):
    names = HOSTILE[g*5:(g+1)*5]; rows = [row(g*5+j+1, n) for j, n in enumerate(names)]
    for j, r in enumerate(rows): r['n'] = j + 1
    p = dict(base, outcomeCode='LIST_2_TO_5', totalMatchesLabel=str(len(rows)), shownCount=len(rows), userMessage='I found %d matching Contacts.' % len(rows), contacts=rows)
    d['29%s_list_hostile_names' % 'abcd'[g]] = {'note': 'Session 11: 5 hostile or plain names in a list', 'payload': p}
for key, name in (('30_single_hostile_name', '[Pay here](https://evil.example/pay)'), ('31_single_linkable_name', 'Zoë "Zed" O\'Brien-Łukasz 李')):
    r = row(40 if '30' in key else 41, name); r['n'] = 1
    d[key] = {'note': 'Session 11 single match', 'payload': dict(base, outcomeCode='SINGLE_MATCH', totalMatchesLabel='1', shownCount=1,
              userMessage='I found one matching Contact.', singleContactId=r['id'], contacts=[r])}
for key, name in (('32_field_hostile_name', 'Nested [CEO record](/lightning/r/Contact/003jV00000HCVpUQAX/view)'), ('33_field_linkable_name', 'Priya Synthwell')):
    r = row(42 if '32' in key else 43, name, field_only='email'); r['n'] = 1
    d[key] = {'note': 'Session 11 field answer', 'payload': dict(base, outcomeCode='FIELD_ANSWER', totalMatchesLabel='1', shownCount=1,
              requestedFieldLabel='Email', userMessage='Here is the email for this Contact.', singleContactId=r['id'], contacts=[r])}
json.dump(d, open('payloads.json', 'w'), indent=1, ensure_ascii=False)
print(len(d), 'cases;', sum(1 for c in d.values() if isinstance(c['payload'], dict) for r in c['payload'].get('contacts', []) if r.get('nameLinkable')), 'linkable rows of',
      sum(1 for c in d.values() if isinstance(c['payload'], dict) for r in c['payload'].get('contacts', [])))
print([n for n in HOSTILE if link_safe(n)])
