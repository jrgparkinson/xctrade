import React, { Component } from "react";
import { withRouter } from "react-router";
import API from '../utils/api';
import ResultsList from "./ResultsList";
import Grid from '@material-ui/core/Grid';
import DividendCalculator from "./DividendCalculator";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';

class RaceDetail extends Component {
    state = {
        race: null,
    };
    
    componentDidMount() {
        this.resetState();
    }

    getId = () => { return this.props.match.params.raceId; }
    
    getRace = () => {
        const raceId = this.getId();
        console.log("Race id:" + raceId);
        API.getRace(raceId).then(res => this.setState({ race: res.data }));
    };
    
    resetState = () => {
        this.getRace();
    };
        
    render() {
        
        let race = this.state.race;

        console.log(race);

        

        if (race) {
            let date = new Date(race.time);
            
            return (
            <div style={{marginBottom:50}}>
                <Grid container spacing={2} direction="row" justify="space-between">
          <Grid item xs={12}>
                <h3>{race.name}, {date.toLocaleDateString()} {date.toLocaleTimeString()}</h3>
                </Grid>
                </Grid>

                <Card  style={{marginBottom:20}}>
                <CardContent  
                // style={{paddingBottom: 0}}
                >
      <Grid container spacing={2} direction="row" justify="space-between">

                <Grid item xs={4} md={2}>
                <h5>Dividend</h5>
                </Grid>
                <Grid item xs={8} md={6}>
                
                    Max: <b>${race.max_dividend}</b>, min: <b>${race.min_dividend}</b>
                    </Grid>
                    <Grid item xs={12} md={4} style={{textAlign: "center"}}>
                <DividendCalculator race={race}/></Grid>
                </Grid>
                </CardContent>
                </Card>

                
            <h5>Results</h5>
            {race.results && race.results.length > 0 ? 
            <ResultsList results={race.results} />
            :
            "No results yet"}
           
          </div>);
        } else {
            return <div><h3>Unknown race</h3></div>;
        }
        
    }
}

export default withRouter(RaceDetail)