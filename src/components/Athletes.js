import React, { Component } from "react";
import { Col, Container, Row } from "reactstrap";
import AthleteList from "./AthleteList";
// import NewStudentModal from "./NewStudentModal";

import API from '../utils/api';

class Athletes extends Component {
  state = {
    athletes: [],
  };

  componentDidMount() {
    this.resetState();
  }

  getAthletes = () => {
    console.log("Token: " + localStorage.getItem('token'));
    // axios. Authorization: 'Token ' + localStorage.getItem('token')
    API.getAthletes().then(res => this.setState({ athletes: res.data }));
    // axios.get(API_URL + "athletes/", {headers: {'Authorization': 'Token ' + localStorage.getItem('token')}}).then(res => this.setState({ athletes: res.data }));
  };

  resetState = () => {
    this.getAthletes();
  };

  render() {
    return (
      <Container style={{ marginTop: "20px" }}>
        <Row>
          <Col>
            <AthleteList
              athletes={this.state.athletes}
              resetState={this.resetState}
            />
          </Col>
        </Row>
        {/* <Row>
          <Col>
            <NewStudentModal create={true} resetState={this.resetState} />
          </Col>
        </Row> */}
      </Container>
    );
  }
}

export default Athletes;