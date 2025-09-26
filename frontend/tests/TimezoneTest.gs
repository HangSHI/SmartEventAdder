/**
 * Quick Timezone Detection Test
 * Copy this to Apps Script and run testMyTimezone() to verify timezone detection
 */

function testMyTimezone() {
  console.log('🌍 Testing Your Timezone Detection...');

  try {
    // Method 1: Calendar timezone
    try {
      const calendarTimezone = CalendarApp.getDefaultCalendar().getTimeZone();
      console.log('✅ Calendar timezone:', calendarTimezone);
    } catch (e) {
      console.log('❌ Calendar timezone failed:', e.message);
    }

    // Method 2: Session timezone
    try {
      const sessionTimezone = Session.getScriptTimeZone();
      console.log('✅ Session timezone:', sessionTimezone);
    } catch (e) {
      console.log('❌ Session timezone failed:', e.message);
    }

    // Method 3: User locale
    try {
      const userLocale = Session.getActiveUserLocale();
      console.log('✅ User locale:', userLocale);
    } catch (e) {
      console.log('❌ User locale failed:', e.message);
    }

    // Test the actual function
    const detectedTimezone = getUserTimezone();
    console.log('🎯 Final detected timezone:', detectedTimezone);

    // Show sample times
    const now = new Date();
    console.log('🕐 Current time in detected timezone:', now.toLocaleString('en-US', { timeZone: detectedTimezone }));
    console.log('🕐 Current time in Japan (JST):', now.toLocaleString('en-US', { timeZone: 'Asia/Tokyo' }));
    console.log('🕐 Current time in New York (EST):', now.toLocaleString('en-US', { timeZone: 'America/New_York' }));

    console.log('✅ Timezone test completed!');

  } catch (error) {
    console.error('❌ Timezone test failed:', error);
  }
}

function getUserTimezone() {
  try {
    const userTimeZone = CalendarApp.getDefaultCalendar().getTimeZone();
    console.log('User timezone from Calendar:', userTimeZone);
    return userTimeZone;
  } catch (calendarError) {
    console.warn('Failed to get calendar timezone:', calendarError.message);

    try {
      const sessionTimeZone = Session.getScriptTimeZone();
      console.log('User timezone from Session:', sessionTimeZone);
      return sessionTimeZone;
    } catch (sessionError) {
      console.warn('Failed to get session timezone:', sessionError.message);

      try {
        const userLocale = Session.getActiveUserLocale();
        console.log('User locale:', userLocale);

        const localeTimezoneMap = {
          'ja': 'Asia/Tokyo',
          'en_US': 'America/New_York',
          'en_GB': 'Europe/London',
          'de': 'Europe/Berlin',
          'fr': 'Europe/Paris',
          'zh_CN': 'Asia/Shanghai',
          'ko': 'Asia/Seoul',
          'en_AU': 'Australia/Sydney'
        };

        const mappedTimezone = localeTimezoneMap[userLocale] || localeTimezoneMap[userLocale.split('_')[0]];
        if (mappedTimezone) {
          console.log('Mapped timezone from locale:', mappedTimezone);
          return mappedTimezone;
        }
      } catch (localeError) {
        console.warn('Failed to get user locale:', localeError.message);
      }

      console.warn('Using UTC as final fallback timezone');
      return 'UTC';
    }
  }
}