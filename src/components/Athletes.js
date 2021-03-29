import React, { Component } from "react";
import { Col, Container, Row } from "reactstrap";
import AthleteList from "./AthleteList";
import TextField from '@material-ui/core/TextField';
import {
  Switch,
  Route,
  withRouter,
} from "react-router-dom";
import AthleteDetail from "./AthleteDetail";
// import NewStudentModal from "./NewStudentModal";

import API from '../utils/api';

class Athletes extends Component {
  state = {
    filter: "",
    athletes: []
  };

  componentDidMount() {
    this.resetState();
  }

  getAthletes = () => {
    console.log("Token: " + localStorage.getItem('token'));
    API.getAthletes().then(res => this.setState({ athletes: res.data }));
    
  };

  resetState = () => {
    this.getAthletes();
    // this.sortAthletes();
  };

  // sortAthletes = () => {
  //   console.log(this.athletes);
  //   if (this.athletes != undefined) {
  //     this.athletes.sort(function(a, b) { 
  //       return a.value - b.value;
  //   })
  //   }
  // }

  
  handleChange = event => {
    this.setState({ filter: event.target.value });
  };


  render() {
    // let match = useRouteMatch();
    let match = this.props.match;

    // if (match.path === "/") { match.path = "/Athletes/"; }
    
    console.log("Match: " + JSON.stringify(match));
    const { filter, athletes } = this.state;
    // sort by value descending
      athletes.sort(function(a, b) { 
        return b.value - a.value;
    })

    const lowercasedFilter = filter.toLowerCase();
    const filteredAthletes = athletes.filter(item => { return item.name.toLowerCase().includes(lowercasedFilter);  }  );
    return (
      <Container style={{ width:"100%", maxWidth: "100%", marginLeft: "0px", marginRight: "0px", padding: "0px"}}>
            <Switch>
        <Route path={`${match.path}/:athleteId`}>
          <AthleteDetail />
        </Route>
        <Route path={match.path}>
         <Row>
         <Col>
         
     
          
<TextField id="search" label="Search" variant="outlined" value={filter} onChange={this.handleChange} fullWidth={true} />
</Col>
         </Row>
        <Row>
          <Col>
            <AthleteList
              athletes={filteredAthletes}
              resetState={this.resetState}
            />
          </Col>
        </Row>
        </Route></Switch>
      </Container>
    );
  }
}



export default withRouter(Athletes);