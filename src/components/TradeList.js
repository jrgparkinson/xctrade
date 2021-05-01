import React, { Component } from "react";
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';

class TradeList extends Component {

  constructor(props) {
    super(props)
    this.state = {
      trades: [],
    }
  }
  componentWillReceiveProps(props) {
    this.setState({ trades: props.trades });
  }

  render() {
    const trades = this.state.trades.sort((a,b)=>new Date(b.timestamp)-new Date(a.timestamp));
    console.log("Trades: " + JSON.stringify(trades));

    if (trades != null && trades.length > 0) {
    
    return (
      <Card style={{marginTop:10}}>
      <CardContent>
        <h4>Trades</h4>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Date</TableCell>
            <TableCell>Volume</TableCell>
            <TableCell>Unit Price</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {!trades || trades.length <= 0 ? (
            <TableRow>
              <TableCell colSpan="6" align="center">
                <b>None found</b>
              </TableCell>
            </TableRow>
          ) : (
            trades.map(trade => (
              <TableRow key={trade.pk}>
                <TableCell>{new Date(trade.timestamp).toLocaleString()}</TableCell>
                <TableCell>{trade.volume}</TableCell>
                <TableCell>{trade.unit_price}</TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
      </CardContent></Card>
    );
            } else {
              return ("");
            }
  }
}

export default TradeList;
