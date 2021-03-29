import React from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Dialog from '@material-ui/core/Dialog';
import Paper from '@material-ui/core/Paper';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import useMediaQuery from '@material-ui/core/useMediaQuery';
import {useTheme} from '@material-ui/core/styles';
import {
  evaluate,
} from 'mathjs';

export default function DividendCalculator({race}) {
  const [open, setOpen] = React.useState(false);
  const [numComp, setNumComp] = React.useState(50);
  const [position, setPosition] = React.useState(1);


  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleNumComp = (event) => {
    setNumComp(event.target.value);
  };
  const handlePosition = (event) => {
    setPosition(event.target.value);
  };

  const getDividend = () => {
    const eqs = require('../utils/math.json');
    const eq = eqs.dividend; //  "d_min + (d_max - d_min) * (num_comp - position) / (num_comp-1)";
    const scope = {
      d_min: race.min_dividend,
      d_max: race.max_dividend,
      num_comp: numComp,
      position: position,
    };
    console.log(scope);
    return evaluate(eq, scope).toFixed(2);
    // return Number(numComp*position).toFixed(2);
  };


  const handleClose = () => {
    setOpen(false);
  };

  const theme = useTheme();
  const fullScreen = useMediaQuery(theme.breakpoints.down('xs'));


  return (
    <div>

      <Button variant="contained" color="secondary" onClick={handleClickOpen}>
        Dividend calculator
      </Button>
      <Dialog fullScreen={fullScreen} open={open} onClose={handleClose} aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">Dividend Calculator for {race.name}</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            id="numComp"
            label="Total runners in race"
            type="number"
            value={numComp}
            fullWidth
            onKeyDown={handleNumComp}
            onChange={handleNumComp}
          />
          <TextField
            autoFocus
            margin="dense"
            id="position"
            label="Position"
            type="number"
            value={position}
            fullWidth
            onKeyDown={handlePosition}
            onChange={handlePosition}
          />

          <Paper style={{paddingTop: 10, textAlign: 'center'}}
            variant="outlined"
            elevation={0}>
            <h5>Dividend: <b>{getDividend()}</b></h5>
          </Paper>

        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="primary">
            Close
          </Button>

        </DialogActions>
      </Dialog>

    </div>
  );
}
