import React from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import useMediaQuery from '@material-ui/core/useMediaQuery';
import {useTheme, makeStyles} from '@material-ui/core/styles';
import Alert from '@material-ui/lab/Alert';
import API from '../utils/api';
import Snackbar from '@material-ui/core/Snackbar';

const useStyles = makeStyles((theme) => ({
  root: {
    width: 'inherit',
  },
  buySell: {
    width: '97%', // 'inherit', // '97%',
    position: 'fixed',
    bottom: 60,
    zIndex: 1100,
    [theme.breakpoints.up('sm')]: {
      bottom: 10,
      width: 'calc(97% - 200px)',
    },
    // backgroundColor: 'white'
  },
}));

export default function OrderCreate({athlete, orderPrices, onCreate}) {
  const [open, setOpen] = React.useState(false);
  const [openSnackbar, setOpenSnackbar] = React.useState(false);
  const [title, setTitle] = React.useState('Buy');
  const [volume, setVolume] = React.useState(1.0);
  const [unitPrice, setUnitPrice] = React.useState(0.0);
  const [createError, setCreateError] = React.useState(null);


  const handleClickOpen = () => {
    console.log(orderPrices);
    console.log(athlete);
    setUnitPrice(athlete.value);
    setOpen(true);
  };

  const handleClickOpenBuy = () => {
    setTitle('Buy');
    handleClickOpen();
  };

  const handleClickOpenSell = () => {
    setTitle('Sell');
    handleClickOpen();
  };

  const handleVolume = (event) => {
    setVolume(event.target.value);
  };
  const handlePrice = (event) => {
    setUnitPrice(event.target.value);
  };

  const getTotalPrice = () => {
    return Number(volume*unitPrice).toFixed(2);
  };

  const getError = () => {
    if (title === 'Buy' && getTotalPrice() > orderPrices.capital) {
      return 'Insufficient funds';
    } else if (title === 'Sell' && volume > orderPrices.shares_owned) {
      return 'Insufficient shares';
    } else if (volume <= 0) {
      return 'Volume must be >= 0';
    } else if (unitPrice <= 0) {
      return 'Price must be >= 0';
    }
    return null;
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleSubmit = () => {
    let buy_sell = 'B';
    if (title === 'Sell') {
      buy_sell = 'S';
    }
    API.postOrder({
      athlete_id: athlete.pk,
      volume: volume,
      unit_price: unitPrice,
      buy_sell: buy_sell,
    }).then((res) => {
      console.log(res);

      if (res.status === 201) {
        console.log('No error');
        setCreateError(false);
        setOpen(false);
        onCreate();
      } else {
        console.log('Has error: ' + res.statusText);
        setCreateError(res.statusText);
        // setOpenSnackbarError(true);
      }
      setOpenSnackbar(true);
    })
        .catch((error) => {
          setCreateError(true);
          console.log(error.response);
          console.log(error.response.data.detail);
          if (error.response.data.detail) {
            setCreateError(error.response.data.detail);
          }
          setOpenSnackbar(true);
        });
  };


  const handleCloseSnackbar = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }

    setOpenSnackbar(false);
  };

  const theme = useTheme();
  const fullScreen = useMediaQuery(theme.breakpoints.down('xs'));
  const classes = useStyles();

  return (
    <div>
      <div className={classes.buySell}>
        <div style={{float: 'left', width: '48%', textAlign: 'center'}}>
          <Button variant="contained" fullWidth={true} size="large" color="primary" onClick={handleClickOpenBuy}>
        Buy
          </Button>
        </div>
        <div style={{float: 'right', width: '48%', textAlign: 'center'}}>
          <Button variant="contained" fullWidth={true} size="large" color="secondary" onClick={handleClickOpenSell}>
        Sell
          </Button>
        </div>
      </div>
      <Dialog fullScreen={fullScreen} open={open} onClose={handleClose} aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">{title} {athlete.name} (owned: {orderPrices.shares_owned})</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="volume"
            label="Volume"
            type="number"
            value={volume}
            fullWidth
            onKeyDown={handleVolume}
            onChange={handleVolume}
          />
          <TextField
            autoFocus
            margin="dense"
            id="unitPrice"
            label="Unit price"
            type="number"
            value={unitPrice}
            fullWidth
            onKeyDown={handlePrice}
            onChange={handlePrice}
          />
          Total price: {getTotalPrice()} (available cash: {orderPrices.capital})

          {getError() ? <Alert severity="error">{getError()}</Alert>: ''}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="primary">
            Cancel
          </Button>
          <Button onClick={handleSubmit} color="primary"
            disabled={getError() !== null}>
            Place order
          </Button>
        </DialogActions>
      </Dialog>
      <Snackbar open={openSnackbar} autoHideDuration={6000} onClose={handleCloseSnackbar}>
        { createError ? <Alert onClose={handleCloseSnackbar} severity="error">
          {createError.length !== undefined ? 'Error creating order: ' + createError : 'Error creating order.'}
        </Alert> :
        <Alert onClose={handleCloseSnackbar} severity="success">
          Order created successfully.
        </Alert> }
      </Snackbar>
    </div>
  );
}
