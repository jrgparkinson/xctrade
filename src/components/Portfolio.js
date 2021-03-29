import React, { Component } from "react";
import { Container } from "reactstrap";
import { Table } from "reactstrap";
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import API from '../utils/api';
import {Link} from 'react-router-dom';

class Portfolio extends Component {
  state = {
    profile: {},
    shares: [],
    dividends: []
  };

  componentDidMount() {
    this.resetState();
  }

  getProfile = () => {
    API.getProfile().then(res => this.setState({ profile: res.data }));
  };

  resetState = () => {
    this.getProfile();
    API.getShares().then(res => this.setState({ shares: res.data }));
    API.getDividends().then(res => this.setState({ dividends: res.data }));
  };

  render() {
    if (!API.isAuthorised()) {
        return (
            <Container>Not logged in</Container>
        );
    }


    console.log(this.state.profile);
    let profile = this.state.profile;
    let shares = this.state.shares;
    let dividends = this.state.dividends;
    console.log(shares);

    let apiKey = API.getKey();

    let sharesValue = Number(profile.portfolio_value - profile.capital).toFixed(2);
    return (
      <Container>
          <h1>{profile.name}</h1>
          <Card style={{marginTop:10}}>
      <CardContent>
        <h2>Portfolio value: {profile.portfolio_value}</h2>
        <h4>Cash: {profile.capital} / Shares {sharesValue}</h4>
        </CardContent>
        </Card>
        <Card style={{marginTop:10}}>
      <CardContent>
      <h4>Shares owned</h4>
        <Table>
        <thead>
          <tr>
            <th>Athlete</th>
            <th>Volume</th>
            <th>Value (per share)</th>
          </tr>
        </thead>
        <tbody>
          {!shares || shares.length === 0 ? (
            <tr>
              <td colSpan="6" align="center">
                None
              </td>
            </tr>
          ) : (
            shares.map((share, index) => (
              <tr key={share.pk}>
                <td><Link to={'/athletes/' + share.athlete.pk + '/'}>{share.athlete.name}</Link></td>
                
                <td>{share.volume}</td>
                <td>{share.volume*share.athlete.value} ({share.athlete.value})</td>
              </tr>
            ))
          )}
        </tbody>
      </Table>
      </CardContent>
      </Card>

      <Card style={{marginTop:10}}>
      <CardContent>
      <h4>Dividends Received</h4>
        <Table>
        <thead>
          <tr>
            <th>Race</th>
            <th>Athlete</th>
            <th>Vol</th>
            <th>Dividend</th>
          </tr>
        </thead>
        <tbody>
          {!dividends || dividends.length === 0 ? (
            <tr>
              <td colSpan="6" align="center">
                None
              </td>
            </tr>
          ) : (
            dividends.map((dividend, index) => (
              <tr key={dividend.pk}>
                <td><Link to={'/athletes/' + dividend.result.race.pk + '/'}>{dividend.result.race.name}</Link></td>
                <td><Link to={'/athletes/' + dividend.result.athlete.pk + '/'}>{dividend.result.athlete.name}</Link></td>
                <td>{dividend.volume}</td>
                <td>{dividend.volume*dividend.dividend_per_share}</td>
              </tr>
            ))
          )}
        </tbody>
      </Table>
      </CardContent>
      </Card>


      <Card style={{marginTop:10}}>
      <CardContent>
      <b>API key</b> <br />
      {apiKey}
      </CardContent>
      </Card>
      </Container>
    );
  }
}

export default Portfolio;
