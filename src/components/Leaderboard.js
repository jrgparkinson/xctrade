import React, { Component } from "react";
import { Container } from "reactstrap";
import { Table } from "reactstrap";

import API from '../utils/api';

class Leaderboard extends Component {
  state = {
    entities: [],
  };

  componentDidMount() {
    this.resetState();
  }

  getEntities = () => {
    API.getEntities().then(res => this.setState({ entities: res.data }));
  };

  resetState = () => {
    this.getEntities();
  };

  render() {
      let entities = this.state.entities;
      entities.sort(function(a, b) { 
        return b.portfolio_value - a.portfolio_value;
    })
    return (
      <Container>
        <h3>Leaderboard</h3>
        <Table>
        <thead>
          <tr>
            <th></th>
            <th>Name</th>
            <th>Portfolio value</th>
          </tr>
        </thead>
        <tbody>
          {!entities || entities.length <= 0 ? (
            <tr>
              <td colSpan="6" align="center">
                ...
              </td>
            </tr>
          ) : (
            entities.map((entity, index) => (
              <tr key={entity.pk}>
                <td>{index+1}</td>
                <td>{entity.name}</td>
                <td>{entity.portfolio_value}</td>
              </tr>
            ))
          )}
        </tbody>
      </Table>
      </Container>
    );
  }
}

export default Leaderboard;
