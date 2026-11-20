import re, os, shutil, sys
W='/tmp/build-52db6c0d-57e1-4383-bac3-df377a70eecc/work'
SRC=open(W+'/Agentforce/force-app/main/default/aiAuthoringBundles/Contact_Read_Agent/Contact_Read_Agent.agent').read()
META=open(W+'/Agentforce/force-app/main/default/aiAuthoringBundles/Contact_Read_Agent/Contact_Read_Agent.bundle-meta.xml').read()
def write(name, text):
    d=f'proj/force-app/main/default/aiAuthoringBundles/{name}'; os.makedirs(d, exist_ok=True)
    text=text.replace('developer_name: "Contact_Read_Agent"', f'developer_name: "{name}"').replace('agent_label: "Contact Read Agent"', f'agent_label: "{name}"')
    open(f'{d}/{name}.agent','w').write(text); open(f'{d}/{name}.bundle-meta.xml','w').write(META)
# promptResponse output made displayable and visible
DISP = SRC.replace('''                promptResponse: string
                    description: "The reply to show the user, exactly as given"
                    is_used_by_planner: False
                    is_displayable: False''','''                promptResponse: string
                    description: "The reply to show the user, exactly as given"
                    is_used_by_planner: True
                    is_displayable: True''')
assert DISP!=SRC
RELAY_START = DISP.index('            if @variables.last_reply != "":')
RELAY_END = DISP.index('            else:\n                | You search Contacts')
# A1: procedural run, displayable output, model told to say only a fixed token
A1 = DISP[:RELAY_START] + '''            if @variables.last_reply != "":
                | Reply with exactly this one word and nothing else: PROBE_DONE
''' + DISP[RELAY_END:]
write('CRA_Probe_A1', A1)
# render-rule variants: present_results exposed as a tool with a render rule on a connection
def render_variant(conn, fmt='@response_formats.json', extra_conn=''):
    s = DISP
    s = s.replace('''            back_to_router: @utils.transition to @subagent.agent_router''', f'''            present_tool: @actions.present_results
                description: "Show the presentation of the last search result"
                with "Input:searchResultJson" = @variables.last_result_json
                when @connection.{conn}
                    render: {fmt}
                        show_and_return: True
            back_to_router: @utils.transition to @subagent.agent_router''')
    s = s.replace('\nvariables:\n', f'\nconnection {conn}:\n{extra_conn}    adaptive_response_allowed: True\n\nvariables:\n', 1)
    return s
write('CRA_Probe_B_slack', render_variant('slack'))
write('CRA_Probe_B_messaging', render_variant('messaging'))
write('CRA_Probe_B_web', render_variant('customer_web_client').replace('    adaptive_response_allowed: True\n','    description: "probe"\n',1))
print('ok')
# B2: no procedural template call; the model must call present_tool (which carries the render rule)
import re
for conn, nm in (('slack','CRA_Probe_B_slack'),('messaging','CRA_Probe_B_messaging'),('customer_web_client','CRA_Probe_B_web')):
    p=f'proj/force-app/main/default/aiAuthoringBundles/{nm}/{nm}.agent'; s=open(p).read()
    a=s.index('            # A search result that has not been presented yet'); z=s.index('            else:\n                | You search Contacts')
    s=s[:a]+'''            if @variables.last_result_json != "":
                | The search is done. Call present_tool now. Write no text of your own.
'''+s[z:]
    open(p,'w').write(s)
print('B2 ok')
