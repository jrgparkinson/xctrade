import React, { Component } from "react";
import { Container } from "reactstrap";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import API from '../utils/api';
import Grid from '@material-ui/core/Grid';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import LoanCreate from "./LoanCreate";
import LoanItem from "./LoanItem";
import Alert from '@material-ui/lab/Alert';
import Snackbar from '@material-ui/core/Snackbar';


class Bank extends Component {

  state = {
    loans: [],
    loanInfo: [],
    snackbarOpen: false,
    error: null,
};

componentDidMount() {
    this.resetState();
}

handleRepayResponse = (error) => {
  if (error === null) {
    this.resetState();
    this.setState({snackbarOpen: true, error: null});
  } else {
    if (error.response) {
      console.log(error.response.data.detail);
      this.setState({snackbarOpen: true, error: error.response.data.detail});
    } else {
      console.log(error);
      this.setState({snackbarOpen: true, error: error});
    }
  }
}

resetState = () => {
    API.getLoans().then(res => this.setState({ loans: res.data }));
    API.getLoanInfo().then(res => this.setState({loanInfo: res.data}));
};

handleCloseSnackbar = (event, reason) => {
  if (reason === 'clickaway') {
    return;
  }

  this.setState({snackbarOpen: false});
};

  render() {
    console.log(this.state.loans);
    console.log(this.state.loanInfo);

    const loans = this.state.loans;
    return (
      <Container>
        <h1>Cowley Club Bank</h1>

        <Card style={{ marginTop: 10 }}>
          <CardContent>
            <Grid container spacing={2}
              direction="row"
              justify="space-between">
              <Grid item>
                <h2>Loans</h2>
              </Grid>
              <Grid item>
                <LoanCreate loanInfos={this.state.loanInfo} onCreate={this.resetState} />
              </Grid>
            </Grid>

            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Balance</TableCell>
                  <TableCell>Interest Rate</TableCell>
                  <TableCell>Interest period</TableCell>
                  <TableCell></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {!loans || loans.length <= 0 ? (
                  <TableRow>
                    <TableCell colSpan="6" align="center">
                      <b>None</b>
                    </TableCell>
                  </TableRow>
                ) : (
                  loans.map(loan => (
                    <LoanItem key={loan.pk} loan={loan} onSubmit={this.handleRepayResponse} />
                  ))
                )}
              </TableBody>
            </Table>

          </CardContent>
        </Card>



        <Snackbar open={this.state.snackbarOpen} autoHideDuration={6000} onClose={this.handleCloseSnackbar}>
          {this.state.error ? <Alert onClose={this.handleCloseSnackbar} severity="error">
            {this.state.error.length !== undefined ? 'Error: ' + this.state.error : 'Error processing request.'}
          </Alert> :
            <Alert onClose={this.handleCloseSnackbar} severity="success">
              Request processed successfully
        </Alert>}
        </Snackbar>

      </Container>
    );
  }
}

export default Bank;
