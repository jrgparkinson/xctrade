import React, { Component } from "react";
import { Container } from "reactstrap";
// import Card from '@material-ui/core/Card';
// import CardContent from '@material-ui/core/CardContent';
import API from '../utils/api';
import { Table } from "reactstrap";
import AuctionAthleteBid from "./AuctionAthleteBid";
import Button from '@material-ui/core/Button';
import Alert from '@material-ui/lab/Alert';
import Snackbar from '@material-ui/core/Snackbar';
import Grid from '@material-ui/core/Grid';

class Auction extends Component {
  state = {
    auction: null,
    bids: [],
    shares: [],
    openSnackbarError: false,
    openSnackbarSuccess: false,
    noChanges: true,
  };

  handleCloseSnackbarError = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    this.setState({openSnackbarError: false});
  };
  handleCloseSnackbarSuccess = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    this.setState({openSnackbarSuccess: false});
  };

  componentDidMount() {
    this.resetState();
  }

  resetState = () => {
    API.getAuction().then(res => {
      let auction = res.data;
      console.log("Auction: " + JSON.stringify(auction));
      if (auction == null) {
        this.setState({ auction: auction });
      } else {
        console.log("Get bids and shares for auction");
        API.getBids(auction.pk).then(res => {
          let bids = res.data;
          API.getAuctionShares().then(res => this.setState({ bids:bids, auction:auction, shares: res.data }));
        });
      }
    });
  };

  getBid = (athlete_pk) => {
    let bid = this.state.bids.find(bid => bid.athlete === athlete_pk);
    return bid;
  }

  saveBids = () => {
    let bids = this.state.bids.map(function(bid) { 
      bid.volume = Number(Number(bid.volume).toFixed(2));
      bid.price_per_volume = Number(Number(bid.price_per_volume).toFixed(2));
      return bid;
    });

    console.log("Save bids: " + JSON.stringify(bids));
    // console.log(this.state.bids);

    API.postBids(this.state.auction.pk, bids).then(res => {
      console.log("Saved: " + JSON.stringify(res));
      this.setState({openSnackbarSuccess: true, noChanges: true});
    }).catch(err => {
      console.log("Error: " + JSON.stringify(err));
      this.setState({openSnackbarError: true});
    });

  }

  updateBid = (bid) => {
    console.log("Update bid: " + JSON.stringify(bid));

    let bids = this.state.bids;
    let oldBid = bids.find(b => b.athlete === bid.athlete);
    if (oldBid === undefined) {
      bids.push({
        athlete: bid.athlete,
        auction: this.state.auction.pk,
        volume: bid.volume,
        price_per_volume: bid.price_per_volume
      });
    } else {
      oldBid.volume = bid.volume;
      oldBid.price_per_volume = bid.price_per_volume;
    }
    this.setState({bids: bids, noChanges: false})
  }


  render() {
    console.log(this.state.auction);
    console.log(this.state.bids);
    console.log(this.state.shares);


    if (this.state.auction === null) {
      return (
        <Container>
            <h1>No auction happening</h1>
        </Container>
      );
    }

    return (
      <Container style={{margin:0, padding:0}}>
<Grid container spacing={2}
                direction="row"
                justify="space-between">
                <Grid item xs={12}>
          <h1>{this.state.auction.name}</h1></Grid>
          <Grid item xs={12}>
          {this.state.auction.description}</Grid>
          <Grid item xs={5} sm={4}>Auction closes: </Grid>
          <Grid item xs={7} sm={4}><h6>{new Date(this.state.auction.end_date).toLocaleString()}</h6></Grid>
          <Grid item xs={12} sm={4} style={{textAlign: "center"}}>
          <Button variant="contained" color="primary" onClick={this.saveBids}
        disabled={this.state.noChanges} 
        style={{
          marginBottom:10
        }}>
  Save bids
  </Button> </Grid>

          </Grid>
      

      <Table
      //  style={{marginLeft:-10,
      // width: "102%"}}
      >
        <thead>
          <tr>
            <th>Athlete (Available)

            {/* </th>
            <th> */}
              </th>
            {/* <th>Bid volume</th>
            <th>Bid unit price</th> */}
            <th>Bid</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          {!this.state.shares || this.state.shares.length <= 0 ? (
            <tr>
              <td colSpan="6" align="center">
                <b>Ops, no one here yet</b>
              </td>
            </tr>
          ) : (
            this.state.shares.map(share => (
              <AuctionAthleteBid key={share.pk} share={share} bid={this.getBid(share.athlete.pk)}
              updateBid={this.updateBid} />
            ))
          )}
        </tbody>
      </Table>

        

     

      <Snackbar open={this.state.openSnackbarError} autoHideDuration={6000} onClose={this.handleCloseSnackbarError}>
        <Alert onClose={this.handleCloseSnackbarError} severity="error">
          Error saving bids
        </Alert>
      </Snackbar>
      <Snackbar open={this.state.openSnackbarSuccess} autoHideDuration={6000} onClose={this.handleCloseSnackbarSuccess}>
        <Alert onClose={this.handleCloseSnackbarSuccess} severity="success">
          Bids saved successfully
        </Alert>
      </Snackbar>

      </Container>
    );
  }
}

export default Auction;
