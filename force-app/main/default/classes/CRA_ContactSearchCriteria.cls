/*****************************************************************
Name:          CRA_ContactSearchCriteria
============================================================
Purpose:       Search criteria for the SCGOE-95 Contact Read Agent.
               Holds the raw inputs the agent sends and turns them
               into validated, normalised values the search service
               can bind safely into a query.
               - Control characters are removed and whitespace collapsed.
               - Over-long values are rejected, never truncated, so a
                 value can never be shortened into a wider search.
               - Phone numbers are reduced to digits.
               - requestedField is matched against a fixed whitelist.
               - contactId must be a well-formed Contact Id.
               This class runs no queries and performs no DML.
============================================================
History
-------
VERSION  AUTHOR                  DATE         DETAIL    DESCRIPTION
1.0      Revecast Orchestrate    19/11/2026   Created   SCGOE-95 Session 2
*****************************************************************/
public with sharing class CRA_ContactSearchCriteria {

    // Maximum accepted length per input, aligned to the Contact field
    // lengths in the org (Name 121, Email 80, Phone 40, Title 128,
    // MailingCity 40, MailingState 80, MailingCountry 80; Account Name 255).
    @TestVisible
    private static final Map<String, Integer> MAX_LENGTH = new Map<String, Integer>{
        'name' => 121,
        'email' => 80,
        'phone' => 40,
        'accountName' => 255,
        'jobTitle' => 128,
        'city' => 40,
        'stateOrRegion' => 80,
        'country' => 80,
        'location' => 80,
        'contactId' => 18,
        'requestedField' => 40
    };

    // Search limits that keep a single request bounded.
    public static final Integer MAX_NAME_WORDS = 5;
    public static final Integer MIN_PHONE_DIGITS = 7;
    public static final Integer MAX_PHONE_DIGITS = 15;

    // Characters a phone number may contain before it is reduced to digits.
    private static final Pattern PHONE_CHARACTERS = Pattern.compile('^[0-9+()\\-. /]+$');

    // Whitelist of requestable fields. Keys are lower-case letters only,
    // so "Phone number", "phone_number" and "PHONE NUMBER" all resolve.
    private static final Map<String, String> REQUESTED_FIELD_ALIASES = new Map<String, String>{
        'name' => 'Name',
        'fullname' => 'Name',
        'account' => 'Account',
        'accountname' => 'Account',
        'company' => 'Account',
        'title' => 'Title',
        'jobtitle' => 'Title',
        'email' => 'Email',
        'emailaddress' => 'Email',
        'phone' => 'Phone',
        'phonenumber' => 'Phone',
        'mailingaddress' => 'MailingAddress',
        'address' => 'MailingAddress'
    };

    // ---------------------------------------------------------------
    // Raw inputs (names match the action contract in technical-design.md)
    // ---------------------------------------------------------------
    public String name;
    public String email;
    public String phone;
    public String accountName;
    public String jobTitle;
    public String city;
    public String stateOrRegion;
    public String country;
    public String location;
    public String contactId;
    public String requestedField;
    public Boolean showRemaining;

    // ---------------------------------------------------------------
    // Normalised values, set by validate()
    // ---------------------------------------------------------------
    public Boolean isValid { get; private set; }
    public String validationMessage { get; private set; }
    public List<String> nameWords { get; private set; }
    public String normalisedName { get; private set; }
    public Boolean isExactEmail { get; private set; }
    public String phoneDigits { get; private set; }
    public String phoneCoreDigits { get; private set; }
    public Id contactRecordId { get; private set; }
    public String requestedFieldKey { get; private set; }

    /*****************************************************************
    Purpose:   Validate and normalise every input in place.
    Returns:   true when the criteria can be searched. When false,
               validationMessage holds a user-safe explanation.
    *****************************************************************/
    public Boolean validate() {
        System.debug(LoggingLevel.FINE, 'Entering CRA_ContactSearchCriteria.validate');
        isValid = false;
        nameWords = new List<String>();
        isExactEmail = false;

        // Clean every text input first; a rejected length stops here.
        if (!cleanAllInputs()) {
            return false;
        }

        // Each specialised check returns false and sets the message on failure.
        Boolean passed = validateName() && validateEmail() && validatePhone()
            && validateContactId() && validateRequestedField();

        if (passed && !hasAnyFilter()) {
            validationMessage = 'Please tell me something to search by, such as a name, '
                + 'email, phone number, Account, job title or location.';
            passed = false;
        }

        isValid = passed;
        System.debug(LoggingLevel.FINE, 'Exiting CRA_ContactSearchCriteria.validate: ' + isValid);
        return isValid;
    }

    /*****************************************************************
    Purpose:   True when at least one search filter is supplied.
               requestedField and showRemaining are not filters.
    *****************************************************************/
    public Boolean hasAnyFilter() {
        return String.isNotBlank(name) || String.isNotBlank(email) || String.isNotBlank(phone)
            || String.isNotBlank(accountName) || String.isNotBlank(jobTitle)
            || String.isNotBlank(city) || String.isNotBlank(stateOrRegion)
            || String.isNotBlank(country) || String.isNotBlank(location)
            || String.isNotBlank(contactId);
    }

    /*****************************************************************
    Purpose:   True when the user asked for the rest of a 6-10 list.
    *****************************************************************/
    public Boolean wantsRemaining() {
        return showRemaining == true;
    }

    /*****************************************************************
    Purpose:   Clean every text input and enforce the length limits.
    Returns:   false when any value is longer than its limit.
    *****************************************************************/
    private Boolean cleanAllInputs() {
        name = clean(name);
        email = clean(email);
        phone = clean(phone);
        accountName = clean(accountName);
        jobTitle = clean(jobTitle);
        city = clean(city);
        stateOrRegion = clean(stateOrRegion);
        country = clean(country);
        location = clean(location);
        contactId = clean(contactId);
        requestedField = clean(requestedField);

        Map<String, String> valuesByInput = new Map<String, String>{
            'name' => name, 'email' => email, 'phone' => phone,
            'accountName' => accountName, 'jobTitle' => jobTitle, 'city' => city,
            'stateOrRegion' => stateOrRegion, 'country' => country,
            'location' => location, 'contactId' => contactId,
            'requestedField' => requestedField
        };

        for (String inputName : valuesByInput.keySet()) {
            String value = valuesByInput.get(inputName);
            if (value != null && value.length() > MAX_LENGTH.get(inputName)) {
                validationMessage = 'One of the search values is too long. '
                    + 'Please shorten it and try again.';
                return false;
            }
        }
        return true;
    }

    /*****************************************************************
    Purpose:   Split the name into words; each word later matches the
               start of the first or last name.
    *****************************************************************/
    private Boolean validateName() {
        if (String.isBlank(name)) {
            return true;
        }
        nameWords = name.split(' ');
        if (nameWords.size() > MAX_NAME_WORDS) {
            validationMessage = 'That name has too many words. Please use the first and last name.';
            return false;
        }
        normalisedName = name;
        return true;
    }

    /*****************************************************************
    Purpose:   An email containing "@" is matched exactly; anything
               else is a partial (contains) match.
    *****************************************************************/
    private Boolean validateEmail() {
        isExactEmail = String.isNotBlank(email) && email.contains('@');
        return true;
    }

    /*****************************************************************
    Purpose:   Reduce the phone number to digits and check its size.
               phoneCoreDigits drops leading zeros so a national number
               such as 0191 4956203 can match +44 191 4956203.
    *****************************************************************/
    private Boolean validatePhone() {
        if (String.isBlank(phone)) {
            return true;
        }
        String digits = phone.replaceAll('[^0-9]', '');
        Boolean shapeOk = PHONE_CHARACTERS.matcher(phone).matches();
        if (!shapeOk || digits.length() < MIN_PHONE_DIGITS || digits.length() > MAX_PHONE_DIGITS) {
            validationMessage = 'That does not look like a phone number. '
                + 'Please give the number with its area code.';
            return false;
        }
        String core = digits.replaceFirst('^0+', '');
        if (core.length() < MIN_PHONE_DIGITS) {
            validationMessage = 'That does not look like a phone number. '
                + 'Please give the number with its area code.';
            return false;
        }
        phoneDigits = digits;
        phoneCoreDigits = core;
        return true;
    }

    /*****************************************************************
    Purpose:   contactId must be a well-formed Id of a Contact.
    *****************************************************************/
    private Boolean validateContactId() {
        if (String.isBlank(contactId)) {
            return true;
        }
        try {
            Id parsedId = Id.valueOf(contactId);
            if (parsedId.getSObjectType() == Contact.SObjectType) {
                contactRecordId = parsedId;
                return true;
            }
        } catch (StringException invalidId) {
            System.debug(LoggingLevel.FINE, 'contactId is not a valid Id');
        }
        validationMessage = 'I could not tell which Contact you mean. Please search for them again.';
        return false;
    }

    /*****************************************************************
    Purpose:   Map requestedField onto the whitelist of answerable fields.
    *****************************************************************/
    private Boolean validateRequestedField() {
        if (String.isBlank(requestedField)) {
            return true;
        }
        String aliasKey = requestedField.toLowerCase().replaceAll('[^a-z]', '');
        requestedFieldKey = REQUESTED_FIELD_ALIASES.get(aliasKey);
        if (requestedFieldKey == null) {
            validationMessage = 'I can tell you a Contact\'s name, Account, title, email, '
                + 'phone or mailing address. Which one would you like?';
            return false;
        }
        return true;
    }

    /*****************************************************************
    Purpose:   Remove control characters, collapse whitespace and trim.
    Returns:   null for blank input.
    *****************************************************************/
    @TestVisible
    private static String clean(String value) {
        if (value == null) {
            return null;
        }
        String cleaned = value.replaceAll('\\p{Cntrl}', ' ').replaceAll('\\s+', ' ').trim();
        return String.isBlank(cleaned) ? null : cleaned;
    }
}
