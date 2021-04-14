import './App.css';
import React, {Fragment} from 'react';
import Header from './components/Header';
import Athletes from './components/Athletes';
import Portfolio from './components/Portfolio';
import Races from './components/Races';
import Leaderboard from './components/Leaderboard';
import SideNav from './components/SideNav';
import BottomNav from './components/BottomNav';
import Bank from './components/Bank';
import About from './components/About';
import {Route, Switch, BrowserRouter} from 'react-router-dom';
import {makeStyles} from '@material-ui/core/styles';

const drawerWidth = 200;


const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
  },
  drawer: {
    [theme.breakpoints.up('sm')]: {
      width: drawerWidth,
      flexShrink: 0,
    },
  },
  appBar: {
    marginLeft: drawerWidth,
    [theme.breakpoints.up('sm')]: {
      width: `calc(100% - ${drawerWidth}px)`,
    },
  },
  menuButton: {
    marginRight: theme.spacing(2),
    [theme.breakpoints.up('sm')]: {
      display: 'none',
    },
  },
  toolbar: theme.mixins.toolbar,
  drawerPaper: {
    width: drawerWidth,
  },
  content: {
    flexGrow: 1,
    padding: theme.spacing(1),
    marginTop: 70,
    marginBottom: 50,
    [theme.breakpoints.up('sm')]: {
      marginLeft: drawerWidth,
    },
  },
}));

// class App extends Component {
function App(props) {
  const classes = useStyles();


  return (
    <Fragment>
      <BrowserRouter>
        <Header />

        <SideNav />
        <BottomNav />

        <main className={classes.content}>
          <Switch>
            <Route path="/" component={Athletes} exact />
            <Route path="/Athletes" component={Athletes} />
            <Route path="/Leaderboard" component={Leaderboard} />
            <Route path="/Portfolio" component={Portfolio} />
            <Route path="/Races" component={Races} />
            <Route path="/About" component={About} />
            <Route path="/Bank" component={Bank} />
          </Switch>

        </main>

      </BrowserRouter>
    </Fragment>
  );
}

export default App;
