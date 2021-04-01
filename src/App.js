import './App.css';
import React, { Component, Fragment } from "react";
import Header from "./components/Header";
import Athletes from "./components/Athletes";
import Orders from "./components/Orders";
import Login from "./components/Login";
import Logout from "./components/Logout";
import SideNav from './components/SideNav';
import { Route, Switch, BrowserRouter } from 'react-router-dom';
import { makeStyles } from "@material-ui/core/styles";

const drawerWidth = 240;


const useStyles = makeStyles(theme => ({
  root: {
    display: "flex"
  },
  drawer: {
    [theme.breakpoints.up("sm")]: {
      width: drawerWidth,
      flexShrink: 0
    }
  },
  appBar: {
    marginLeft: drawerWidth,
    [theme.breakpoints.up("sm")]: {
      width: `calc(100% - ${drawerWidth}px)`
    }
  },
  menuButton: {
    marginRight: theme.spacing(2),
    [theme.breakpoints.up("sm")]: {
      display: "none"
    }
  },
  toolbar: theme.mixins.toolbar,
  drawerPaper: {
    width: drawerWidth
  },
  content: {
    flexGrow: 1,
    padding: theme.spacing(3)
  }
}));

// class App extends Component {
function App(props) {
    const classes = useStyles();

  
    return (     
      <Fragment>
        <BrowserRouter>
        <Header />
        
        <SideNav />
        <Login />
        <Logout />

        <main className={classes.content}>
            <Switch>
                <Route path="/" component={Athletes} exact />
                <Route path="/Athletes" component={Athletes} />
                <Route path="/Orders" component={Orders} />
            </Switch>
        </main>
        </BrowserRouter>
      </Fragment>
    );
}

export default App;
