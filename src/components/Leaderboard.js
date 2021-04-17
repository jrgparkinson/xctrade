import React, { Component } from "react";
import { Container } from "reactstrap";
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Typography from '@material-ui/core/Typography';

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
         <Typography variant="h3">Leaderboard</Typography>
        <Table>
        <TableHead>
          <TableRow>
            <TableCell></TableCell>
            <TableCell><Typography variant="body1">Name</Typography></TableCell>
            <TableCell>Portfolio value</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {!entities || entities.length <= 0 ? (
            <TableRow>
              <TableCell colSpan="6" align="center">
                ...
              </TableCell>
            </TableRow>
          ) : (
            entities.map((entity, index) => (
              <TableRow key={entity.pk}>
                <TableCell>{index+1}</TableCell>
                <TableCell>{entity.name}</TableCell>
                <TableCell>{entity.portfolio_value}</TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
      </Container>
    );
  }
}

export default Leaderboard;
