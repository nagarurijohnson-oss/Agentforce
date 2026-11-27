import re,sys
src=open('v6.agent').read()
CF_SEARCH="I couldn't run the Contact search just now, so I'm not showing any Contact details. Please try again in a moment. If it keeps happening, contact your Salesforce administrator."
CF_PRESENT="The Contact search ran, but I couldn't display its result just now, so I'm not showing any Contact details. Please try again in a moment. If it keeps happening, contact your Salesforce administrator."
KB_FAIL="I couldn't get an answer from the published Knowledge articles just now, so I can't answer this question, and I won't answer it from memory. Please try again in a moment. If it keeps happening, contact your Salesforce administrator."
def rep(s,old,new,count):
    n=s.count(old)
    if n!=count: sys.exit(f"expected {count} got {n}: {old[:80]!r}")
    return s.replace(old,new)
I12=' '*12; I16=' '*16
# 1 header
src=rep(src,"# new search (seen in v4's mixed Contact and Knowledge request, 2 of 3 runs).\n",
"# new search (seen in v4's mixed Contact and Knowledge request, 2 of 3 runs).\n"
"# D-8 (2026-11-26, v7): fail closed. A template step (present_results, answer_from_knowledge) or a search that\n"
"# was due but did not produce output (skipped for a missing permission, failed, null or empty) no longer hands\n"
"# the turn back to the planner. The script sets contact_failed / kb_failed and puts a fixed failure message in\n"
"# the reply, which is relayed unchanged; the planner's actions are switched off for the rest of that turn.\n",1)
# 2 variables
src=rep(src,'''        description: "new or narrow, set by the action that stored the latest message's details; emptied at the start of every turn"\n''',
'''        description: "new or narrow, set by the action that stored the latest message's details; emptied at the start of every turn"
    contact_failed: mutable boolean = False
        description: "D-8: True when this turn's Contact search or its presentation produced no output; the fixed failure message is shown. Cleared every turn"
    kb_failed: mutable boolean = False
        description: "D-8: True when this turn's Knowledge answer produced no output; the fixed failure message is shown. Cleared every turn"
    kb_attempted: mutable boolean = False
        description: "D-8: True once the Knowledge answer step was due in this turn. Cleared every turn"
    page_attempted: mutable boolean = False
        description: "D-8: True once the next-page search was due in this turn. Cleared every turn"
''',1)
# 3 router reset
src=rep(src,'''        set @variables.in_mode = ""\n    reasoning:''','''        set @variables.in_mode = ""
        # D-8: failure flags are per turn.
        set @variables.contact_failed = False
        set @variables.kb_failed = False
        set @variables.kb_attempted = False
        set @variables.page_attempted = False
    reasoning:''',1)
# 4 search failed (contact_search + contact_and_knowledge): insert after the search callback block
SEARCH_END=I16+'    set @variables.search_pending = False\n'+I16+'    set @variables.criteria_requested_field = ""\n'
SEARCH_FAIL=(I12+'# D-8 (v7): a search that was due but did not run (skipped or failed) fails closed.\n'
 +I12+'if @variables.search_pending == True:\n'
 +I16+'set @variables.contact_failed = True\n'+I16+'set @variables.search_pending = False\n'
 +I16+'set @variables.remaining_available = False\n'+I16+'set @variables.last_result_json = ""\n'
 +I16+f'set @variables.last_reply = "{CF_SEARCH}"\n'
 +I12+'if @variables.last_result_json is None:\n'+I16+'set @variables.last_result_json = ""\n')
src=rep(src,SEARCH_END,SEARCH_END+SEARCH_FAIL,2)
# 5 presentation failed (contact_search, contact_page, contact_and_knowledge)
PRES=(I12+'if @variables.last_result_json != "" and @variables.last_reply == "":\n'+I16+'run @actions.present_results\n'
 +I16+'    with "Input:searchResultJson" = @variables.last_result_json\n'+I16+'    set @variables.last_reply = @outputs.promptResponse\n')
PRES_FAIL=(I12+'if @variables.last_reply is None:\n'+I16+'set @variables.last_reply = ""\n'
 +I12+'# D-8 (v7): a result the template did not turn into a reply (skipped, failed, null or empty) fails closed.\n'
 +I12+'if @variables.last_result_json != "" and @variables.last_reply == "":\n'
 +I16+'set @variables.contact_failed = True\n'+I16+'set @variables.remaining_available = False\n'
 +I16+f'set @variables.last_reply = "{CF_PRESENT}"\n')
src=rep(src,PRES,PRES+PRES_FAIL,3)
# 6 paging attempted + skipped search
src=rep(src,I12+'if @variables.remaining_available == True:\n'+I16+'run @actions.search_contacts\n',
 I12+'if @variables.remaining_available == True:\n'+I16+'set @variables.page_attempted = True\n'+I16+'run @actions.search_contacts\n',1)
PAGE_END=I16+'    set @variables.last_reply = ""\n'+PRES
assert src.count(PAGE_END)==1
src=src.replace(PAGE_END, I16+'    set @variables.last_reply = ""\n'
 +I12+'# D-8 (v7): a next-page search that was due but did not run fails closed, not as "no other Contacts".\n'
 +I12+'if @variables.page_attempted == True and @variables.remaining_available == True:\n'
 +I16+'set @variables.contact_failed = True\n'+I16+'set @variables.remaining_available = False\n'
 +I16+'set @variables.last_result_json = ""\n'+I16+f'set @variables.last_reply = "{CF_SEARCH}"\n'
 +I12+'if @variables.last_result_json is None:\n'+I16+'set @variables.last_result_json = ""\n'+PRES)
# 7 knowledge attempted + failure (knowledge_search + contact_and_knowledge)
KB=(I12+'if @variables.kb_pending == True:\n'+I16+'run @actions.answer_from_knowledge\n'
 +I16+'    with "Input:question" = @variables.kb_question\n'+I16+'    set @variables.kb_reply = @outputs.promptResponse\n'
 +I16+'    set @variables.kb_pending = False\n')
KB_NEW=(I12+'if @variables.kb_pending == True:\n'+I16+'set @variables.kb_attempted = True\n'+I16+'run @actions.answer_from_knowledge\n'
 +I16+'    with "Input:question" = @variables.kb_question\n'+I16+'    set @variables.kb_reply = @outputs.promptResponse\n'
 +I16+'    set @variables.kb_pending = False\n'
 +I12+'if @variables.kb_reply is None:\n'+I16+'set @variables.kb_reply = ""\n'
 +I12+'# D-8 (v7): an answer step that was due but produced nothing (skipped, failed, null or empty) fails closed.\n'
 +I12+'if @variables.kb_attempted == True and @variables.kb_reply == "":\n'
 +I16+'set @variables.kb_failed = True\n'+I16+'set @variables.kb_pending = False\n'
 +I16+f'set @variables.kb_reply = "{KB_FAIL}"\n')
src=rep(src,KB,KB_NEW,2)
# 8 actions off after failure
for name in ['new_search','narrow_search','select_contact']:
    pat=f'            {name}: @utils.setVariables\n'
    i=src.index(pat); j=src.index('\n',src.index('description:',i))+1
    src=src[:j]+'                available when @variables.contact_failed == False\n'+src[j:]
src=rep(src,'                available when @variables.selected_contact_id != ""\n',
 '                available when @variables.selected_contact_id != "" and @variables.contact_failed == False\n',1)
src=rep(src,'                available when @variables.remaining_available == True\n',
 '                available when @variables.remaining_available == True and @variables.contact_failed == False\n',1)
for name,cond in [('set_question','@variables.kb_failed == False'),('set_both','@variables.contact_failed == False and @variables.kb_failed == False')]:
    pat=f'            {name}: @utils.setVariables\n'
    i=src.index(pat); j=src.index('\n',src.index('description:',i))+1
    src=src[:j]+f'                available when {cond}\n'+src[j:]
# 9 after_reasoning resets
cs_after='''    after_reasoning:
        set @variables.last_reply = ""
        set @variables.last_result_json = ""
        set @variables.search_pending = False
        set @variables.criteria_requested_field = ""
'''
assert src.count(cs_after)==2  # contact_search, contact_and_knowledge
src=src.replace(cs_after,cs_after+'        set @variables.contact_failed = False\n')
src=rep(src,'''        set @variables.kb_reply = ""
        set @variables.kb_pending = False
''','''        set @variables.kb_reply = ""
        set @variables.kb_pending = False
        set @variables.kb_failed = False
        set @variables.kb_attempted = False
''',2)
pg_after='''    after_reasoning:
        set @variables.last_reply = ""
        set @variables.last_result_json = ""

subagent knowledge_search:'''
src=rep(src,pg_after,'''    after_reasoning:
        set @variables.last_reply = ""
        set @variables.last_result_json = ""
        set @variables.contact_failed = False
        set @variables.page_attempted = False

subagent knowledge_search:''',1)
open('v7.agent','w').write(src)
print('ok',len(src.splitlines()))
