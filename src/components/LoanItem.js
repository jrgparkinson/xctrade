
import TextField from '@material-ui/core/TextField';
import TableCell from '@material-ui/core/TableCell';
import TableRow from '@material-ui/core/TableRow';
import React from "react";
import Button from '@material-ui/core/Button';
import API from '../utils/api';

export default function LoanItem({ loan, onSubmit }) {
    const [repay, setRepay] = React.useState(0.0);

    const handleRepay = (e) => {
        setRepay(e.target.value);
    }
    const handleClickRepay = (e) => {
        API.updateLoan(loan.pk, {
            "balance": loan.balance - repay
        }).then((res) => {
            console.log(res);

            if (res.status === 204) {
                console.log('No error');
                onSubmit(null);
            } else {
                console.log('Has error: ' + res.statusText);
                onSubmit(res.statusText);
            }
        })
            .catch((error) => {
                onSubmit(error);
            });
    }

    return (
        <TableRow key={loan.pk}>
            <TableCell>{loan.balance}</TableCell>
            <TableCell>{loan.loan_info.interest_rate}</TableCell>
            <TableCell>{loan.loan_info.interest_interval} days
                {loan.interest_last_added != null ?

                    <span> (last added: {new Date(loan.interest_last_added).toLocaleString()})</span>
                    : ""
                }</TableCell>
            {loan.balance > 0 ? <TableCell>

                <TextField
                    autoFocus
                    margin="dense"
                    id={"repay" + loan.pk}
                    label="Repay amount"
                    type="number"
                    value={repay}
                    onKeyDown={handleRepay}
                    onChange={handleRepay}
                />
                <Button variant="contained" size="small" color="primary" onClick={handleClickRepay}>
                    Go
            </Button>

            </TableCell> :
                <TableCell>Loan repayed</TableCell>}
        </TableRow>
    );
}