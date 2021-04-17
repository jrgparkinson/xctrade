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
import Auction from './components/Auction';
import {Route, Switch, BrowserRouter} from 'react-router-dom';
import {makeStyles} from '@material-ui/core/styles';
import {drawerWidth, breakpointSize} from "./utils/links";
import useMediaQuery from '@material-ui/core/useMediaQuery';
import { createMuiTheme, ThemeProvider } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';


const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
  },
  drawer: {
    [theme.breakpoints.up(breakpointSize)]: {
      width: drawerWidth,
      flexShrink: 0,
    },
  },
  appBar: {
    marginLeft: drawerWidth,
    [theme.breakpoints.up(breakpointSize)]: {
      width: `calc(100% - ${drawerWidth}px)`,
    },
  },
  menuButton: {
    marginRight: theme.spacing(2),
    [theme.breakpoints.up(breakpointSize)]: {
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
    marginLeft: 0,
    [theme.breakpoints.up(breakpointSize)]: {
      marginLeft: drawerWidth,
    },
  },
}));

// class App extends Component {
function App(props) {
  const classes = useStyles();

const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');

  const theme = React.useMemo(
    () =>
      createMuiTheme({
        palette: {
          type: prefersDarkMode ? 'dark' : 'light',
        },
      }),
    [prefersDarkMode],
  );


  return (
<ThemeProvider theme={theme}>
      <CssBaseline/>
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
            <Route path="/Auction" component={Auction} />
          </Switch>

        </main>

      </BrowserRouter>
    </Fragment>
</ThemeProvider>
  );
}

export default App;
