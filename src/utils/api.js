import axios from 'axios';
import {API_URL} from '../constants';

class Api {

    constructor() { }

    getAxios() {
        return axios.create({
            headers: {
                common: {
                Authorization: 'Token ' + localStorage.getItem('token')
                }
            }
          })
    }

    getAthletes() {
        return this.getAxios().get(API_URL + "athletes/");
    }
    getOrders() {
        return this.getAxios().get(API_URL + "orders/");
    }
}

let API = new Api();

export default API;