import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import MoreIcon from '@material-ui/icons/MoreVert';
import API from '../utils/api';
import axios from 'axios';
import {GoogleLogin, GoogleLogout} from 'react-google-login';
import {refreshTokenSetup} from '../utils/refreshToken';
import Button from '@material-ui/core/Button';
import {API_URL, GOOGLE_OAUTH_ID} from '../constants';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';
import Alert from '@material-ui/lab/Alert';
import Snackbar from '@material-ui/core/Snackbar';
import {Link} from 'react-router-dom';

const options = [
  {text: 'About', link: "/About"}
];

const ITEM_HEIGHT = 48;

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1,
  },
  menuButton: {
    marginRight: theme.spacing(2),
  },
  title: {
    flexGrow: 1,
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
  },
}));

export default function Header() {
  const classes = useStyles();
  const [openSnackbar, setOpenSnackbar] = React.useState(false);

  const onSuccess = (res) => {
    console.log(res);
    console.log('Login Success: currentUser:', res.profileObj);
    refreshTokenSetup(res);

    axios.post(API_URL + 'oauth/google-oauth2/', res.tc)
        .then((response) => {
          console.log(response);
          // this.props.saveToken(response.data.token);
          localStorage.setItem('token', response.data.token);
          axios.defaults.headers.common['Authorization'] = 'Token ' + localStorage.getItem('token');
          window.location.reload(false);
        }, (error) => {
          console.log(error);
          setOpenSnackbar(true);
        });
  };

  const onFailure = (res) => {
    console.log('Login failed: res:', res);
    setOpenSnackbar(true);
  };

  const onLogoutSuccess = () => {
    console.log('Logout made successfully');
    localStorage.setItem('token', null);
    window.location.reload(false);
  };

  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleCloseSnackbar = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setOpenSnackbar(false);
  };


  return (
    <div className={classes.root}>
      <AppBar position="fixed" className={classes.appBar}>
        <Toolbar>
          <Typography variant="h6" className={classes.title}>
            XC Trade
          </Typography>
          {API.isAuthorised() ? <GoogleLogout
            clientId={GOOGLE_OAUTH_ID}
            tag={'span'}
            onLogoutSuccess={onLogoutSuccess}
            render={(renderProps) => (
              <Button onClick={renderProps.onClick} disabled={renderProps.disabled} color="inherit">Logout</Button>
            )}
            buttonText="Login"
          /> :
          <GoogleLogin
            clientId={GOOGLE_OAUTH_ID}
            render={(renderProps) => (
              <Button onClick={renderProps.onClick} disabled={renderProps.disabled} color="inherit">Login</Button>
            )}
            buttonText="Login"
            onSuccess={onSuccess}
            onFailure={onFailure}
            cookiePolicy={'single_host_origin'}
            style={{marginTop: '100px'}}
            isSignedIn={true}
            tag={'span'}
          />
          }
          <IconButton aria-label="display more actions" edge="end" color="inherit"
          onClick={handleClick}>
            <MoreIcon />
          </IconButton>
          <Menu
            id="long-menu"
            anchorEl={anchorEl}
            keepMounted
            open={open}
            onClose={handleClose}
            PaperProps={{
              style: {
                maxHeight: ITEM_HEIGHT * 4.5,
                width: '20ch',
              },
            }}
          >
            {options.map((option) => (
              <MenuItem 
              component={ Link } to={option.link}
              key={option.text}
               >
                 {option.text}
              </MenuItem>
            ))}
          </Menu>
        </Toolbar>
      </AppBar>

      <Snackbar open={openSnackbar} autoHideDuration={6000} onClose={handleCloseSnackbar}>
        <Alert onClose={handleCloseSnackbar} severity="error">
          Error logging in
        </Alert>
      </Snackbar>

    </div>
  );
}
