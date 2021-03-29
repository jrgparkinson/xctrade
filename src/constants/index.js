let apiUrl;
if (window.location.hostname.includes('heroku')) {
  apiUrl = 'https://xctrade.herokuapp.com/api/';
} else {
  apiUrl = 'http://127.0.0.1:8000/api/';
}
export const API_URL=apiUrl;
export const GOOGLE_OAUTH_ID = '976464063211-pu7l0ondr00ifp1127pnqj04nfp9m2f9.apps.googleusercontent.com';
