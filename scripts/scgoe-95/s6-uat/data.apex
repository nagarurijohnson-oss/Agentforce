// SCGOE-95 Session 6 synthetic data (approved A2). All records CRA-TEST.
String marker = 'CRA-TEST synthetic record (SCGOE-95 Session 6 UAT)';
Database.DMLOptions opts = new Database.DMLOptions();
opts.DuplicateRuleHeader.allowSave = true;
List<Contact> priv = new List<Contact>{
    new Contact(FirstName='Zed', LastName='Hiddenmore', Email='zed.hiddenmore@synthetic.example', Title='Synthetic Archivist', Phone='+1 555 0611', Description=marker+' P1 private'),
    new Contact(FirstName='Jordan', LastName='Samename', Email='jordan.samename.c@synthetic.example', Title='Synthetic Partner', Phone='+1 555 0113', MailingCity='Hiddenburg', Description=marker+' P2 private'),
    new Contact(FirstName='Priyanka', LastName='Shadowell', Email='priya.synthwell@synthetic.example', Title='Synthetic Controller', Phone='+1 555 0612', Description=marker+' P3 private, shares Priya email'),
    new Contact(FirstName='Coord', LastName='Hidden09', Email='coord9@synthetic.example', Title='Synthetic Coordinator', Phone='+1 555 0319', Description=marker+' P4 private'),
    new Contact(FirstName='Coord', LastName='Hidden10', Email='coord10@synthetic.example', Title='Synthetic Coordinator', Phone='+1 555 0320', Description=marker+' P5 private'),
    new Contact(FirstName='Coord', LastName='Hidden11', Email='coord11@synthetic.example', Title='Synthetic Coordinator', Phone='+1 555 0321', Description=marker+' P6 private')
};
Account bulkAccount = new Account(Name='CRA-TEST Bulk Synthetic', Description=marker+' B1');
insert bulkAccount;
List<Contact> many = new List<Contact>();
for (Integer i = 1; i <= 101; i++) {
    String n = String.valueOf(i).leftPad(3, '0');
    many.add(new Contact(FirstName='Bulk', LastName='Synthetic' + n, AccountId=bulkAccount.Id, Title='Synthetic Bulk Member',
        Email='bulk' + n + '@synthetic.example', Description=marker+' B1'));
}
List<Database.SaveResult> res = Database.insert(priv, opts);
res.addAll(Database.insert(many, opts));
Integer ok = 0;
for (Database.SaveResult r : res) { if (r.isSuccess()) { ok++; } else { System.debug(LoggingLevel.ERROR, 'FAIL ' + r.getErrors()); } }
System.debug(LoggingLevel.ERROR, 'CRA_S6_RESULT inserted=' + ok + ' of ' + res.size() + ' account=' + bulkAccount.Id);
