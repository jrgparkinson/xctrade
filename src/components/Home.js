import React, { Component } from "react";
import { Col, Container, Row } from "reactstrap";
import AthleteList from "./AthleteList";
// import NewStudentModal from "./NewStudentModal";

import axios from "axios";

import { API_URL } from "../constants";

class Home extends Component {
  state = {
    athletes: []
  };

  componentDidMount() {
    this.resetState();
  }

  getAthletes = () => {
    axios.get(API_URL + "athletes/").then(res => this.setState({ athletes: res.data }));
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

export default Home;