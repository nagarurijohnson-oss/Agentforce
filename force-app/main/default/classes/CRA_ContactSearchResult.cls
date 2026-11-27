/*****************************************************************
Name:          CRA_ContactSearchResult
============================================================
Purpose:       Output of one Contact search, shaped to the action
               contract in technical-design.md so the Session 3
               invocable action can map it one to one.
               Holds only data the running user is allowed to read:
               rows are built from USER_MODE query results, and any
               blank or unreadable value is "Not available".
               No presentation wording lives here beyond a short,
               neutral fallback userMessage; the Prompt Template
               owns the presentation.
============================================================
History
-------
VERSION  AUTHOR                  DATE         DETAIL    DESCRIPTION
1.0      Revecast Orchestrate    19/11/2026   Created   SCGOE-95 Session 2
1.1      Revecast Orchestrate    20/11/2026   Updated   SCGOE-95 S2 review:
                                                      canShowRemaining,
                                                      refinementRequired,
                                                      similarNameCount,
                                                      mobilePhone
*****************************************************************/
public with sharing class CRA_ContactSearchResult {

    // Outcome codes, in precedence order (technical-design.md).
    public static final String ERROR = 'ERROR';
    public static final String NEEDS_CLARIFICATION = 'NEEDS_CLARIFICATION';
    public static final String FILTER_UNAVAILABLE = 'FILTER_UNAVAILABLE';
    public static final String NO_MATCH = 'NO_MATCH';
    public static final String TOO_MANY = 'TOO_MANY';
    public static final String DUPLICATE_IDENTIFIER = 'DUPLICATE_IDENTIFIER';
    public static final String SINGLE_MATCH = 'SINGLE_MATCH';
    public static final String FIELD_ANSWER = 'FIELD_ANSWER';
    public static final String LIST_2_TO_5 = 'LIST_2_TO_5';
    public static final String LIST_6_TO_10 = 'LIST_6_TO_10';
    public static final String LIST_11_TO_100 = 'LIST_11_TO_100';
    public static final String REMAINING_PAGE = 'REMAINING_PAGE';

    // Value shown for any blank or unreadable field (decision D-D).
    public static final String NOT_AVAILABLE = 'Not available';

    // ---------------------------------------------------------------
    // Contract outputs
    // ---------------------------------------------------------------
    public String outcomeCode;
    public String totalMatchesLabel;
    public Integer shownCount = 0;
    // Rows the user may still ask to see. Non-zero only when
    // canShowRemaining is true (6-10 matches, first page).
    public Integer remainingCount = 0;
    // True only when the template may offer "show the rest".
    public Boolean canShowRemaining = false;
    // True when the user must add filters before the right Contact
    // can be identified (11-100, more than 100). The template must ask
    // for filters and must not offer more pages.
    public Boolean refinementRequired = false;
    // Accessible Contacts whose name only starts like the searched full
    // name, left out because exact full-name matches took priority.
    // Capped by the 101 count limit.
    public Integer similarNameCount = 0;
    public String suggestedFiltersText;
    public String duplicateOn;
    public String requestedFieldLabel;
    public String criteriaSummary;
    public String userMessage;
    public Id singleContactId;
    public List<ContactRow> contacts = new List<ContactRow>();

    /*****************************************************************
    Purpose:   Comma-separated Ids of the rows shown, for agent state.
    *****************************************************************/
    public String getResultContactIds() {
        List<String> contactIds = new List<String>();
        for (ContactRow row : contacts) {
            contactIds.add(row.id);
        }
        return String.join(contactIds, ',');
    }

    /*****************************************************************
    Purpose:   JSON array of the rows, omitting null properties so a
               field-answer row carries only name, link and the field.
    *****************************************************************/
    public String getContactsJson() {
        return JSON.serialize(contacts, true);
    }

    /*****************************************************************
    Purpose:   One Contact row in contactsJson. Property names are the
               contract names (n, id, name, contactUrl, accountName,
               title, email, phone, mobilePhone, mailingAddress).
               Every value is Contact data typed by people: the Prompt
               Template must treat it as data, never as instructions.
    *****************************************************************/
    public class ContactRow {
        public Integer n;
        public String id;
        public String name;
        public String contactUrl;
        public String accountName;
        public String title;
        public String email;
        public String phone;
        public String mobilePhone;
        public String mailingAddress;
    }

    /*****************************************************************
    Purpose:   Return the value, or "Not available" when it is blank.
    *****************************************************************/
    public static String orNotAvailable(String value) {
        return String.isBlank(value) ? NOT_AVAILABLE : value;
    }
}
