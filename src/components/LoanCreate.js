import React from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import useMediaQuery from '@material-ui/core/useMediaQuery';
import { useTheme } from '@material-ui/core/styles';
import Alert from '@material-ui/lab/Alert';
import API from '../utils/api';
import Snackbar from '@material-ui/core/Snackbar';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Input from '@material-ui/core/Input';
import InputLabel from '@material-ui/core/InputLabel';



export default function LoanCreate({ loanInfos, onCreate }) {
    const [open, setOpen] = React.useState(false);
    const [openSnackbar, setOpenSnackbar] = React.useState(false);
    const [balance, setBalance] = React.useState(1.0);
    const [loanType, setLoanType] = React.useState(1);
    const [createError, setCreateError] = React.useState(null);


    const handleClickOpen = () => {
        setBalance(0.0);
        if (loanInfos.length > 0) {
            setLoanType(loanInfos[0].pk);

        }
        setOpen(true);
    };

    const formatDuration = (duration) => {
        return duration + " days";
    }

    const handleBalance = (event) => {
        setBalance(event.target.value);
    };

    const handleLoanType = (event) => {
        setLoanType(event.target.value);
    }


    const getError = () => {
        return null;
    };

    const handleClose = () => {
        setOpen(false);
    };

    const handleSubmit = () => {
        API.createLoan([{
            loan_info_id: loanType,
            balance: Number(balance).toFixed(2),
        }]).then((res) => {
            console.log(res);

            if (res.status === 201) {
                console.log('No error');
                setCreateError(false);
                setOpen(false);
                onCreate();
            } else {
                console.log('Has error: ' + res.statusText);
                setCreateError(res.statusText);
            }
            setOpenSnackbar(true);
        })
            .catch((error) => {
                setCreateError(true);
                console.log(error);
                console.log(error.response);
                //   console.log(error.response.data.detail);
                if (error.response && error.response.data.detail) {
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
    //   const classes = useStyles();

    console.log("Loan infos: ");
    console.log(loanInfos);
    console.log("Loan type: " + loanType);
    return (
        <div>
            <div>

                <Button variant="contained" size="large" color="primary" onClick={handleClickOpen}>
                    New loan
          </Button>
            </div>
            <Dialog fullScreen={fullScreen} open={open} onClose={handleClose} aria-labelledby="form-dialog-title">
                <DialogTitle id="form-dialog-title">New loan</DialogTitle>
                <DialogContent>
                    <FormControl>
                        <InputLabel id="load-details-select-label">Loan interest details</InputLabel>
                        <Select
                            labelId="loaninfolabel"
                            id="loaninfo"
                            value={loanType}
                            onChange={handleLoanType}
                            input={<Input />}
                        >
                            {
                                loanInfos.length > 0 ? (
                                    loanInfos.map(loanInfo => (
                                        <MenuItem value={loanInfo.pk}>
                                            {loanInfo.interest_rate}% every {formatDuration(loanInfo.interest_interval)}
                                        </MenuItem>
                                    ))
                                ) : ("")
                            }

                        </Select></FormControl>

                    <TextField
                        autoFocus
                        margin="dense"
                        id="balance"
                        label="Loan amount"
                        type="number"
                        value={balance}
                        fullWidth
                        onKeyDown={handleBalance}
                        onChange={handleBalance}
                    />

                    {getError() ? <Alert severity="error">{getError()}</Alert> : ''}
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose} color="primary">
                        Cancel
          </Button>
                    <Button onClick={handleSubmit} color="primary"
                        disabled={getError() !== null}>
                        Take out loan
          </Button>
                </DialogActions>
            </Dialog>
            <Snackbar open={openSnackbar} autoHideDuration={6000} onClose={handleCloseSnackbar}>
                {createError ? <Alert onClose={handleCloseSnackbar} severity="error">
                    {createError.length !== undefined ? 'Error creating loan: ' + createError : 'Error creating loan.'}
                </Alert> :
                    <Alert onClose={handleCloseSnackbar} severity="success">
                        Loan created successfully.
        </Alert>}
            </Snackbar>
        </div>
    );
}
