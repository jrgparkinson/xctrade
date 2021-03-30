import './App.css';
import React, { Component, Fragment } from "react";
import Header from "./components/Header";
import Home from "./components/Home";
// import Login from "./components/Login";
// import Logout from "./components/Logout";
import {Helmet} from "react-helmet";

{/* <Login />
<Logout /> */}

class App extends Component {
  render() {
    return (
     <div>
       <Helmet>
         <meta name="google-site-verification" content="XgQIxzadoD1l96u2A3av9GPyRdSBQRkXLOQr019BDD4" />
         </Helmet>
     
      <Fragment>
        <Header />
       
        <Home />
      </Fragment>
      </div>
    );
  }
}

export default App;
