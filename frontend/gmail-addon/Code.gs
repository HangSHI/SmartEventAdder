/**
 * Smart Event Adder - Gmail Add-on
 *
 * This Gmail add-on integrates with the SmartEventAdder API to parse email content
 * and extract event information for creating Google Calendar events.
 *
 * Main Features:
 * - Parse email content using AI (Vertex AI via backend API)
 * - Extract event details (title, date, time, location)
 * - Create Google Calendar events
 * - User-friendly card-based interface
 */

// Backend API Configuration
// Production API endpoint on Google Cloud Run
const API_BASE_URL = 'https://smarteventadder-api-20081880195.us-central1.run.app/api';

// Development/Testing Configuration
const DEV_MODE = false; // Set to true for development testing
const DEV_API_URL = 'http://localhost:8000/api'; // Local development URL

// Get the appropriate API URL based on mode
function getApiBaseUrl() {
  return DEV_MODE ? DEV_API_URL : API_BASE_URL;
}

// API request timeout (in milliseconds)
const API_TIMEOUT = 30000; // 30 seconds

/**
 * Main trigger function called by Gmail when an email is opened
 * This is the entry point specified in appsscript.json
 *
 * @param {Object} e - Gmail event object containing email context
 * @return {Card[]} Array of cards to display in the add-on sidebar
 */
function buildCardForEmail(e) {
  console.log('buildCardForEmail triggered');
  console.log('Initial event object:', JSON.stringify(e, null, 2));

  try {
    // Get email information from the event object
    const messageId = e.gmail.messageId;
    const accessToken = e.gmail.accessToken;

    console.log('Extracted messageId:', messageId);
    console.log('Has accessToken:', !!accessToken);

    // Create the main interface card
    const card = createMainCard(messageId, accessToken);

    return [card];
  } catch (error) {
    console.error('Error in buildCardForEmail:', error);
    return [createErrorCard('Failed to load add-on: ' + error.message)];
  }
}

/**
 * Creates the main interface card for the Gmail add-on
 *
 * @param {string} messageId - Gmail message ID
 * @param {string} accessToken - Gmail access token
 * @return {Card} The main interface card
 */
function createMainCard(messageId, accessToken) {
  const card = CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader()
      .setTitle('Smart Event Adder')
      .setSubtitle('AI-powered event extraction')
      .setImageUrl('https://hangshi.github.io/SmartEventAdder/image/logo.png'))
    .addSection(createEmailInfoSection(messageId))
    .addSection(createActionSection(messageId))
    .build();

  return card;
}

/**
 * Creates a section showing email information
 *
 * @param {string} messageId - Gmail message ID
 * @return {CardSection} Email information section
 */
function createEmailInfoSection(messageId) {
  return CardService.newCardSection()
    .setHeader('Email Information')
    .addWidget(CardService.newKeyValue()
      .setTopLabel('Message ID')
      .setContent(messageId)
      .setMultiline(true))
    .addWidget(CardService.newTextParagraph()
      .setText('Click "Parse Event" to extract event details from this email using AI.'));
}

/**
 * Creates the action section with buttons
 *
 * @param {string} messageId - Gmail message ID
 * @return {CardSection} Action section with buttons
 */
function createActionSection(messageId) {
  const parseAction = CardService.newAction()
    .setFunctionName('parseEmailEvent')
    .setParameters({'messageId': messageId});

  const parseButton = CardService.newTextButton()
    .setText('Parse Event')
    .setOnClickAction(parseAction)
    .setTextButtonStyle(CardService.TextButtonStyle.FILLED);

  return CardService.newCardSection()
    .setHeader('Actions')
    .addWidget(parseButton);
}

/**
 * Handles the "Parse Event" button click
 * Fetches email content and calls the backend API to parse event details
 *
 * @param {Object} e - Action event object
 * @return {ActionResponse} Response to update the card
 */
function parseEmailEvent(e) {
  console.log('parseEmailEvent called');
  console.log('Event object:', JSON.stringify(e, null, 2));

  // Declare messageId outside try block so it's accessible in catch
  let messageId = null;

  try {
    // Try multiple ways to get messageId
    if (e && e.parameters && e.parameters.messageId) {
      messageId = e.parameters.messageId;
    } else if (e && e.gmail && e.gmail.messageId) {
      messageId = e.gmail.messageId;
    } else if (e && e.messageId) {
      messageId = e.messageId;
    }

    console.log('Extracted messageId:', messageId);

    if (!messageId) {
      throw new Error('Could not extract messageId from event. Event structure: ' + JSON.stringify(e));
    }

    // Show loading state
    const loadingCard = createLoadingCard();

    // Fetch email content using Gmail API
    const emailData = fetchEmailContent(messageId);

    if (!emailData) {
      throw new Error('Failed to fetch email content');
    }

    console.log('Email data extracted:', {
      subject: emailData.subject,
      bodyLength: emailData.plainTextBody ? emailData.plainTextBody.length : 0
    });

    // Call backend API to parse event details with authentication
    const eventData = callParseEmailAPI(emailData);

    if (!eventData || !eventData.success) {
      const errorMessage = eventData ? (eventData.error || eventData.detail || 'Unknown error') : 'Failed to parse email';
      throw new Error(errorMessage);
    }

    console.log('Event data parsed successfully:', eventData.event_data);

    // Create card showing parsed event details
    const resultCard = createEventDetailsCard(eventData.event_data, messageId);

    return CardService.newActionResponseBuilder()
      .setNavigation(CardService.newNavigation().updateCard(resultCard))
      .build();

  } catch (error) {
    console.error('Error in parseEmailEvent:', error);
    const errorCard = createErrorCard('Failed to parse event: ' + error.message, messageId);

    return CardService.newActionResponseBuilder()
      .setNavigation(CardService.newNavigation().updateCard(errorCard))
      .build();
  }
}

/**
 * Fetches email content using Gmail API and extracts subject and plainTextBody
 *
 * @param {string} messageId - Gmail message ID
 * @return {Object} Object containing subject and plainTextBody
 */
function fetchEmailContent(messageId) {
  try {
    // Get the current message using Gmail API
    const message = Gmail.Users.Messages.get('me', messageId);

    // Extract headers
    const headers = message.headers || message.payload.headers;
    const subjectHeader = headers.find(header => header.name === 'Subject');
    const fromHeader = headers.find(header => header.name === 'From');
    const dateHeader = headers.find(header => header.name === 'Date');

    // Extract subject
    const subject = subjectHeader ? subjectHeader.value : 'No Subject';

    // Extract plain text body
    const plainTextBody = extractMessageBody(message.payload);

    // Return structured data for API communication
    return {
      subject: subject,
      plainTextBody: plainTextBody,
      from: fromHeader ? fromHeader.value : 'Unknown',
      date: dateHeader ? dateHeader.value : 'Unknown',
      // Also maintain formatted content for backward compatibility
      formattedContent: `Subject: ${subject}\nFrom: ${fromHeader ? fromHeader.value : 'Unknown'}\nDate: ${dateHeader ? dateHeader.value : 'Unknown'}\n\n${plainTextBody}`
    };

  } catch (error) {
    console.error('Error fetching email content:', error);
    throw new Error('Failed to fetch email content: ' + error.message);
  }
}

/**
 * Extracts message body from Gmail API payload
 *
 * @param {Object} payload - Gmail message payload
 * @return {string} Extracted message body
 */
function extractMessageBody(payload) {
  let body = '';

  console.log('Extracting message body from payload:', JSON.stringify(payload, null, 2));

  try {
    if (payload.body && payload.body.data) {
      // Simple message body
      console.log('Found simple message body, data length:', payload.body.data.length);
      body = decodeBase64Content(payload.body.data, 'simple message body');
    } else if (payload.parts) {
      // Multipart message
      console.log('Found multipart message with', payload.parts.length, 'parts');
      for (let i = 0; i < payload.parts.length; i++) {
        const part = payload.parts[i];
        console.log(`Part ${i}: mimeType=${part.mimeType}, hasData=${!!(part.body && part.body.data)}`);

        if (part.mimeType === 'text/plain' && part.body && part.body.data) {
          const partContent = decodeBase64Content(part.body.data, `text/plain part ${i}`);
          if (partContent) {
            body += partContent + '\n';
          }
        } else if (part.mimeType === 'text/html' && part.body && part.body.data && !body) {
          // If no plain text found, try HTML as fallback
          const htmlContent = decodeBase64Content(part.body.data, `text/html part ${i}`);
          if (htmlContent) {
            body += htmlContent + '\n';
          }
        } else if (part.parts) {
          // Nested multipart (recursive handling)
          console.log(`Part ${i} has nested parts, recursing...`);
          const nestedContent = extractMessageBody(part);
          if (nestedContent && nestedContent !== 'Email content could not be extracted') {
            body += nestedContent + '\n';
          }
        }
      }
    } else {
      console.log('No body data or parts found in payload');
      body = 'No readable content found in email';
    }

    // Clean up the extracted body
    if (body && body !== 'No readable content found in email') {
      // Remove HTML tags if present
      body = body.replace(/<[^>]*>/g, '');

      // Clean up extra whitespace and newlines
      body = body.replace(/\s+/g, ' ').trim();

      // Remove common email artifacts
      body = body.replace(/=\r?\n/g, ''); // Remove line breaks from quoted-printable
      body = body.replace(/\u00A0/g, ' '); // Replace non-breaking spaces
    }

    console.log('Extracted body length:', body.length);
    console.log('Body preview:', body.substring(0, 200));

    return body || 'Email content could not be extracted';

  } catch (error) {
    console.error('Error in extractMessageBody:', error);
    return 'Error extracting email content: ' + error.message;
  }
}

/**
 * Helper function to decode base64 content with comprehensive error handling
 * Handles URL-safe base64 encoding used by Gmail API
 *
 * @param {string} base64Data - Base64 encoded string from Gmail API
 * @param {string} context - Context description for logging
 * @return {string} Decoded content or empty string if decoding fails
 */
function decodeBase64Content(base64Data, context) {
  if (!base64Data) {
    console.log(`No data to decode for ${context}`);
    return '';
  }

  console.log(`Attempting to decode ${context}, data length: ${base64Data.length}`);

  try {
    // Method 1: Convert URL-safe base64 to standard base64 and decode with proper padding
    let standardBase64 = base64Data.replace(/-/g, '+').replace(/_/g, '/');

    // Add padding if necessary
    while (standardBase64.length % 4) {
      standardBase64 += '=';
    }

    console.log(`Converted URL-safe base64 for ${context}, new length: ${standardBase64.length}`);

    try {
      const decodedBytes = Utilities.base64Decode(standardBase64);
      const content = Utilities.newBlob(decodedBytes).getDataAsString('UTF-8');
      console.log(`Successfully decoded ${context} using UTF-8, content length: ${content.length}`);
      return content;
    } catch (utf8Error) {
      console.warn(`UTF-8 decoding failed for ${context}, trying default encoding:`, utf8Error.message);

      // Try without explicit encoding
      const decodedBytes = Utilities.base64Decode(standardBase64);
      const content = Utilities.newBlob(decodedBytes).getDataAsString();
      console.log(`Successfully decoded ${context} using default encoding, content length: ${content.length}`);
      return content;
    }

  } catch (standardError) {
    console.warn(`Standard base64 decode failed for ${context}:`, standardError.message);

    try {
      // Method 2: Try direct decoding of original data
      console.log(`Trying direct decode for ${context}...`);
      const decodedBytes = Utilities.base64Decode(base64Data);
      const content = Utilities.newBlob(decodedBytes).getDataAsString();
      console.log(`Direct decode successful for ${context}, content length: ${content.length}`);
      return content;
    } catch (directError) {
      console.error(`All decoding methods failed for ${context}:`, directError.message);

      try {
        // Method 3: Try decoding as raw string (last resort)
        console.log(`Trying raw string interpretation for ${context}...`);
        const content = Utilities.newBlob(Utilities.base64Decode(base64Data, Utilities.Charset.UTF_8)).getDataAsString();
        console.log(`Raw string decode successful for ${context}, content length: ${content.length}`);
        return content;
      } catch (rawError) {
        console.error(`Raw string decode also failed for ${context}:`, rawError.message);
        return `[Could not decode ${context}: ${rawError.message}]`;
      }
    }
  }
}

/**
 * Generic function to communicate with the backend API
 * Handles authentication, data preparation, and response processing
 *
 * @param {string} endpoint - API endpoint (e.g., '/parse-email')
 * @param {Object} data - Data to send to the backend
 * @return {Object} Parsed response from backend API
 */
function callBackendAPI(endpoint, data) {
  try {
    // Get Google OIDC identity token for authentication
    const identityToken = getIdentityToken();

    // Prepare headers with authentication
    const headers = {
      'Content-Type': 'application/json'
    };

    // Add authorization header if identity token is available
    if (identityToken) {
      headers['Authorization'] = `Bearer ${identityToken}`;
    }

    // Prepare request options
    const options = {
      method: 'POST',
      headers: headers,
      payload: JSON.stringify(data)
    };

    // Add timeout to options
    options.muteHttpExceptions = true; // Don't throw exceptions for HTTP error codes

    // Make the API request
    const fullUrl = getApiBaseUrl() + endpoint;
    console.log(`Making API request to: ${fullUrl}`);
    const response = UrlFetchApp.fetch(fullUrl, options);
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();

    console.log(`API response code: ${responseCode}`);

    // Handle different response codes
    if (responseCode === 200) {
      const result = JSON.parse(responseText);
      console.log('API request successful');
      return result;
    } else if (responseCode === 401) {
      throw new Error('Authentication failed. Please check your permissions.');
    } else if (responseCode === 403) {
      throw new Error('Access forbidden. Please check your authorization.');
    } else if (responseCode >= 500) {
      throw new Error(`Server error (${responseCode}). Please try again later.`);
    } else {
      // Try to parse error response
      try {
        const errorResult = JSON.parse(responseText);
        throw new Error(errorResult.detail || errorResult.error || `API error: ${responseCode}`);
      } catch (parseError) {
        throw new Error(`API error: ${responseCode} - ${responseText}`);
      }
    }

  } catch (error) {
    console.error('Error in callBackendAPI:', error);
    throw error;
  }
}

/**
 * Gets Google OIDC identity token for API authentication
 *
 * @return {string|null} Identity token or null if not available
 */
function getIdentityToken() {
  try {
    // Get the identity token representing the current user
    const token = ScriptApp.getIdentityToken();
    console.log('Identity token obtained successfully');
    return token;
  } catch (error) {
    console.warn('Failed to get identity token:', error);
    // In development or testing, we might continue without authentication
    // In production, this should be handled more strictly
    return null;
  }
}

/**
 * Calls the backend API to parse email content
 * Uses the generic callBackendAPI function with proper authentication
 *
 * @param {Object} emailData - Email data object with subject and plainTextBody
 * @return {Object} Parsed event data from API
 */
function callParseEmailAPI(emailData) {
  try {
    // Prepare data for the backend API
    const payload = {
      email_content: emailData.formattedContent || emailData,
      subject: emailData.subject,
      plain_text_body: emailData.plainTextBody,
      project_id: null, // Will use API default
      location: null    // Will use API default
    };

    console.log('Calling parse-email API with authentication');
    return callBackendAPI('/parse-email', payload);

  } catch (error) {
    console.error('Error calling parse email API:', error);
    throw error;
  }
}

/**
 * Creates a card displaying parsed event details with editable fields
 * Follows Gemini's recommendation for user-editable TextInput widgets
 *
 * @param {Object} eventData - Parsed event data
 * @param {string} messageId - Original message ID
 * @return {Card} Card showing editable event details
 */
function createEventDetailsCard(eventData, messageId) {
  const cardBuilder = CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader()
      .setTitle('Suggested Calendar Event')
      .setSubtitle('Review and edit details before adding to calendar'));

  // Editable event details section
  const detailsSection = CardService.newCardSection()
    .setHeader('Event Details (Editable)');

  // Editable Title/Summary
  const titleInput = CardService.newTextInput()
    .setFieldName('event_title')
    .setTitle('Event Title')
    .setValue(eventData.summary || eventData.title || '')
    .setHint('Enter the event title or meeting name');
  detailsSection.addWidget(titleInput);

  // Editable Date
  const dateInput = CardService.newTextInput()
    .setFieldName('event_date')
    .setTitle('Date')
    .setValue(eventData.date || '')
    .setHint('Format: YYYY-MM-DD or "tomorrow", "next Friday"');
  detailsSection.addWidget(dateInput);

  // Editable Start Time
  const timeInput = CardService.newTextInput()
    .setFieldName('event_time')
    .setTitle('Start Time')
    .setValue(eventData.start_time || '')
    .setHint('Format: HH:MM (24-hour) or "2:30 PM"');
  detailsSection.addWidget(timeInput);

  // Editable End Time (if available)
  if (eventData.end_time) {
    const endTimeInput = CardService.newTextInput()
      .setFieldName('event_end_time')
      .setTitle('End Time (Optional)')
      .setValue(eventData.end_time || '')
      .setHint('Format: HH:MM (24-hour) or "4:00 PM"');
    detailsSection.addWidget(endTimeInput);
  }

  // Editable Location
  const locationInput = CardService.newTextInput()
    .setFieldName('event_location')
    .setTitle('Location (Optional)')
    .setValue(eventData.location || '')
    .setHint('Meeting room, address, or video conference link')
    .setMultiline(false);
  detailsSection.addWidget(locationInput);

  // Editable Description
  const descriptionInput = CardService.newTextInput()
    .setFieldName('event_description')
    .setTitle('Description (Optional)')
    .setValue(eventData.description || '')
    .setHint('Additional details about the event')
    .setMultiline(true);
  detailsSection.addWidget(descriptionInput);

  cardBuilder.addSection(detailsSection);

  // Instructions section
  const instructionsSection = CardService.newCardSection()
    .addWidget(CardService.newTextParagraph()
      .setText('📝 Review the extracted information above. You can edit any field before adding the event to your calendar.'));
  cardBuilder.addSection(instructionsSection);

  // Action buttons section
  const actionSection = CardService.newCardSection()
    .setHeader('Actions');

  const createEventAction = CardService.newAction()
    .setFunctionName('createCalendarEventFromForm')
    .setParameters({
      'originalEventData': JSON.stringify(eventData),
      'messageId': messageId
    });

  const createEventButton = CardService.newTextButton()
    .setText('📅 Add to Calendar')
    .setOnClickAction(createEventAction)
    .setTextButtonStyle(CardService.TextButtonStyle.FILLED);

  const backAction = CardService.newAction()
    .setFunctionName('showMainCard')
    .setParameters({'messageId': messageId});

  const backButton = CardService.newTextButton()
    .setText('← Back')
    .setOnClickAction(backAction);

  actionSection.addWidget(createEventButton);
  actionSection.addWidget(backButton);
  cardBuilder.addSection(actionSection);

  return cardBuilder.build();
}

/**
 * Creates a calendar event directly using Google Calendar API
 * No longer uses backend - creates events directly in the add-on
 *
 * @param {Object} e - Action event object with form inputs
 * @return {ActionResponse} Response to update the card
 */
function createCalendarEventFromForm(e) {
  console.log('createCalendarEventFromForm called');

  try {
    const messageId = e.parameters.messageId;
    const originalEventData = JSON.parse(e.parameters.originalEventData);

    // Extract user-edited data from form inputs
    const formInputs = e.formInputs || {};

    // Build event data from user inputs (fallback to original if empty)
    const finalEventData = {
      summary: getFormValue(formInputs, 'event_title') || originalEventData.summary || originalEventData.title,
      date: getFormValue(formInputs, 'event_date') || originalEventData.date,
      start_time: getFormValue(formInputs, 'event_time') || originalEventData.start_time,
      end_time: getFormValue(formInputs, 'event_end_time') || originalEventData.end_time,
      location: getFormValue(formInputs, 'event_location') || originalEventData.location,
      description: getFormValue(formInputs, 'event_description') || originalEventData.description
    };

    console.log('Final event data after user edits:', finalEventData);

    // Validate required fields
    if (!finalEventData.summary || !finalEventData.date) {
      throw new Error('Event title and date are required. Please fill in these fields.');
    }

    // Create calendar event directly using Google Calendar API
    const result = createGoogleCalendarEvent(finalEventData);

    if (!result || !result.success) {
      throw new Error(result ? result.error : 'Failed to create calendar event');
    }

    console.log('Calendar event created successfully:', result);

    // Show enhanced success card with calendar link
    const successCard = createEnhancedSuccessCard(finalEventData, result, messageId);

    return CardService.newActionResponseBuilder()
      .setNavigation(CardService.newNavigation().updateCard(successCard))
      .build();

  } catch (error) {
    console.error('Error in createCalendarEventFromForm:', error);
    const errorCard = createErrorCard('Failed to create calendar event: ' + error.message, e.parameters.messageId);

    return CardService.newActionResponseBuilder()
      .setNavigation(CardService.newNavigation().updateCard(errorCard))
      .build();
  }
}

/**
 * Helper function to extract form input values safely
 *
 * @param {Object} formInputs - Form inputs object
 * @param {string} fieldName - Field name to extract
 * @return {string} Field value or empty string
 */
function getFormValue(formInputs, fieldName) {
  if (formInputs && formInputs[fieldName] && formInputs[fieldName].length > 0) {
    return formInputs[fieldName][0].trim();
  }
  return '';
}

/**
 * Legacy function - kept for backward compatibility
 * Redirects to new form-based function
 *
 * @param {Object} e - Action event object
 * @return {ActionResponse} Response to update the card
 */
function createCalendarEvent(e) {
  console.log('createCalendarEvent called (legacy)');

  try {
    const eventData = JSON.parse(e.parameters.eventData);
    const messageId = e.parameters.messageId;

    // Call backend API directly with original data
    const result = callCreateEventAPI(eventData);

    if (!result || !result.success) {
      throw new Error(result ? result.error : 'Failed to create calendar event');
    }

    // Show enhanced success card
    const successCard = createEnhancedSuccessCard(eventData, result, messageId);

    return CardService.newActionResponseBuilder()
      .setNavigation(CardService.newNavigation().updateCard(successCard))
      .build();

  } catch (error) {
    console.error('Error in createCalendarEvent:', error);
    const errorCard = createErrorCard('Failed to create calendar event: ' + error.message);

    return CardService.newActionResponseBuilder()
      .setNavigation(CardService.newNavigation().updateCard(errorCard))
      .build();
  }
}

/**
 * Get user's timezone dynamically from their Google account
 * Provides multi-timezone support for global users
 *
 * @return {string} User's timezone (e.g., 'Asia/Tokyo', 'America/New_York')
 */
function getUserTimezone() {
  try {
    // Method 1: From user's Google Calendar settings (most accurate)
    const userTimeZone = CalendarApp.getDefaultCalendar().getTimeZone();
    console.log('User timezone from Calendar:', userTimeZone);
    return userTimeZone;
  } catch (calendarError) {
    console.warn('Failed to get calendar timezone:', calendarError.message);

    try {
      // Method 2: From Apps Script session settings
      const sessionTimeZone = Session.getScriptTimeZone();
      console.log('User timezone from Session:', sessionTimeZone);
      return sessionTimeZone;
    } catch (sessionError) {
      console.warn('Failed to get session timezone:', sessionError.message);

      // Method 3: Default fallback based on user's Google account locale
      try {
        const userLocale = Session.getActiveUserLocale();
        console.log('User locale:', userLocale);

        // Simple locale to timezone mapping for common cases
        const localeTimezoneMap = {
          'ja': 'Asia/Tokyo',         // Japan
          'en_US': 'America/New_York', // US East
          'en_GB': 'Europe/London',    // UK
          'de': 'Europe/Berlin',       // Germany
          'fr': 'Europe/Paris',        // France
          'zh_CN': 'Asia/Shanghai',    // China
          'ko': 'Asia/Seoul',          // Korea
          'en_AU': 'Australia/Sydney'  // Australia
        };

        const mappedTimezone = localeTimezoneMap[userLocale] || localeTimezoneMap[userLocale.split('_')[0]];
        if (mappedTimezone) {
          console.log('Mapped timezone from locale:', mappedTimezone);
          return mappedTimezone;
        }
      } catch (localeError) {
        console.warn('Failed to get user locale:', localeError.message);
      }

      // Final fallback: UTC
      console.warn('Using UTC as final fallback timezone');
      return 'UTC';
    }
  }
}

/**
 * Creates a calendar event directly using Google Calendar API
 * Now with dynamic timezone support for global users
 *
 * @param {Object} eventData - Event data to create
 * @return {Object} Result with success status and event details
 */
function createGoogleCalendarEvent(eventData) {
  try {
    console.log('Creating calendar event directly with Google Calendar API');
    console.log('Event data:', eventData);

    // Get user's timezone dynamically
    const userTimeZone = getUserTimezone();
    console.log('Creating event in user timezone:', userTimeZone);

    // Parse and validate date/time
    const eventDate = eventData.date; // YYYY-MM-DD format
    const startTime = eventData.start_time || '09:00'; // Default to 9 AM if no time
    const endTime = eventData.end_time;

    // Create start datetime
    let startDateTime;
    let endDateTime;

    if (startTime.includes(':')) {
      // Has specific time - create in user's timezone context
      const dateTimeString = `${eventDate}T${startTime}:00`;
      console.log('Creating date from:', dateTimeString, 'in timezone:', userTimeZone);

      // Create date object (interprets as local time, which is what we want)
      startDateTime = new Date(dateTimeString);

      // Check if the date is invalid
      if (isNaN(startDateTime.getTime())) {
        throw new Error(`Invalid date/time: ${dateTimeString}`);
      }

      if (endTime && endTime.includes(':')) {
        endDateTime = new Date(`${eventDate}T${endTime}:00`);
      } else {
        // Default to 1 hour duration
        endDateTime = new Date(startDateTime.getTime() + 60 * 60 * 1000);
      }

      console.log('Parsed start time:', startDateTime.toISOString(), 'for timezone:', userTimeZone);
      console.log('Parsed end time:', endDateTime.toISOString(), 'for timezone:', userTimeZone);
    } else {
      // All day event
      startDateTime = new Date(eventDate);
      endDateTime = new Date(eventDate);
      endDateTime.setDate(endDateTime.getDate() + 1);
    }

    // Create calendar event object with user's timezone
    const calendarEvent = {
      summary: eventData.summary || 'New Event',
      description: eventData.description || '',
      location: eventData.location || '',
      start: {
        dateTime: startDateTime.toISOString(),
        timeZone: userTimeZone  // Dynamic timezone based on user!
      },
      end: {
        dateTime: endDateTime.toISOString(),
        timeZone: userTimeZone  // Dynamic timezone based on user!
      }
    };

    console.log('Calendar event object:', calendarEvent);

    // Try Calendar API first, fallback to CalendarApp
    let createdEvent;
    try {
      // Method 1: Advanced Calendar API
      createdEvent = Calendar.Events.insert(calendarEvent, 'primary');
      console.log('Event created with Calendar API:', createdEvent.id);

      return {
        success: true,
        event_id: createdEvent.id,
        event_url: createdEvent.htmlLink,
        calendar_link: createdEvent.htmlLink,
        message: 'Calendar event created successfully'
      };
    } catch (apiError) {
      console.warn('Calendar API failed, trying CalendarApp:', apiError);

      // Method 2: CalendarApp fallback
      const calendar = CalendarApp.getDefaultCalendar();
      const appEvent = calendar.createEvent(
        eventData.summary || 'New Event',
        startDateTime,
        endDateTime,
        {
          description: eventData.description || '',
          location: eventData.location || ''
        }
      );

      console.log('Event created with CalendarApp:', appEvent.getId());

      return {
        success: true,
        event_id: appEvent.getId(),
        event_url: 'https://calendar.google.com/calendar',
        calendar_link: 'https://calendar.google.com/calendar',
        message: 'Calendar event created successfully'
      };
    }

  } catch (error) {
    console.error('Error creating calendar event:', error);
    return {
      success: false,
      error: error.message || 'Failed to create calendar event',
      message: 'Calendar event creation failed'
    };
  }
}

/**
 * Shows the main card (back navigation)
 *
 * @param {Object} e - Action event object
 * @return {ActionResponse} Response to show main card
 */
function showMainCard(e) {
  const messageId = e.parameters.messageId;
  const mainCard = createMainCard(messageId, null);

  return CardService.newActionResponseBuilder()
    .setNavigation(CardService.newNavigation().updateCard(mainCard))
    .build();
}

/**
 * Creates a loading card
 *
 * @return {Card} Loading card
 */
function createLoadingCard() {
  return CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader()
      .setTitle('Processing...')
      .setSubtitle('Parsing email content'))
    .addSection(CardService.newCardSection()
      .addWidget(CardService.newTextParagraph()
        .setText('🤖 AI is analyzing your email content to extract event details. Please wait...')))
    .build();
}

/**
 * Creates an enhanced success card with calendar link
 * Implements Gemini's recommendation for final confirmation with OpenLink
 *
 * @param {Object} eventData - Created event data
 * @param {Object} apiResult - Result from create event API
 * @param {string} messageId - Original message ID
 * @return {Card} Enhanced success card
 */
function createEnhancedSuccessCard(eventData, apiResult, messageId) {
  const cardBuilder = CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader()
      .setTitle('✅ Event Created!')
      .setSubtitle('Successfully added to your calendar'));

  // Success message section
  const successSection = CardService.newCardSection()
    .addWidget(CardService.newTextParagraph()
      .setText('🎉 Your calendar event has been successfully created and added to Google Calendar!'));

  // Event details confirmation
  successSection.addWidget(CardService.newKeyValue()
    .setTopLabel('📅 Event Title')
    .setContent(eventData.summary || 'Untitled Event'));

  if (eventData.date && eventData.start_time) {
    successSection.addWidget(CardService.newKeyValue()
      .setTopLabel('🕐 When')
      .setContent(`${eventData.date} at ${eventData.start_time}`));
  }

  if (eventData.location) {
    successSection.addWidget(CardService.newKeyValue()
      .setTopLabel('📍 Where')
      .setContent(eventData.location)
      .setMultiline(true));
  }

  cardBuilder.addSection(successSection);

  // Calendar link section (if provided by API)
  if (apiResult && (apiResult.calendar_link || apiResult.event_url || apiResult.calendar_result)) {
    const linkSection = CardService.newCardSection()
      .setHeader('Quick Access');

    // Extract calendar URL from API result
    const calendarUrl = apiResult.calendar_link ||
                       apiResult.event_url ||
                       generateCalendarUrl(eventData);

    if (calendarUrl) {
      const openCalendarAction = CardService.newOpenLink()
        .setUrl(calendarUrl)
        .setOpenAs(CardService.OpenAs.FULL_SIZE);

      const openCalendarButton = CardService.newTextButton()
        .setText('🗓️ View in Google Calendar')
        .setOpenLink(openCalendarAction)
        .setTextButtonStyle(CardService.TextButtonStyle.FILLED);

      linkSection.addWidget(openCalendarButton);
      cardBuilder.addSection(linkSection);
    }
  }

  // Action buttons section
  const actionSection = CardService.newCardSection();

  // "Add Another Event" button
  const addAnotherAction = CardService.newAction()
    .setFunctionName('showMainCard')
    .setParameters({'messageId': messageId});

  const addAnotherButton = CardService.newTextButton()
    .setText('➕ Add Another Event')
    .setOnClickAction(addAnotherAction);

  // "Done" button
  const doneAction = CardService.newAction()
    .setFunctionName('showMainCard')
    .setParameters({'messageId': messageId});

  const doneButton = CardService.newTextButton()
    .setText('✅ Done')
    .setOnClickAction(doneAction)
    .setTextButtonStyle(CardService.TextButtonStyle.FILLED);

  actionSection.addWidget(addAnotherButton);
  actionSection.addWidget(doneButton);
  cardBuilder.addSection(actionSection);

  return cardBuilder.build();
}

/**
 * Creates a processing card to show during event creation
 *
 * @param {string} message - Processing message
 * @return {Card} Processing card
 */
function createProcessingCard(message) {
  return CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader()
      .setTitle('Processing...')
      .setSubtitle('Please wait'))
    .addSection(CardService.newCardSection()
      .addWidget(CardService.newTextParagraph()
        .setText('⏳ ' + (message || 'Creating your calendar event. This may take a few moments...'))))
    .build();
}

/**
 * Legacy success card function - kept for compatibility
 *
 * @param {Object} eventData - Created event data
 * @param {string} messageId - Original message ID
 * @return {Card} Success card
 */
function createSuccessCard(eventData, messageId) {
  // Redirect to enhanced version
  return createEnhancedSuccessCard(eventData, null, messageId);
}

/**
 * Generate Google Calendar URL for event
 * Fallback if backend doesn't provide direct link
 *
 * @param {Object} eventData - Event data
 * @return {string} Google Calendar URL
 */
function generateCalendarUrl(eventData) {
  try {
    // Generate a link to Google Calendar with the event details
    // This is a fallback if the backend doesn't provide a direct event link
    const baseUrl = 'https://calendar.google.com/calendar/render';
    const params = {
      action: 'TEMPLATE',
      text: eventData.summary || 'Event',
      dates: formatDateForCalendarUrl(eventData.date, eventData.start_time, eventData.end_time),
      details: eventData.description || '',
      location: eventData.location || ''
    };

    const queryString = Object.keys(params)
      .filter(key => params[key])
      .map(key => `${key}=${encodeURIComponent(params[key])}`)
      .join('&');

    return `${baseUrl}?${queryString}`;

  } catch (error) {
    console.error('Error generating calendar URL:', error);
    return 'https://calendar.google.com/calendar'; // Fallback to main calendar
  }
}

/**
 * Format date and time for Google Calendar URL
 *
 * @param {string} date - Event date
 * @param {string} startTime - Start time
 * @param {string} endTime - End time
 * @return {string} Formatted date string for calendar URL
 */
function formatDateForCalendarUrl(date, startTime, endTime) {
  try {
    // This is a simplified implementation
    // In production, you'd want more robust date parsing
    const eventDate = new Date(date + ' ' + (startTime || '00:00'));
    const endDate = endTime ? new Date(date + ' ' + endTime) : new Date(eventDate.getTime() + 60 * 60 * 1000); // +1 hour default

    const formatDateTime = (dt) => {
      return dt.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
    };

    return formatDateTime(eventDate) + '/' + formatDateTime(endDate);

  } catch (error) {
    console.error('Error formatting date for calendar URL:', error);
    return ''; // Return empty string if formatting fails
  }
}

/**
 * Creates an error card with improved error handling and user guidance
 *
 * @param {string} errorMessage - Error message to display
 * @param {string} messageId - Optional message ID for retry functionality
 * @return {Card} Error card
 */
function createErrorCard(errorMessage, messageId) {
  const cardBuilder = CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader()
      .setTitle('Error')
      .setSubtitle('Something went wrong'));

  const errorSection = CardService.newCardSection()
    .addWidget(CardService.newTextParagraph()
      .setText('❌ ' + errorMessage));

  // Add specific guidance based on error type
  if (errorMessage.includes('Authentication') || errorMessage.includes('401')) {
    errorSection.addWidget(CardService.newTextParagraph()
      .setText('🔑 Please check your Google account permissions and try again.'));
  } else if (errorMessage.includes('Network') || errorMessage.includes('fetch')) {
    errorSection.addWidget(CardService.newTextParagraph()
      .setText('🌐 Network error. Please check your internet connection and try again.'));
  } else if (errorMessage.includes('Server') || errorMessage.includes('500')) {
    errorSection.addWidget(CardService.newTextParagraph()
      .setText('🔧 Server error. Our backend service may be temporarily unavailable.'));
  } else {
    errorSection.addWidget(CardService.newTextParagraph()
      .setText('Please try again or contact support if the problem persists.'));
  }

  cardBuilder.addSection(errorSection);

  // Add retry button if messageId is provided
  if (messageId) {
    const actionSection = CardService.newCardSection();

    const retryAction = CardService.newAction()
      .setFunctionName('parseEmailEvent')
      .setParameters({'messageId': messageId});

    const retryButton = CardService.newTextButton()
      .setText('Retry')
      .setOnClickAction(retryAction);

    const backAction = CardService.newAction()
      .setFunctionName('showMainCard')
      .setParameters({'messageId': messageId});

    const backButton = CardService.newTextButton()
      .setText('Back')
      .setOnClickAction(backAction);

    actionSection.addWidget(retryButton);
    actionSection.addWidget(backButton);
    cardBuilder.addSection(actionSection);
  }

  return cardBuilder.build();
}

/**
 * Enhanced API health check function
 * Tests backend connectivity and authentication
 *
 * @return {Object} Health check result
 */
function testBackendConnection() {
  try {
    console.log('Testing backend API connection...');

    // Test basic connectivity with health endpoint
    const result = callBackendAPI('/health', {});

    console.log('Backend health check result:', result);
    return {
      success: true,
      status: result.status || 'unknown',
      message: 'Backend API is accessible and healthy'
    };

  } catch (error) {
    console.error('Backend connection test failed:', error);
    return {
      success: false,
      error: error.message || 'Unknown error',
      message: 'Failed to connect to backend API'
    };
  }
}

/**
 * Test function for development - can be called manually
 * Tests the complete workflow with sample data
 */
function testCompleteWorkflow() {
  try {
    console.log('Testing complete workflow...');

    // Test data
    const sampleEmailData = {
      subject: 'Team Meeting Tomorrow',
      plainTextBody: 'Hi everyone, let\'s meet tomorrow at 2:30 PM in conference room A for our weekly team meeting. We\'ll discuss the project updates and next steps.',
      formattedContent: 'Subject: Team Meeting Tomorrow\nFrom: test@example.com\nDate: 2024-01-01\n\nHi everyone, let\'s meet tomorrow at 2:30 PM in conference room A for our weekly team meeting. We\'ll discuss the project updates and next steps.'
    };

    // Test API communication
    console.log('Step 1: Testing email parsing...');
    const parseResult = callParseEmailAPI(sampleEmailData);
    console.log('Parse result:', parseResult);

    if (parseResult && parseResult.success && parseResult.event_data) {
      console.log('Step 2: Testing calendar event creation...');
      const createResult = callCreateEventAPI(parseResult.event_data);
      console.log('Create result:', createResult);

      return {
        success: true,
        message: 'Complete workflow test successful',
        parseResult: parseResult,
        createResult: createResult
      };
    } else {
      throw new Error('Email parsing failed');
    }

  } catch (error) {
    console.error('Complete workflow test failed:', error);
    return {
      success: false,
      error: error.message,
      message: 'Complete workflow test failed'
    };
  }
}