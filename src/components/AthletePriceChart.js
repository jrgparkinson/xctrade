import * as React from 'react';
import Paper from '@material-ui/core/Paper';
import {VictoryLine, VictoryChart, VictoryTheme, VictoryAxis, VictoryBar, VictoryLabel, VictoryLegend} from 'victory';
import Button from '@material-ui/core/Button';
import ButtonGroup from '@material-ui/core/ButtonGroup';
import {withStyles} from '@material-ui/core/styles';
import API from '../utils/api';

const styles = (theme) => ({
  // myCustomClass: {
  //   color: theme.palette.tertiary.dark
  // }
});


class AthletePriceChart extends React.PureComponent {
  constructor(props) {
    super(props);

    console.log('Props:');
    console.log(props);

    this.state = {
      athleteId: props.athleteId,
      trades: [],
      daysRange: 12,
      width: 250,
      height: 250,
    };
  }

  getTrades() {
    API.getTrades(this.state.athleteId).then((res) => this.setState({trades: res.data}));
  }

  componentDidMount() {
    this.getTrades();
    this.setState({
      width: this.container.getBoundingClientRect().width,
    });
  }


  formatDate(t) {
    const d = new Date(t);
    console.log(d);
    if (this.state.daysRange > 30) {
      return d.toLocaleDateString();
    } else {
      const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December',
      ];

      return d.getDate() + ' ' + monthNames[d.getMonth()].substr(0, 3);
    }
    // return d.getUTCDate() + "/" + d.getUTCMonth() + " " + d.getUTCHours() + ":" + d.getUTCMinutes();
  }

  handleClickRange(range) {
    // e.preventDefault();
    // console.log('The link was clicked.');
    // console.log(range);
    this.setState({daysRange: range});
  }


  render() {
    const {theme} = this.props;
    const primary = theme.palette.primary.main;
    const secondary = theme.palette.secondary.main;
    const {trades} = this.state;

    console.log(this.state);

    const msPerDay = 1000 * 60 * 60 * 24;

    // let data = trades;
    const data = []; const volData = [];
    // let trades = [];
    const now = new Date();
    let maxVal = 0;
    let currentVol = {timestamp: null, volume: 0};
    for (let i=0; i < trades.length; i++) {
      const trade = this.state.trades[i];
      const d = new Date(trade.timestamp);
      trade.timestamp = d;
      data.push(trade);

      // Coarse grain volume data
      // console.log(trade.timestamp + ", " + currentVol);
      if (currentVol.timestamp === null) {
        currentVol = {timestamp: trade.timestamp, volume: Number(trade.volume)};
      }

      console.log(trade.timestamp - currentVol.timestamp);
      if ((trade.timestamp - currentVol.timestamp)/(1000*60*60*24) < 1) {
        currentVol.volume += Number(trade.volume);
      } else {
        volData.push(currentVol);
        currentVol = {timestamp: trade.timestamp, volume: Number(trade.volume)};
      }
      console.log(currentVol);

      if (i===trades.length-1) {
        volData.push(currentVol);
      }

      console.log('Include: ' + JSON.stringify(trade));
      maxVal = Number(trade.unit_price) > maxVal ? Number(trade.unit_price) : maxVal;

    }

    if (trades.length > 0) {
      const lastTrade = trades[trades.length-1];
      data.push({timestamp: new Date(),
        unit_price: lastTrade.unit_price});
      maxVal = Number(lastTrade.unit_price) > maxVal ? Number(lastTrade.unit_price) : maxVal;
    }

    console.log("Data: "  + JSON.stringify(data));
    console.log(volData);

    if (trades.length > 0) {

      const domainMaxPrice = maxVal*1.25;

      // Scale volumes
      let maxVol = 0.0;
      if (volData.length > 0) {
        maxVol = volData.sort((a,b)=>b.volume-a.volume)[0].volume;
      }

      //let dataVolScaled = volData.map(x => {timestamp: x.timestamp, volume: x.volume*(0.5*domainMaxPrce/maxVol)});
      volData.forEach((value, index) => {volData[index].volume *=  0.33*domainMaxPrice/maxVol});

      let axisRange = {
        y: [0, domainMaxPrice]
      };
      if (this.state.daysRange > 0) {
        axisRange.x = [new Date() - msPerDay*this.state.daysRange, new Date()];
      }

      return (
        <Paper>
          <div style={{float: 'right', textAlign: 'right', width: '100%', marginBottom: 0}}>
            <ButtonGroup color="primary" aria-label="outlined primary button group">
              <Button onClick={(e) => this.handleClickRange(-1)}>Max</Button>
              <Button onClick={(e) => this.handleClickRange(30)}>Month</Button>
              <Button onClick={(e) => this.handleClickRange(7)}>Week</Button>
            </ButtonGroup></div>

            { data.length > 0 ? (

          <div
            style={{height: 360, width: '100%', padding: 5, marginTop: -10}}
            ref={(c) => this.container = c}
          >
            <VictoryChart
              theme={VictoryTheme.material}
              height={300}
              width={this.state.width}
              domainPadding={{x: 15}}
              domain  ={axisRange}
            >

              <VictoryAxis
                tickCount={4}
                tickFormat={(t) => `${this.formatDate(t)}`}
                label={'Time'}
                axisLabelComponent={<VictoryLabel dy={20} />}
                style={{
                  axisLabel: {fontSize: 20,
                  },
                  tickLabels: {fontSize: 15},
                }}

              />
              <VictoryAxis dependentAxis
                tickCount={4}
                label={'Value'}
                orientation="left"
                axisLabelComponent={<VictoryLabel dy={-25} />}
                // offsetX={70}
                style={{
                  axisLabel: {fontSize: 20,
                  },
                  tickLabels: {fontSize: 15},
                }}
              />


              <VictoryLine
                // interpolation="natural"
                data={data}
                x="timestamp"
                // data accessor for y values
                y="unit_price"
                scale={{x: 'linear', y: 'linear'}}
                // style= {{color: "indigo", }}
                style={{data: {
                  //  stroke: "blue",
                  stroke: primary,
                  strokeWidth: 3, strokeLinecap: 'round'}}}

              />


              <VictoryBar
                style={{data: {
                  // fill: "pink"
                  fill: secondary,
                }}}
                data={volData}
                x="timestamp"
                y="volume"
                // scale={{x: "linear", y: "linear"}}
                standalone={true}
                barWidth={8}
                // bins={bins}
                // domainPadding={{x:50, y:50}}
              />
              <VictoryLegend x={125} y={50}
  	title=""
    centerTitle
    orientation="horizontal"
    gutter={20}
    style={{ border: { stroke: "black" }, title: {fontSize: 20 } }}
    data={[
      { name: "Spot price", symbol: { fill: primary } },
      { name: "Volume", symbol: { fill: secondary } },
    ]}
  />
            </VictoryChart>
          </div>
            ): 
            "No price data found for time range"
  }</Paper>
      );
    } else {
      return <Paper style={{height: 250, width: '100%'}}
        ref={(c) => this.container = c}>
          No price data found.
      </Paper>;
    }
  }
}

// export default withStyles(demoStyles, { name: 'AthletePriceChart' })(AthletePriceChart);
export default withStyles(styles, {withTheme: true})(AthletePriceChart);
