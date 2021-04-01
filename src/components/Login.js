import React from 'react';
import axios from "axios";
import { GoogleLogin } from 'react-google-login';
// refresh token
import { refreshTokenSetup } from '../utils/refreshToken';

import { API_URL, GOOGLE_OAUTH_ID, GOOGLE_OAUTH_SECRET } from "../constants";


function Login() {
  const onSuccess = (res) => {
    console.log(res);
    console.log('Login Success: currentUser:', res.profileObj);
    refreshTokenSetup(res);

    axios.post(API_URL + 'oauth/google-oauth2/', res.tc)
    .then((response) => {
        console.log(response);
        // this.props.saveToken(response.data.token);
        localStorage.setItem('token', response.data.token);
        axios.defaults.headers.common['Authorization'] =  'Token ' + localStorage.getItem('token');
 
      }, (error) => {
        console.log(error);
      });
    // {
    //   firstName: 'Finn',
    //   lastName: 'Williams'
    // });
  };

  const onFailure = (res) => {
    console.log('Login failed: res:', res);
    // alert(
    //   `Failed to login. 😢 Please ping this to repo owner twitter.com/sivanesh_fiz`
    // );
  };

  return (
    <div>
      <GoogleLogin
        clientId={GOOGLE_OAUTH_ID}
        buttonText="Login"
        onSuccess={onSuccess}
        onFailure={onFailure}
        cookiePolicy={'single_host_origin'}
        style={{ marginTop: '100px' }}
        isSignedIn={true}
      />
    </div>
  );
}

export default Login;