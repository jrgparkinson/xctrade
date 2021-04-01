import React, { Component } from "react";
import { Col, Container, Row } from "reactstrap";
import OrderList from "./OrderList";

import API from '../utils/api';

class Orders extends Component {
  state = {
    orders: [],
  };

  componentDidMount() {
    this.resetState();
  }

  getOrders = () => {
    API.getOrders().then(res => this.setState({ orders: res.data }));
  };

  resetState = () => {
    this.getOrders();
  };

  render() {
    return (
      <Container style={{ marginTop: "20px" }}>
        <Row>
          <Col>
            <OrderList
              orders={this.state.orders}
              resetState={this.resetState}
            />
          </Col>
        </Row>
      </Container>
    );
  }
}

export default Orders;
