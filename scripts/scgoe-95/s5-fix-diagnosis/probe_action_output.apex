// Read-only probe on the synthetic CRA-TEST record only: is the display value escaped when Apex returns it?
Invocable.Action a = Invocable.Action.createCustomAction('apex', 'CRA_ContactSearchAction');
a.setInvocationParameter('email', 'zed.obrien@synthetic.example');
List<Invocable.Action.Result> rs = a.invoke();
String j = (String) rs[0].getOutputParameters().get('searchResultJson');
Integer i = j.indexOf('LLC');
System.debug('PROBE>>' + j.substring(Math.max(0, i - 60), i + 30));
