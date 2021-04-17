import React, { Component } from "react";
import Button from '@material-ui/core/Button';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import API from "../utils/api";
import LinearProgress from '@material-ui/core/LinearProgress';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';

class OrderList extends Component {
  // state = {
  //   orders: [],
  // };

  constructor(props) {
    super(props)
    this.state = {
      orders: [],
      userDetails: null
    }
  }
  componentWillReceiveProps(props) {
    this.setState({ orders: props.orders,
     userDetails: props.userDetails });
     console.log(this.state);
  }

  componentDidMount() {
    this.resetState();
  }

  getOrders = () => {
    API.getOrders().then(res => this.setState({ orders: res.data }));
  };

  resetState = () => {
    this.getOrders();
  };

  cancelOrder(pk) {
    console.log("Cancel order: " + pk);
    API.cancelOrder(pk).then(res => {
      console.log(res);
      this.resetState();
    }).catch(
      error => {
        console.log(error);
      console.log(error.response); }
    );
  };

  render() {
    const orders = this.state.orders;

    if (orders != null && orders.length > 0) {
    
    return (
     
      <Card style={{marginTop:10}}>
      <CardContent>
        <h4>Your orders
          {
            this.state.userDetails != null ?
            <span> (you own {this.state.userDetails.shares_owned} shares)</span>
            : ""
          } </h4>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell></TableCell>
            <TableCell>Volume</TableCell>
            <TableCell>Price</TableCell>
            <TableCell></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {!orders || orders.length <= 0 ? (
            <TableRow>
              <TableCell colSpan="6" align="center">
                <b>Ops, no one here yet</b>
              </TableCell>
            </TableRow>
          ) : (
            orders.map(order => (
              <TableRow key={order.pk}>
                <TableCell>{order.buy_sell === "B" ? "Buy" : "Sell"}</TableCell>
                <TableCell>{order.volume}
                <LinearProgress variant="determinate" value={100*(order.volume - order.unfilled_volume)/order.volume} />
                </TableCell>
                <TableCell>{order.unit_price}</TableCell>
              <TableCell> 
                {order.status === "O" ?
                <Button variant="contained" color="info" onClick={() => this.cancelOrder(order.pk)}>   
        Cancel
      </Button> : "Filled"}</TableCell>
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

export default OrderList;
