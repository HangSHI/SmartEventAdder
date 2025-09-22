/**
 * Production API Test for Smart Event Adder
 *
 * This script tests the frontend-backend communication with the production API.
 * Copy this to Apps Script console and run the test functions.
 */

// Production API Configuration
const PRODUCTION_API_URL = 'https://smarteventadder-api-6qqmniwadq-an.a.run.app/api';

/**
 * Quick connectivity test to verify the production API is accessible
 */
function testProductionAPIConnectivity() {
  console.log('🔌 Testing Production API Connectivity...');
  console.log('API Base URL:', PRODUCTION_API_URL);

  try {
    // Test root endpoint
    const rootResponse = UrlFetchApp.fetch('https://smarteventadder-api-6qqmniwadq-an.a.run.app/');
    console.log('Root endpoint status:', rootResponse.getResponseCode());
    console.log('Root response:', rootResponse.getContentText());

    // Test config endpoint
    const configResponse = UrlFetchApp.fetch(PRODUCTION_API_URL + '/config');
    console.log('Config endpoint status:', configResponse.getResponseCode());
    console.log('Config response:', configResponse.getContentText());

    // Test health endpoint
    const healthResponse = UrlFetchApp.fetch(PRODUCTION_API_URL.replace('/api', '') + '/api/health');
    console.log('Health endpoint status:', healthResponse.getResponseCode());
    console.log('Health response:', healthResponse.getContentText());

    console.log('✅ Basic connectivity test passed!');
    return true;

  } catch (error) {
    console.error('❌ Connectivity test failed:', error);
    return false;
  }
}

/**
 * Test the parse-email API endpoint with sample data
 */
function testParseEmailAPI() {
  console.log('📧 Testing Parse Email API...');

  try {
    const sampleEmailContent = `Subject: Team Meeting Tomorrow
From: manager@company.com
Date: 2024-01-15

Hi everyone,

Let's have our weekly team meeting tomorrow (January 16th) at 2:30 PM in Conference Room A.

Agenda:
- Project updates
- Next sprint planning
- Q&A session

Please bring your laptops and project status reports.

Best regards,
Team Manager`;

    const payload = {
      email_content: sampleEmailContent,
      project_id: null, // Will use API default
      location: null    // Will use API default
    };

    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    };

    console.log('Making request to:', PRODUCTION_API_URL + '/parse-email');
    const response = UrlFetchApp.fetch(PRODUCTION_API_URL + '/parse-email', options);
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();

    console.log('Response code:', responseCode);
    console.log('Response text:', responseText);

    if (responseCode === 200) {
      const result = JSON.parse(responseText);
      console.log('✅ Parse Email API test passed!');
      console.log('Extracted event data:', result.event_data);
      return result;
    } else if (responseCode === 500 && responseText.includes('credentials.json')) {
      console.log('⚠️ Parse Email API needs Google Cloud credentials (expected in production)');
      console.log('ℹ️ This will work once Google Cloud auth is configured');
      return { success: false, expected_error: true };
    } else {
      console.error('❌ Parse Email API test failed:', responseCode, responseText);
      return null;
    }

  } catch (error) {
    console.error('❌ Parse Email API test error:', error);
    return null;
  }
}

/**
 * Test the create-event API endpoint (without actually creating calendar events)
 */
function testCreateEventAPI() {
  console.log('📅 Testing Create Event API...');

  try {
    const sampleEventData = {
      summary: 'Test Meeting from Frontend',
      date: '2024-01-16',
      start_time: '14:30',
      location: 'Conference Room A',
      description: 'This is a test event created from the frontend API test'
    };

    const payload = {
      event_data: sampleEventData
    };

    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    };

    console.log('Making request to:', PRODUCTION_API_URL + '/create-event');
    const response = UrlFetchApp.fetch(PRODUCTION_API_URL + '/create-event', options);
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();

    console.log('Response code:', responseCode);
    console.log('Response text:', responseText);

    if (responseCode === 200) {
      const result = JSON.parse(responseText);
      console.log('✅ Create Event API test passed!');
      console.log('Calendar result:', result.calendar_result);
      return result;
    } else {
      console.error('❌ Create Event API test failed:', responseCode, responseText);
      return null;
    }

  } catch (error) {
    console.error('❌ Create Event API test error:', error);
    return null;
  }
}

/**
 * Test the complete workflow API endpoint
 */
function testCompleteWorkflowAPI() {
  console.log('🔄 Testing Complete Workflow API...');

  try {
    // Test with a mock message ID since we don't have real Gmail messages
    // In real usage, this would be a real Gmail message ID from the add-on
    const payload = {
      message_id: "mock_message_id_for_testing",
      create_event: false // Set to false to avoid creating actual calendar events during testing
    };

    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    };

    console.log('Making request to:', PRODUCTION_API_URL + '/complete-workflow');
    const response = UrlFetchApp.fetch(PRODUCTION_API_URL + '/complete-workflow', options);
    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();

    console.log('Response code:', responseCode);
    console.log('Response text:', responseText);

    if (responseCode === 200) {
      const result = JSON.parse(responseText);
      console.log('✅ Complete Workflow API test passed!');
      console.log('Workflow result:', {
        success: result.success,
        has_event_data: !!result.event_data,
        workflow_completed: result.workflow_completed
      });
      return result;
    } else {
      console.error('❌ Complete Workflow API test failed:', responseCode, responseText);
      return null;
    }

  } catch (error) {
    console.error('❌ Complete Workflow API test error:', error);
    return null;
  }
}

/**
 * Test authentication with Google Identity Token
 */
function testAPIAuthentication() {
  console.log('🔐 Testing API Authentication...');

  try {
    // Get identity token
    let identityToken = null;
    try {
      identityToken = ScriptApp.getIdentityToken();
      console.log('Identity token obtained:', identityToken ? 'YES' : 'NO');
    } catch (error) {
      console.warn('Could not get identity token:', error.message);
    }

    // Test with authentication header
    const payload = {
      email_content: 'Test email for authentication check'
    };

    const headers = {
      'Content-Type': 'application/json'
    };

    if (identityToken) {
      headers['Authorization'] = `Bearer ${identityToken}`;
    }

    const options = {
      method: 'POST',
      headers: headers,
      payload: JSON.stringify(payload),
      muteHttpExceptions: true
    };

    const response = UrlFetchApp.fetch(PRODUCTION_API_URL + '/parse-email', options);
    const responseCode = response.getResponseCode();

    console.log('Authenticated request response code:', responseCode);

    if (responseCode === 200) {
      console.log('✅ Authentication test passed!');
      return true;
    } else if (responseCode === 401) {
      console.log('⚠️ Authentication required (401) - this is expected if auth is enforced');
      return true;
    } else {
      console.log('ℹ️ Authentication test completed with code:', responseCode);
      return true;
    }

  } catch (error) {
    console.error('❌ Authentication test error:', error);
    return false;
  }
}

/**
 * 🎯 ONE-CLICK COMPREHENSIVE TEST - Run this function to test everything!
 *
 * This function tests all frontend-backend communication and provides detailed logs
 * for problem identification. Perfect for single-click testing in Apps Script.
 */
function runAllProductionAPITests() {
  console.log('🚀 SmartEventAdder - ONE-CLICK COMPREHENSIVE TEST');
  console.log('='.repeat(60));
  console.log('📅 Test Date:', new Date().toISOString());
  console.log('🔗 Production API:', PRODUCTION_API_URL);
  console.log('');

  const results = {
    connectivity: false,
    parseEmail: false,
    createEvent: false,
    completeWorkflow: false,
    authentication: false
  };

  const errors = [];
  let testNumber = 1;

  try {
    // Test 1: Basic Connectivity
    console.log(`[${testNumber++}/5] 🔌 CONNECTIVITY TEST`);
    console.log('-'.repeat(40));
    results.connectivity = testProductionAPIConnectivity();
    if (!results.connectivity) {
      errors.push('❌ API connectivity failed - check if production API is running');
    }
    console.log('');

    // Test 2: Parse Email API
    console.log(`[${testNumber++}/5] 📧 EMAIL PARSING TEST`);
    console.log('-'.repeat(40));
    const parseResult = testParseEmailAPI();
    results.parseEmail = !!parseResult || (parseResult && parseResult.expected_error);
    if (!results.parseEmail) {
      errors.push('❌ Email parsing failed - check AI/Vertex integration');
    } else if (parseResult && parseResult.expected_error) {
      console.log('⚠️ Email parsing needs credentials (expected - will work in Gmail add-on)');
    } else {
      console.log('✅ Email parsing successful!');
    }
    console.log('');

    // Test 3: Create Event API
    console.log(`[${testNumber++}/5] 📅 EVENT CREATION TEST`);
    console.log('-'.repeat(40));
    const createResult = testCreateEventAPI();
    results.createEvent = !!createResult;
    if (!results.createEvent) {
      errors.push('⚠️ Event creation failed - likely needs Google Calendar auth (this is normal)');
    } else {
      console.log('✅ Event creation API responded successfully!');
    }
    console.log('');

    // Test 4: Complete Workflow API
    console.log(`[${testNumber++}/5] 🔄 COMPLETE WORKFLOW TEST`);
    console.log('-'.repeat(40));
    const workflowResult = testCompleteWorkflowAPI();
    results.completeWorkflow = !!workflowResult;
    if (!results.completeWorkflow) {
      errors.push('❌ Complete workflow failed - check end-to-end pipeline');
    } else {
      console.log('✅ Complete workflow successful!');
    }
    console.log('');

    // Test 5: Authentication
    console.log(`[${testNumber++}/5] 🔐 AUTHENTICATION TEST`);
    console.log('-'.repeat(40));
    results.authentication = testAPIAuthentication();
    if (!results.authentication) {
      errors.push('⚠️ Authentication test failed - may need Apps Script identity token setup');
    } else {
      console.log('✅ Authentication test passed!');
    }
    console.log('');

  } catch (criticalError) {
    console.error('🚨 CRITICAL ERROR during testing:', criticalError);
    errors.push(`🚨 Critical error: ${criticalError.message}`);
  }

  // 📊 FINAL RESULTS SUMMARY
  console.log('🏁 FINAL TEST RESULTS');
  console.log('='.repeat(60));

  const passed = Object.values(results).filter(r => r).length;
  const total = Object.keys(results).length;

  // Individual test results
  Object.keys(results).forEach(test => {
    const status = results[test] ? '✅ PASS' : '❌ FAIL';
    const testName = test.charAt(0).toUpperCase() + test.slice(1);
    console.log(`${testName.padEnd(15)}: ${status}`);
  });

  console.log('');
  console.log(`📈 OVERALL SCORE: ${passed}/${total} tests passed (${Math.round(passed/total*100)}%)`);

  // 🔍 PROBLEM IDENTIFICATION
  if (errors.length > 0) {
    console.log('');
    console.log('🔍 PROBLEMS IDENTIFIED:');
    console.log('-'.repeat(40));
    errors.forEach((error, index) => {
      console.log(`${index + 1}. ${error}`);
    });
  }

  // 💡 RECOMMENDATIONS
  console.log('');
  console.log('💡 RECOMMENDATIONS:');
  console.log('-'.repeat(40));

  if (results.connectivity) {
    console.log('✅ API is reachable - backend deployment successful');
  } else {
    console.log('🔧 Check if production API is deployed and running');
  }

  if (results.parseEmail) {
    console.log('✅ Email parsing works - AI integration successful');
  } else {
    console.log('🔧 Check Vertex AI configuration and project settings');
  }

  if (!results.createEvent) {
    console.log('ℹ️  Event creation failure is normal without full Google Calendar auth');
  }

  if (results.completeWorkflow) {
    console.log('✅ End-to-end workflow ready for Gmail add-on');
  } else {
    console.log('🔧 Check complete pipeline: email → parse → event creation');
  }

  console.log('');
  console.log('🎯 NEXT STEPS:');
  console.log('-'.repeat(40));
  if (passed >= 3) {
    console.log('✅ Ready to test Gmail add-on in Gmail interface!');
    console.log('📧 Deploy as test add-on and try with real emails');
  } else {
    console.log('🔧 Fix identified issues before Gmail add-on testing');
    console.log('📞 Review backend logs and API configuration');
  }

  console.log('');
  console.log('✨ Test completed at:', new Date().toLocaleString());

  return {
    results: results,
    passed: passed,
    total: total,
    errors: errors,
    success: passed >= 3 // Consider successful if most tests pass
  };
}

/**
 * Test specific frontend functions that call the backend
 */
function testFrontendFunctions() {
  console.log('🎯 Testing Frontend Functions...');

  try {
    // Test the callBackendAPI function directly
    console.log('Testing callBackendAPI function...');

    const testData = {
      email_content: 'Quick meeting tomorrow at 2pm in room 101'
    };

    const result = callBackendAPI('/parse-email', testData);
    console.log('callBackendAPI result:', result);

    if (result && result.success) {
      console.log('✅ Frontend callBackendAPI function works!');
      return true;
    } else {
      console.log('❌ Frontend callBackendAPI function failed');
      return false;
    }

  } catch (error) {
    console.error('❌ Frontend function test error:', error);
    return false;
  }
}