import React, { Component } from "react";
import Button from '@material-ui/core/Button';
import { Table } from "reactstrap";
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
      orders: []
    }
  }
  componentWillReceiveProps(props) {
    this.setState({ orders: props.orders })
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
        <h4>Your orders</h4>
      <Table>
        <thead>
          <tr>
            <th></th>
            <th>Volume</th>
            <th>Price</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {!orders || orders.length <= 0 ? (
            <tr>
              <td colSpan="6" align="center">
                <b>Ops, no one here yet</b>
              </td>
            </tr>
          ) : (
            orders.map(order => (
              <tr key={order.pk}>
                <td>{order.buy_sell === "B" ? "Buy" : "Sell"}</td>
                <td>{order.volume}
                <LinearProgress variant="determinate" value={100*(order.volume - order.unfilled_volume)/order.volume} />
                </td>
                <td>{order.unit_price}</td>
              <td> 
                {order.status === "O" ?
                <Button variant="contained" color="info" onClick={() => this.cancelOrder(order.pk)}>   
        Cancel
      </Button> : "Filled"}</td>
              </tr>
            ))
          )}
        </tbody>
      </Table>
      </CardContent></Card>
    );
            } else {
              return ("");
            }
  }
}

export default OrderList;
