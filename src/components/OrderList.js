import React, { Component } from "react";
import { Table } from "reactstrap";
class OrderList extends Component {
  render() {
    const orders = this.props.orders;
    return (
      <Table dark>
        <thead>
          <tr>
            <th>Name</th>
            
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
                <td>{order.athlete.name}, {order.unit_price}</td>
              </tr>
            ))
          )}
        </tbody>
      </Table>
    );
  }
}

export default OrderList;
