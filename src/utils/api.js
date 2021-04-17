import axios from 'axios';
import {API_URL} from '../constants';

class Api {
  // constructor() { }

  getKey() {
    return localStorage.getItem('token');
  }

  isAuthorised() {
    return localStorage.getItem('token') !== 'null';
  }

  getAxios() {
    if (this.isAuthorised()) {
      return axios.create({
        headers: {
          common: {
            Authorization: 'Token ' + localStorage.getItem('token'),
          },
        },
      });
    } else {
      return axios.create();
    }
  }

  getAthletes() {
    return this.getAxios().get(API_URL + 'athletes/');
  }
  getResultsForAthlete(id) {
    return this.getAxios().get(API_URL + 'results/?athlete_id=' + id);
  }
  getRaces() {
    return this.getAxios().get(API_URL + 'races/');
  }
  getRace(pk) {
    return this.getAxios().get(API_URL + 'races/' + pk + '/');
  }
  getProfile() {
    return this.getAxios().get(API_URL + 'profile/');
  }
  saveProfile(data) {
    return this.getAxios().put(API_URL + 'profile/', data);
  }
  getDividends() {
    return this.getAxios().get(API_URL + 'dividends/');
  }
  getEntities() {
    return this.getAxios().get(API_URL + 'entities/');
  }
  getShares() {
    return this.getAxios().get(API_URL + 'shares/');
  }
  getAthlete(id) {
    return this.getAxios().get(API_URL + 'athletes/' + id + '/');
  }
  getOrders() {
    return this.getAxios().get(API_URL + 'orders/');
  }
  getAuction() {
    return this.getAxios().get(API_URL + 'auction/');
  }
  getAuctionShares() {
    return this.getAxios().get(API_URL + 'auction_shares/');
  }
  getBids(auction_id) {
    return this.getAxios().get(API_URL + 'bids/' + auction_id + '/');
  }
  postBids(auction_id, data) {
    return this.getAxios().post(API_URL + 'bids/' + auction_id + '/', data);
  }
  getOrdersForAthlete(athleteId) {
    return this.getAxios().get(API_URL + 'orders/?athlete_id=' + athleteId);
  }
  getTrades(athleteId) {
    return this.getAxios().get(API_URL + 'trades/?athlete_id=' + athleteId);
  }
  getAtheletePriceDetails(athleteId) {
    return this.getAxios().get(API_URL + 'order_prices/' + athleteId + '/');
  }
  postOrder(order) {
    return this.getAxios().post(API_URL + 'orders/', order);
  }
  getLoans() {
    return this.getAxios().get(API_URL + 'loans/');
  }
  getLoanInfo() {
    return this.getAxios().get(API_URL + 'loan_info/');
  }
  updateLoan(loan_id, data) {
    return this.getAxios().put(API_URL + 'loans/' + loan_id + "/", data);
  }
  createLoan(data) {
    return this.getAxios().post(API_URL + 'loans/', data);
  }
  cancelOrder(pk) {
    return this.getAxios().put(API_URL + 'orders/' + pk + '/', {
      'status': 'C',
    });
  }
}

const API = new Api();

export default API;
