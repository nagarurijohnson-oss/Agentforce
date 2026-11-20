"""Test replies for the Builder rendering check. Values are synthetic. E* = proposed v3 Markdown escaping, C* = unescaped / v2 controls."""
import json
ESC = ['\\', '<', '>', '[', ']', '|', '*', '_', '`', '~', '#', '&']
def md(v):
    v = v.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    for c in ESC: v = v.replace(c, '\\' + c)
    return v
P = '/lightning/r/Contact/003jV00000GrntVQAR/view'
VALUES = [  # (label, original value)
 ('V01 bold tag', 'Smith | Jones & Co <b>LLC</b>'),
 ('V02 script tag', 'Ann <script>alert(1)</script> Lee'),
 ('V03 img onerror', '<img src=x onerror=alert(1)>Img'),
 ('V04 md link', '[click here](https://evil.example/phish)'),
 ('V05 js link', '[open](javascript:alert(1))'),
 ('V06 autolink angle', '<https://evil.example/auto>'),
 ('V07 bare url', 'Visit https://evil.example/bare now'),
 ('V08 www', 'see www.evil.example today'),
 ('V09 html anchor', '<a href="https://evil.example/a">Pay here</a>'),
 ('V10 pipe', 'Sales | EMEA'),
 ('V11 backslash', 'C:\\Temp\\new and \\* star'),
 ('V12 entity amp', 'R&amp;D literal'),
 ('V13 entity lt', 'Tag &lt;b&gt; literal &#124; code'),
 ('V14 emphasis', '*bold* _ital_ ~~strike~~ `code`'),
 ('V15 heading', '# Heading text'),
 ('V16 image', '![x](https://evil.example/x.png)'),
 ('V17 email', 'zed.obrien@synthetic.example'),
 ('V18 quotes', 'Zoë "Zed" O\'Brien-Núñez [VIP]'),
]
def table(f):
    rows = ['| # | Case | Value |', '|---|---|---|']
    for i, (lab, v) in enumerate(VALUES, 1): rows.append('| %d | %s | %s |' % (i, lab, f(v)))
    return '\n'.join(rows)
def single(f):
    return ('I found one matching Contact.  \n**Name:** [%s](%s)  \n**Account:** %s  \n**Title:** %s  \n**Email:** %s'
            % (f('Zoë "Zed" O\'Brien <b>VIP</b> [x](https://evil.example)'), P, f('Smith | Jones & Co <b>LLC</b>'),
               f('<script>alert(1)</script> CFO'), f('zed.obrien@synthetic.example')))
FIX = {
 'E1_table_escaped': 'Here are the test values.\n\n' + table(md),
 'E2_single_escaped': single(md),
 'C1_table_raw': 'Here are the test values.\n\n' + table(lambda v: v),
 'C2_single_raw': single(lambda v: v),
}
if __name__ == '__main__':
    json.dump({'values': VALUES, 'fixtures': FIX}, open('fixtures.json', 'w'), indent=1, ensure_ascii=False)
    print(FIX['E1_table_escaped'])

ESC_X = ESC + [':', '.', '@']
def mdx(v):
    v = v.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    for c in ESC_X: v = v.replace(c, '\\' + c)
    return v
FIX['E3_table_extended'] = 'Here are the test values.\n\n' + table(mdx)
json.dump({'values': VALUES, 'fixtures': FIX}, open('fixtures.json', 'w'), indent=1, ensure_ascii=False)
