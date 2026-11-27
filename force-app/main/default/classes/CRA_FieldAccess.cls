/*****************************************************************
Name:          CRA_FieldAccess
============================================================
Purpose:       Object and field read checks for the running user,
               used by CRA_ContactSearchService to decide which fields
               it may select and which filters it may apply BEFORE it
               runs a USER_MODE query (a USER_MODE query that touches
               an unreadable field fails instead of returning data).
               USER_MODE on every query remains the enforcement; this
               class only lets the service degrade gracefully.
               The class is virtual so tests can substitute a
               simulated access profile (the "access seam").
============================================================
History
-------
VERSION  AUTHOR                  DATE         DETAIL    DESCRIPTION
1.0      Revecast Orchestrate    19/11/2026   Created   SCGOE-95 Session 2
1.1      Revecast Orchestrate    27/11/2026   Updated   SCGOE-95 AID-1:
                                                      Account Id filter and
                                                      visibility checks
*****************************************************************/
public virtual with sharing class CRA_FieldAccess {

    // Describe of Contact fields, loaded once per transaction.
    private static Map<String, Schema.SObjectField> contactFields;

    /*****************************************************************
    Purpose:   True when the running user can read Contact records.
    *****************************************************************/
    public virtual Boolean isContactReadable() {
        return Schema.SObjectType.Contact.isAccessible();
    }

    /*****************************************************************
    Purpose:   True when the running user can read a Contact's
               Account name (Contact.AccountId and Account.Name).
    *****************************************************************/
    public virtual Boolean isAccountNameReadable() {
        return isContactFieldReadable('AccountId')
            && Schema.SObjectType.Account.isAccessible()
            && Schema.SObjectType.Account.fields.Name.isAccessible();
    }

    /*****************************************************************
    Purpose:   True when the running user may filter Contacts by an
               Account Id: Read on Contact.AccountId and on Account.
               No Account field is selected or returned (AID-1).
    *****************************************************************/
    public virtual Boolean isAccountIdFilterable() {
        return isContactFieldReadable('AccountId') && Schema.SObjectType.Account.isAccessible();
    }

    /*****************************************************************
    Purpose:   True when the running user can see the Account record,
               checked with a USER_MODE query (sharing, object access).
               Only the Id is selected. A missing Account and a hidden
               one both return false, so callers answer them alike.
    Parameters: accountId — a validated Account Id.
    *****************************************************************/
    public virtual Boolean isAccountRecordVisible(Id accountId) {
        List<Account> visible = Database.queryWithBinds(
            'SELECT Id FROM Account WHERE Id = :accountIdValue LIMIT 1',
            new Map<String, Object>{ 'accountIdValue' => accountId }, AccessLevel.USER_MODE);
        return !visible.isEmpty();
    }

    /*****************************************************************
    Purpose:   True when the running user can read the Contact field.
    Parameters: fieldName — Contact field API name, e.g. Email.
    Returns:   false for a field that does not exist in this org.
    *****************************************************************/
    public virtual Boolean isContactFieldReadable(String fieldName) {
        Schema.SObjectField field = getContactFields().get(fieldName);
        return field != null && field.getDescribe().isAccessible();
    }

    /*****************************************************************
    Purpose:   True when the Contact field exists in this org, whatever
               the user's access. Used for MailingStateCode and
               MailingCountryCode, which exist only when state and
               country picklists are enabled.
    *****************************************************************/
    public Boolean contactFieldExists(String fieldName) {
        return getContactFields().containsKey(fieldName);
    }

    /*****************************************************************
    Purpose:   Lazily load the Contact field map.
    *****************************************************************/
    private static Map<String, Schema.SObjectField> getContactFields() {
        if (contactFields == null) {
            contactFields = Schema.SObjectType.Contact.fields.getMap();
        }
        return contactFields;
    }
}
