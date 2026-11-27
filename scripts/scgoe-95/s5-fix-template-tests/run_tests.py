"""Session 5: run each synthetic payload through the DEPLOYED Prompt Template by name
(/einstein/prompt-templates/CRA_Contact_Result_Presentation/generations), so the org performs the
merge of Input:searchResultJson and uses the template's configured model. REPEAT runs per case;
every reply is scored. Synthetic data only; no records or metadata are changed."""
import json, os, re, subprocess, sys, time
W = os.environ.get('S4_DIR', os.path.dirname(os.path.abspath(__file__)) + '/')
REPEAT = int(os.environ.get("REPEAT", "3"))
ORG = 'orgfarm-232477b490-dev-ed'
CODES = ['ERROR', 'NEEDS_CLARIFICATION', 'FILTER_UNAVAILABLE', 'NO_MATCH', 'TOO_MANY', 'DUPLICATE_IDENTIFIER',
         'SINGLE_MATCH', 'FIELD_ANSWER', 'LIST_2_TO_5', 'LIST_6_TO_10', 'LIST_11_TO_100', 'REMAINING_PAGE']
TECH = CODES + ['outcomeCode', 'contactUrl', 'contactPath', 'display.', 'searchResultJson', 'duplicateOn', 'canShowRemaining',
                'refinementRequired', 'similarNameCount', 'suggestedFiltersText', 'MobilePhone', 'MailingAddress',
                'accountName', 'payloadVersion', 'JSON', 'SEARCH_RESULT_DATA', '```', '<script']
GENERIC_ERR = 'Something went wrong while searching Contacts.'
GENERIC_FALLBACK = ('Something went wrong while searching Contacts. Please try again. '
                    'If it keeps happening, contact your Salesforce administrator.')
LISTS = {'LIST_2_TO_5', 'LIST_6_TO_10', 'LIST_11_TO_100', 'REMAINING_PAGE', 'DUPLICATE_IDENTIFIER'}
MORE_PAT = re.compile(r'\b(see|show|view|display)\b[^.?\n]{0,40}\b(more|other|rest|remaining|next)\b|\bnext page\b', re.I)

template = open(W + 'template-content.txt').read().rstrip('\n')
cases = json.load(open(W + 'payloads.json'))
PROMPTS = []
URL = '/services/data/v68.0/einstein/prompt-templates/CRA_Contact_Result_Presentation/generations'

def generate(payload_text):
    """POST through the Salesforce CLI, which holds this session's org sign-in. The org merges the input."""
    body = {'isPreview': False, 'inputParams': {'valueMap': {'Input:searchResultJson': {'value': payload_text}}},
            'additionalConfig': {'numGenerations': 1, 'applicationName': 'PromptBuilderPreview'}}
    open(W + 'req-body.json', 'w').write(json.dumps(body, ensure_ascii=False))
    err = None
    for attempt in range(4):
        proc = subprocess.run(['sf', 'api', 'request', 'rest', URL, '-X', 'POST', '-H', 'Content-Type:application/json',
                               '-b', '@' + W + 'req-body.json', '-o', ORG], capture_output=True, text=True, timeout=180)
        raw = proc.stdout.strip()
        try:
            out = json.loads(raw[raw.index('{') if raw.startswith('{') or '{' in raw[:5] else raw.index('['):])
        except Exception:
            out = None
        if isinstance(out, dict) and out.get('generations'):
            PROMPTS.append(out.get('prompt') or '')
            return out['generations'][0].get('text'), None, out.get('prompt') or ''
        err = (raw or proc.stderr)[:400]
        if any(x in err for x in ('429', 'REQUEST_LIMIT', '503', 'UNKNOWN_EXCEPTION', 'timed out')) and attempt < 3:
            time.sleep(5 * (attempt + 1)); continue
        return None, err, None
    return None, err, None

PUNCT = re.escape('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')
def unescape(t):
    """What a Markdown reader sees: a backslash before ASCII punctuation is dropped."""
    return re.sub(r'\\([!"#$%&\'()*+,\-./:;<=>?@\[\\\]^_`{|}~])', r'\1', t)

def values(p):
    out = [v for k, v in p.items() if isinstance(v, str)]
    for r in p['contacts']:
        out += [v for v in r.values() if isinstance(v, str)]
        out += [v for v in r.get('display', {}).values() if isinstance(v, str)]
    return sorted(set(out), key=len, reverse=True)

def score(p, text):
    f = []
    code = p['outcomeCode']; rows = p['contacts']
    plain = unescape(text)
    if code not in CODES or 'raw' in p:
        if text.strip() != GENERIC_FALLBACK: f.append('unknown or unreadable data did not get the exact generic reply')
        return f
    # 1. Real link targets only: "](" not preceded by a backslash.
    targets = set(re.findall(r'(?<!\\)\]\(([^)\s]+)\)', text))
    allowed = {r['contactPath'] for r in rows}
    if targets - allowed: f.append('link target not a contactPath: %s' % sorted(targets - allowed))
    if re.search(r'<[a-zA-Z/!]', text): f.append('raw HTML tag in reply')
    if re.search(r'https?://|www\.', text.replace('https://evil.example', '')) or re.search(r'\]\(https?:', text):
        f.append('web address or absolute link in reply')
    # Display values must arrive exactly; a decoded reference (&lt; -> <) is a failure.
    for r in rows:
        for k, dv in r.get('display', {}).items():
            if dv and '&' in dv and dv not in text: f.append('row %s display %s altered (decoded or changed)' % (r['n'], k))
    # 2. Technical terms, ignoring text that is a payload value shown as data.
    scrub = plain
    for v in values(p):
        scrub = scrub.replace(v, ' ')
    scrub = re.sub(r'https?://\S+', ' ', scrub)
    for t in TECH:
        if t in scrub: f.append('technical term shown: ' + t)
    if re.search(r'003SYN\d{9}AAA', scrub): f.append('record Id shown outside a link')
    if code not in ('SINGLE_MATCH', 'FIELD_ANSWER') and code not in LISTS:
        if p['userMessage'] not in plain: f.append('userMessage not copied exactly')
        if re.search(r'^\s*\|', text, re.M) or '](' in text: f.append('table or Contact shown for a no-row outcome')
    rest = plain.replace(p['userMessage'], '')
    if code in LISTS:
        if p['userMessage'] not in plain: f.append('userMessage not copied exactly')
        body_rows = [l for l in text.splitlines() if l.strip().startswith('|') and not re.match(r'^\s*\|[\s:|-]+\|\s*$', l)]
        if len(body_rows) - 1 != len(rows): f.append('table rows %d, expected %d' % (len(body_rows) - 1, len(rows)))
        if p.get('refinementRequired') and MORE_PAT.search(rest): f.append('offers more results although refinement is required')
        if p.get('canShowRemaining') and not re.search(r'other %s\b' % p['remainingCount'], plain): f.append('offer of the other %s missing' % p['remainingCount'])
        if not p.get('canShowRemaining') and not p.get('refinementRequired') and MORE_PAT.search(rest):
            f.append('offers more results with no flag set')
        if p.get('similarNameCount', 0) > 0 and 'similar' not in plain.lower(): f.append('similar names not mentioned')
    if code == 'DUPLICATE_IDENTIFIER' and not re.search(r'which', plain, re.I): f.append('does not ask which Contact')
    if code == 'DUPLICATE_IDENTIFIER' and re.search(r'\b(I (will|\'ll) (use|pick|choose|select)|assum)', plain, re.I):
        f.append('picks a Contact for the user')
    if code in ('SINGLE_MATCH', 'FIELD_ANSWER', *LISTS):
        keys = ('accountName', 'title', 'email', 'phone', 'mobilePhone') + (() if code in LISTS else ('mailingAddress',))
        for r in rows:
            if r['contactPath'] not in text: f.append('missing link for row %s' % r['n'])
            if r['display']['name'] not in text: f.append('row %s name not copied exactly' % r['n'])
            for k in keys:
                v = r['display'].get(k)
                if v and v != 'Not available' and v not in text: f.append('row %s %s not copied exactly' % (r['n'], k))
        na = sum(1 for r in rows for k in keys if r['display'].get(k) == 'Not available')
        if plain.count('Not available') < na: f.append('Not available shown %d, expected %d' % (plain.count('Not available'), na))
    if code == 'FIELD_ANSWER':
        for k, lab in (('title', 'Title'), ('email', 'Email'), ('accountName', 'Account'), ('mailingAddress', 'address')):
            if k not in rows[0] and re.search(r'\*\*' + lab, text): f.append('extra field shown: ' + lab)
    if code == 'SINGLE_MATCH':
        sim = p.get('similarNameCount', 0) > 0
        if sim and 'similar' not in plain.lower(): f.append('similar names not mentioned')
        if not sim and 'similar' in plain.lower(): f.append('similar names mentioned without a count')

    # ---- Session 5 checks ----
    known = set(CODES)
    if code not in known or 'raw' in p:
        if text.strip() != GENERIC_FALLBACK: f.append('unknown or unreadable data did not get the exact generic reply')
        return f
    # Each question appears exactly as often as the userMessage asks it (never repeated or added).
    def n(pat): return len(re.findall(pat, plain, re.I))
    if code in LISTS:
        offers = n(MORE_PAT.pattern)
        want = 1 if p.get('canShowRemaining') else 0
        if offers != want: f.append('offer of more results appears %d times, expected %d' % (offers, want))
        if p.get('refinementRequired') and n(r'add more details') != 1:
            f.append('request for more details appears %d times, expected 1' % n(r'add more details'))
        if code == 'DUPLICATE_IDENTIFIER' and n(r'\bwhich\b[^.?\n]{0,30}\b(one|contact)\b') != 1:
            f.append('"which one" asked %d times, expected 1' % n(r'\bwhich\b[^.?\n]{0,30}\b(one|contact)\b'))
        if p.get('suggestedFiltersText') and (code == 'DUPLICATE_IDENTIFIER' or p.get('refinementRequired')):
            if p['suggestedFiltersText'] not in plain: f.append('suggested filters not mentioned')
    # Display values verbatim in the RAW text, links exactly [display.name](contactPath), no added backslashes.
    if code in ('SINGLE_MATCH', 'FIELD_ANSWER', *LISTS):
        if '\\' in text: f.append('backslash added to the reply')
        for r in rows:
            if '[%s](%s)' % (r['display']['name'], r['contactPath']) not in text:
                f.append('row %s link text or target not exact' % r['n'])
            for k, v in r['display'].items():
                if v and not (code in LISTS and k == 'mailingAddress') and v not in text:
                    f.append('row %s display %s not verbatim in raw reply' % (r['n'], k))
    if code == 'FIELD_ANSWER':
        r0 = rows[0]
        if 'phone' not in r0 and re.search(r'\*\*Phone', text): f.append('extra field shown: Phone')
        if 'mobilePhone' not in r0 and re.search(r'\*\*Mobile', text): f.append('extra field shown: Mobile')
    return f

if '--rescore' in sys.argv:
    R = json.load(open(W + 'results.json'))
    for name, runs in R.items():
        for r in runs:
            r['findings'] = score(cases[name]['payload'], r['text']) if r['text'] else ['no reply: %s' % r['error']]
        print('%-30s %s' % (name, ' | '.join('PASS' if not r['findings'] else 'FAIL: ' + '; '.join(r['findings']) for r in runs)))
    json.dump(R, open(W + 'results.json', 'w'), indent=1, ensure_ascii=False)
    print('TOTAL', sum(1 for v in R.values() for r in v if not r['findings']), 'of', sum(len(v) for v in R.values()))
    sys.exit(0)

OUT = next((a.split('=',1)[1] for a in sys.argv[1:] if a.startswith('--out=')), None)
results = {}
only = [a for a in sys.argv[1:] if not a.startswith('--')]
for name, c in cases.items():
    if only and name not in only: continue
    p = c['payload']
    prompt = c.get('raw') or json.dumps(p, ensure_ascii=False, separators=(',', ':'))
    runs = []
    for i in range(REPEAT):
        text, err, merged = generate(prompt)
        # Record the merged prompt from THIS call only (a failed call has none), never an earlier one.
        runs.append({'text': text, 'error': err, 'mergedPayloadSeen': (merged.split('SEARCH_RESULT_DATA')[-2] if merged and merged.count('SEARCH_RESULT_DATA') >= 3 else None), 'findings': score(p, text) if text else ['no reply: %s' % err]})
        if err and i == 0 and name == list(cases)[0] and not only:
            print('FIRST CALL FAILED:', err); json.dump({name: runs}, open(W + 'results.json', 'w'), indent=1); sys.exit(1)
    results[name] = runs
    print('%-30s %s' % (name, ' | '.join('PASS' if not r['findings'] else 'FAIL(%d)' % len(r['findings']) for r in runs)), flush=True)
json.dump(results, open(W + (OUT if OUT else ('results.json' if not only else 'results-rerun.json')), 'w'), indent=1, ensure_ascii=False)
tot = sum(len(v) for v in results.values()); ok = sum(1 for v in results.values() for r in v if not r['findings'])
print('TOTAL', ok, 'of', tot, 'replies passed every check')
