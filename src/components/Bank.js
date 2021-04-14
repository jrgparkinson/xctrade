import React, { Component } from "react";
import { Container } from "reactstrap";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';

class Bank extends Component {

  render() {
    return (
      <Container>
          <h1>Bank</h1>
          
      <Card style={{marginTop:10}}>
      <CardContent>
      Opening soon
      </CardContent>
      </Card>
      </Container>
    );
  }
}

export default Bank;
