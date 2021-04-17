import React, { Component } from "react";
import { withRouter } from "react-router";
import OrderList from "./OrderList";
import API from '../utils/api';
import Grid from '@material-ui/core/Grid';
import Waiting from "./Waiting";
import AthletePriceChart from "./AthletePriceChart";
import OrderCreate from "./OrderCreate";
import TradeList from "./TradeList";
import EqualizerIcon from '@material-ui/icons/Equalizer';
import AthleteResultList from "./AthleteResultsList";
import Tooltip from '@material-ui/core/Tooltip';

class AthleteDetail extends Component {
    state = {
        loaded: false,
        athlete: null,
        trades: null,
        orders: null,
        results: null,
        orderPrices: {}
    };

    componentDidMount() {
        this.resetState();
    }

    getId = () => { return this.props.match.params.athleteId; }

    getAthlete = () => {
        const athleteId = this.getId();
        console.log("Athlete id:" + athleteId);
        API.getAthlete(athleteId).then(res => this.setState({ athlete: res.data }));
    };

    resetState = () => {
        console.log("Athlete detail reset state");
        this.getAthlete();
        API.getTrades(this.getId()).then(res => this.setState({ trades: res.data }));
        API.getAtheletePriceDetails(this.getId()).then(res => this.setState({ orderPrices: res.data }));
        API.getOrders().then(res => this.setState({ orders: res.data }));
        API.getResultsForAthlete(this.getId()).then(res => this.setState({ results: res.data }));
        this.setState({ loaded: true });
    };

    render() {
        let athlete = this.state.athlete;

        if (!this.state.loaded) { return <div><Waiting /></div>; }

        if (athlete) {
            // let {change, changeColor} = formatPercentChange(athlete.percent_change);
            return <div style={{ marginBottom: 50 }}>
                <Grid container spacing={2}
                    direction="row"
                    justify="space-between">
                    <Grid item>
                        <h3>{athlete.name}</h3>
                    </Grid>
                    <Grid item>
                        <h5>
                            <Tooltip title="Value">
                                <span>${athlete.value} </span>
                            </Tooltip>
                   /
                   <Tooltip title="7-day volume"><span>
                                <EqualizerIcon />{athlete.weekly_volume}
                            </span>
                            </Tooltip>
                        </h5>
                    </Grid>

                </Grid>

                {API.isAuthorised() ? <OrderCreate athlete={athlete} orderPrices={this.state.orderPrices} onCreate={this.resetState} /> : ""}
                <AthletePriceChart athleteId={athlete.pk} />
                <AthleteResultList results={this.state.results} />
                <OrderList orders={this.state.orders} userDetails={this.state.orderPrices} />
                <TradeList trades={this.state.trades} />
            </div>;
        } else {
            return <div><h3>Unknown athlete</h3></div>;
        }

    }
}

export default withRouter(AthleteDetail)