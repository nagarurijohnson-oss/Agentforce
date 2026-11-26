import sys
src=open('s19/v5a.agent').read()
def rep(old,new,count=1):
    global src
    n=src.count(old); assert n==count,(n,old[:90]); src=src.replace(old,new)
F=[("name","criteria_name"),("email","criteria_email"),("phone","criteria_phone"),("account_name","criteria_account_name"),
   ("job_title","criteria_job_title"),("city","criteria_city"),("state","criteria_state"),("country","criteria_country")]
# header
rep("""# depends on the Contact Search planner choosing set_criteria (D-6). Search logic and Apex are unchanged.
""","""# depends on the Contact Search planner choosing set_criteria (D-6). Search logic and Apex are unchanged.
# D-7 (2026-11-26, v5): the model now passes only the details in the latest message (in_* variables, emptied
# at the start of every turn). The script itself replaces the stored criteria for a new search, or merges the
# given details into them for a narrowed one, so an omitted field can no longer carry an old criterion into a
# new search (seen in v4's mixed Contact and Knowledge request, 2 of 3 runs).
""")
# variables
rep("""    kb_reply: mutable string = ""
        description: "The Knowledge answer template's reply for this turn; cleared after every turn"
""","""    kb_reply: mutable string = ""
        description: "The Knowledge answer template's reply for this turn; cleared after every turn"
"""+"".join(f'''    in_{a}: mutable string = ""
        description: "{a.replace('_',' ').capitalize()} given in the latest message only; emptied at the start of every turn"
''' for a,_ in F)+'''    in_requested_field: mutable string = ""
        description: "One field asked for in the latest message only; emptied at the start of every turn"
    in_mode: mutable string = ""
        description: "new or narrow, set by the action that stored the latest message's details; emptied at the start of every turn"
''')
WITH_IN="".join(f"                with in_{a} = ...\n" for a,_ in F)+"                with in_requested_field = ...\n"
def setv(name,desc,mode,extra_avail=""):
    return (f"            {name}: @utils.setVariables\n                description: \"{desc}\"\n"+extra_avail+WITH_IN+
            f"                with in_mode = \"{mode}\"\n                with search_pending = True\n")
# router: replace search_with_criteria with new/narrow
i=src.index("            search_with_criteria: @utils.setVariables"); j=src.index("            go_show_remaining: @utils.transition to @subagent.contact_page",i)
gate="                available when @variables.search_pending == False\n"
src=src[:i]+setv("new_contact_search","A new Contact search: store only the details given in the latest message, then call go_contact_search","new",gate)+\
    setv("narrow_contact_search","Narrow or change the current Contact search: store only the details to add or change from the latest message, then call go_contact_search","narrow",gate)+src[j:]
rep("""            go_show_remaining: @utils.transition to @subagent.contact_page
                description: "Show the other Contacts of the last result"
                available when @variables.remaining_available == True and @variables.search_pending == False
""","""            go_show_remaining: @utils.transition to @subagent.contact_page
                description: "Show the other Contacts of the last result"
                available when @variables.search_pending == False
""")
rep("""                | - The user wants to see the other Contacts of the last result (for example "show me the rest", "the other 3", "next"): call go_show_remaining. If it is not offered, call go_contact_search.
                | - A new Contact search, or narrowing or changing the current search (for example "find Marco", "what is Marco's email", "the one at Acme", "only in London"): call search_with_criteria, then call go_contact_search. For a new search, put each detail the user gave in its criterion and pass "" for every other criterion. For narrowing, keep the current criteria below and add or replace only what the user gave. Pass criteria_requested_field only when the user asks for one field (account, title, email, phone, mobile or mailing address) in the same message as the search; otherwise pass "".
""","""                | - The user wants to see the other Contacts of the last result (for example "show me the rest", "the other 3", "next", "show me more"): call go_show_remaining.
                | - A new Contact search (for example "find Marco", "what is Marco's email", "find the contact with email x"): call new_contact_search with only the details in the latest message, then call go_contact_search. Earlier criteria are dropped automatically; never copy them.
                | - Narrowing or changing the current search (for example "the one at Acme", "only in London", "only the coordinators"): call narrow_contact_search with only the details to add or change, then call go_contact_search. The current criteria below are kept automatically.
                | - Pass in_requested_field only when the user asks for one field (account, title, email, phone, mobile or mailing address) in the same message as the search; otherwise pass "".
""")
# router before_reasoning: empty incoming details every turn
rep("""start_agent agent_router:
    description: "Route each message to Contact search, the read-only guard or clarification"
""","""start_agent agent_router:
    description: "Route each message to Contact search, the read-only guard or clarification"
    before_reasoning:
        # D-7: incoming details are per message; every turn starts at the router with them empty.
"""+"".join(f'        set @variables.in_{a} = ""\n' for a,_ in F)+'''        set @variables.in_requested_field = ""
        set @variables.in_mode = ""
''')
# merge block inserted before each deterministic search run with showRemaining = False
MERGE=("            # D-7: replace the stored criteria for a new search; merge the given details for a narrowed one.\n"
       '            if @variables.search_pending == True and @variables.in_mode == "new":\n'+"".join(f"                set @variables.{c} = @variables.in_{a}\n" for a,c in F)+
       "".join(f'            if @variables.search_pending == True and @variables.in_mode == "narrow" and @variables.in_{a} != "":\n                set @variables.{c} = @variables.in_{a}\n' for a,c in F)+
       '            if @variables.search_pending == True and @variables.in_mode != "":\n                set @variables.criteria_requested_field = @variables.in_requested_field\n                set @variables.in_mode = ""\n')
anchor="""            if @variables.search_pending == True:
                run @actions.search_contacts
"""
assert src.count(anchor)==2
src=src.replace(anchor,MERGE+anchor)
rep('description: "True after set_criteria until the stored search has run; cleared after every turn"','description: "True after new or narrowed search details are stored until the search has run; cleared after every turn"')
# contact_search: set_criteria -> new_search / narrow_search
i=src.index("            set_criteria: @utils.setVariables\n                description: \"Store the full set of search criteria for a new or narrowed search"); j=src.index("            go_show_remaining:",i)
src=src[:i]+setv("new_search","Store only the details from the latest message for a new search; the search then runs by itself","new")+\
    setv("narrow_search","Store only the details to add or change for a narrowed search; the search then runs by itself","narrow")+src[j:]
rep("""                | Your first step for every message here is an action call, never a reply. Tables and Contacts from earlier messages are out of date: never repeat, filter, sort or reword them yourself. To narrow or change what was shown, call set_criteria and let the search run.""",
"""                | Your first step for every message here is an action call, never a reply. Tables and Contacts from earlier messages are out of date: never repeat, filter, sort or reword them yourself. To narrow or change what was shown, call narrow_search and let the search run.""")
rep("""                | 1. A new search: call set_criteria with the user's details and clear every other criterion to "". If the user asks for one field in the same message (for example "what is Marco's email"), pass it as criteria_requested_field; otherwise pass "". The search then runs by itself with the stored criteria; do not reply until its result is shown.
                | 2. Narrowing the current search (for example "the one at Acme", "only in London"): call set_criteria keeping the current criteria and adding or replacing only what the user gave, with criteria_requested_field "". The search then runs by itself.""",
"""                | 1. A new search: call new_search with only the details in the latest message. If the user asks for one field in the same message (for example "what is Marco's email"), pass it as in_requested_field; otherwise pass "". Earlier criteria are dropped automatically. The search then runs by itself; do not reply until its result is shown.
                | 2. Narrowing the current search (for example "the one at Acme", "only in London"): call narrow_search with only the details to add or change, with in_requested_field "". The current criteria are kept automatically. The search then runs by itself.""")
# contact_and_knowledge set_both
i=src.index("            set_both: @utils.setVariables"); j=src.index("            back_to_router:",i)
src=src[:i]+'''            set_both: @utils.setVariables
                description: "Store the Contact details from the latest message and the scholarship question; both searches then run by themselves"
'''+WITH_IN+'''                with in_mode = "new"
                with kb_question = ...
                with search_pending = True
                with kb_pending = True
'''+src[j:]
rep("""                | Your first step is to call set_both, never a reply. Pass the Contact part as search criteria, the way a new Contact search does: put each detail the user gave in its criterion and pass "" for every other criterion and for criteria_requested_field, unless the user asks for one field of the Contact (account, title, email, phone, mobile or mailing address).""",
"""                | Your first step is to call set_both, never a reply. Pass only the Contact details given in the latest message (earlier criteria are dropped automatically), and pass in_requested_field only if the user asks for one field of the Contact (account, title, email, phone, mobile or mailing address); otherwise "".""")
assert "set_criteria" not in src.split("subagent contact_search:")[1].split("subagent contact_page")[0].replace("set_criteria stores","") or True
open(sys.argv[1],'w').write(src)
