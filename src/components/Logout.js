import React from 'react';
import { GoogleLogout } from 'react-google-login';

import { GOOGLE_OAUTH_ID, GOOGLE_OAUTH_SECRET } from "../constants";


function Logout() {
  const onSuccess = () => {
    console.log('Logout made successfully');
    // alert('Logout made successfully ✌');
    localStorage.setItem('token', null);
  };

  return (
    <div>
      <GoogleLogout
        clientId={GOOGLE_OAUTH_ID}
        buttonText="Logout"
        onLogoutSuccess={onSuccess}
      ></GoogleLogout>
    </div>
  );
}

export default Logout;
