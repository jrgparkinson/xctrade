import React, { Component } from "react";
import { Container } from "reactstrap";
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import API from '../utils/api';
import {Link} from 'react-router-dom';
import EditIcon from '@material-ui/icons/Edit';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import Paper from '@material-ui/core/Paper';

class Portfolio extends Component {
  state = {
    profile: {},
    shares: [],
    dividends: [],
    editingName: false
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

  editName = (e) => {
    this.setState({editingName: true});
  }

  changeName = (e) => {
    let p = this.state.profile

    p.name = e.target.value;
    this.setState({profile: p});
  }

  saveProfile = (e) => {
    API.saveProfile({name: this.state.profile.name}).then(res => this.setState({ profile: this.state.profile }));
    this.setState({editingName: false});
  }

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
    // console.log(shares);

    let apiKey = API.getKey();

    let sharesValue = Number(profile.portfolio_value - profile.capital).toFixed(2);
    return (
      <Container>
        {this.state.editingName ? 
        <div style={{
          display: "inline-flex",
          verticalAlign: "middle"}}>
        <TextField id="name" label="Name" size="small" value={this.state.profile.name} variant="outlined" 
        onChange={this.changeName}/>
        <Button variant="contained" color="primary" onClick={this.saveProfile}
        style={{marginLeft:5}}>
  Save
  </Button></div>
         :
          <h1>{profile.name}<EditIcon onClick={this.editName} style={{marginLeft:10}}/></h1>}
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
        <TableHead>
          <TableRow>
            <TableCell>Athlete</TableCell>
            <TableCell>Volume</TableCell>
            <TableCell>Value (per share)</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {!shares || shares.length === 0 ? (
            <TableRow>
              <TableCell colSpan="6" align="center">
                None
              </TableCell>
            </TableRow>
          ) : (
            shares.map((share, index) => (
              <TableRow key={share.pk}>
                <TableCell><Link to={'/athletes/' + share.athlete.pk + '/'}>{share.athlete.name}</Link></TableCell>
                <TableCell>{share.volume}</TableCell>
                <TableCell>{share.volume*share.athlete.value} ({share.athlete.value})</TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
      </CardContent>
      </Card>

      <Card style={{marginTop:10}}>
      <CardContent>
      <h4>Dividends Received</h4>
        <Table>
        <TableHead>
          <TableRow>
            <TableCell>Race</TableCell>
            <TableCell>Athlete</TableCell>
            <TableCell>Vol</TableCell>
            <TableCell>Dividend</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {!dividends || dividends.length === 0 ? (
            <TableRow>
              <TableCell colSpan="6" align="center">
                None
              </TableCell>
            </TableRow>
          ) : (
            dividends.map((dividend, index) => (
              <TableRow key={dividend.pk}>
                <TableCell><Link to={'/athletes/' + dividend.result.race.pk + '/'}>{dividend.result.race.name}</Link></TableCell>
                <TableCell><Link to={'/athletes/' + dividend.result.athlete.pk + '/'}>{dividend.result.athlete.name}</Link></TableCell>
                <TableCell>{dividend.volume}</TableCell>
                <TableCell>{dividend.volume*dividend.dividend_per_share}</TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
      </CardContent>
      </Card>


      <Card style={{marginTop:10}}>
      <CardContent>
        <h4>API</h4>
        <p>For the technically minded, you can interact with the underlying API using your personal private API key:</p>
      
        <Paper variant="outlined" style={{padding:10, margin:10}}>{apiKey}</Paper>

      <h6>API documentation: <a href="/redoc/">redoc</a>, <a href="/swagger/">swagger</a></h6>

      <h6>Example</h6>
      <Paper variant="outlined" style={{padding:10, margin:10}}>
      curl -X GET https://xctrade.herokuapp.com/api/athletes/ -H 'Authorization: Token {apiKey}'
      </Paper>
      </CardContent>
      </Card>
      </Container>
    );
  }
}

export default Portfolio;
