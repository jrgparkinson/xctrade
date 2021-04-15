import React, { Component } from "react";
import { Container } from "reactstrap";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';

class About extends Component {

  render() {
    return (
      <Container>
          <h1>About</h1>
          
      <Card style={{marginTop:10}}>
      <CardContent>
      <h5>This is a fantasy trading game.</h5>
      
      <p>Like normal "fantasy cross country", 
      the aim is to pick the best runners and accumulate the most points (or here, money) over a season.
      However here, you are not fixed into your initial choices - you can buy/sell a stake in any athlete at any
      time (as long as you offer a price that someone else is willing to match).</p>

      <p> Athletes earn their shareholders dividends based on race results, and at the end of the season
      the player with the most money wins. </p>

      <p>For more details, check out (and feel free to contribute to) the <a href="https://github.com/jrgparkinson/xctrade/wiki" target="_blank" rel="noreferrer">wiki page.</a></p>

      <p><b>Found a bug or have an idea for an improvement?</b> <a href="https://github.com/jrgparkinson/xctrade/issues" target="_blank" rel="noreferrer">Please add it here</a></p>
      </CardContent>
      </Card>
      </Container>
    );
  }
}

export default About;
