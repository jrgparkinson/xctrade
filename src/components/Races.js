import React, { Component } from "react";
import { Container } from "reactstrap";
import {
  Switch,
  Route,
  withRouter,
} from "react-router-dom";
import RaceDetail from "./RaceDetail";
import RaceCard from "./RaceCard";

import API from '../utils/api';

class Races extends Component {
  state = {
    races: []
  };

  componentDidMount() {
    this.resetState();
  }

  getRaces = () => {
    API.getRaces().then(res => this.setState({ races: res.data }));
  };

  resetState = () => {
    this.getRaces();
  };



  render() {
    let match = this.props.match;

    
    console.log("Match: " + JSON.stringify(match));
    const { races } = this.state;

    // sort by value descending
    //   races.sort(function(a, b) { 
    //     return b.value - a.value;
    // })

    const week = [
      "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"
    ];
    const year = [
      "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ];

    // Group races by date
    let dateToRaces = new Map();
    for (var i=0; i < races.length; i++) {
      let race = races[i];
      let d = new Date(race.time);
      // let key = d.toLocaleDateString();
      let key = week[d.getDay()] + " " + d.getDate() + " " + year[d.getMonth()] + " " + d.getFullYear();
      let racesForKey = dateToRaces.get(key);
      if (racesForKey === undefined ) {
        racesForKey = [];
        // dateToRaces.set(key, []);
      }
      racesForKey.push(race);
      dateToRaces.set(key, racesForKey);
    }
    let dates = [ ...dateToRaces.keys()];

    console.log(dateToRaces);
    console.log(dates);

    return (
      <Container style={{ width:"100%", maxWidth: "100%", marginLeft: "0px", marginRight: "0px", padding: "0px"}}>
            <Switch>
        <Route path={`${match.path}/:raceId`}>
          <RaceDetail />
        </Route>
        <Route path={match.path}>
          {
            dates.map(date => (
              <div><h3>{date}</h3>
              {
                dateToRaces.get(date).map(race => (
                  <RaceCard race={race} />
               ))
              }
              </div>
            ))
          }
            {/* {races.map(race => (
               <RaceCard race={race} />
            ))} */}
        </Route></Switch>
      </Container>
    );
  }
}



export default withRouter(Races);