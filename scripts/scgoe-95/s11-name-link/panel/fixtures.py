import re, json
NAMES = [
 'Priya Synthwell',
 'Zoë "Zed" O\'Brien-Łukasz 李',
 'Eve ](https://evil.example/phish) Linkbreaker',
 '[Pay here](https://evil.example/pay)',
 'Nested [CEO record](/lightning/r/Contact/003jV00000HCVpUQAX/view)',
 'Bob) [x](https://evil.example',
 'Zed <b>VIP</b> <img src=https://evil.example/x.png>',
 '![x](https://evil.example/x.png) Img',
 '*Bold* _it_ ~~del~~ `code` # Hash',
 'Ana | Pipe | Split',
 'Back\\slash \\] Name',
 'Visit https://evil.example now',
 'www.evil.example',
 'mail me@evil.example',
 '&lt;b&gt; &amp; entity',
 '<https://evil.example>',
 '[x](javascript:alert(1))',
 'Smith & Jones (Contractor)',
 'Ann [Finance] Lee',
]
ESC = ['\\','<','>','[',']','|','*','_','`','~','#','&']
def esc(v):
    for c in ESC: v = v.replace(c, '\\'+c)
    return v
def strip(t):  # what L-1 does: escape backslashes removed
    return re.sub(r'\\([!"#$%&\'()*+,\-./:;<=>?@\[\\\]^_`{|}~])', r'\1', t)
def path(k): return '/lightning/r/Contact/003SYN0000000%02dAAA/view' % k
def table(link_text):
    lines = ['Here are the test values.', '', '| # | Name | Account | Title |', '|---|---|---|---|']
    for k, n in enumerate(NAMES, 1):
        lines.append('| %d | [%s](%s) | ACC%02d | TTL%02d |' % (k, link_text(n), path(k), k, k))
    return '\n'.join(lines)
def single(link_text):
    out = ['I found one matching Contact.']
    for k, n in enumerate(NAMES, 1):
        out.append('**Name:** [%s](%s)\n**Account:** ACC%02d' % (link_text(n), path(k), k))
    return '\n\n'.join(out)
FIX = {
 'T-esc': table(esc), 'T-L1': strip(table(esc)),
 'S-esc': single(esc), 'S-L1': strip(single(esc)),
}
if __name__ == '__main__':
    json.dump({'names': NAMES, 'fixtures': FIX}, open('s11/fixtures.json','w'), indent=1, ensure_ascii=False)
    print(FIX['T-esc'][:900])

SAFE = re.compile(r"^[\w\s.,'’\"-]+$", re.U)
DOMAIN = re.compile(r'[^\W\d_]{2,}\.[^\W\d_]{2,}', re.U)
def linkable(n): return bool(SAFE.match(n)) and '_' not in n and not DOMAIN.search(n)
def table_g(e):
    lines = ['Here are the test values.', '', '| # | Name | Account | Title |', '|---|---|---|---|']
    for k, n in enumerate(NAMES, 1):
        cell = '[%s](%s)' % (e(n), path(k)) if linkable(n) else '%s — [Open record](%s)' % (e(n), path(k))
        lines.append('| %d | %s | ACC%02d | TTL%02d |' % (k, cell, k, k))
    return '\n'.join(lines)
def single_g(e):
    out = ['I found one matching Contact.']
    for k, n in enumerate(NAMES, 1):
        v = '[%s](%s)' % (e(n), path(k)) if linkable(n) else '%s — [Open record](%s)' % (e(n), path(k))
        out.append('**Name:** %s\n**Account:** ACC%02d' % (v, k))
    return '\n\n'.join(out)
def table_o(e):
    lines = ['Here are the test values.', '', '| # | Name | Record | Account | Title |', '|---|---|---|---|---|']
    for k, n in enumerate(NAMES, 1):
        lines.append('| %d | %s | [Open record](%s) | ACC%02d | TTL%02d |' % (k, e(n), path(k), k, k))
    return '\n'.join(lines)
FIX2 = {'O-esc': table_o(esc), 'O-L1': strip(table_o(esc)), 'G-esc': table_g(esc), 'G-L1': strip(table_g(esc)),
        'GS-esc': single_g(esc), 'GS-L1': strip(single_g(esc))}
if __name__ == '__main__':
    json.dump({'names': NAMES, 'fixtures': FIX2, 'linkable': [linkable(n) for n in NAMES]}, open('s11/fixtures2.json','w'), indent=1, ensure_ascii=False)
    print([ (n, linkable(n)) for n in NAMES])
