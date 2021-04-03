import React, { Component } from "react";
import { Table } from "reactstrap";
// import NewathleteModal from "./NewathleteModal";
// import ConfirmRemovalModal from "./ConfirmRemovalModal";

class AthleteList extends Component {
  render() {
    const athletes = this.props.athletes;
    return (
      <Table dark>
        <thead>
          <tr>
            <th>Name</th>
            
            <th></th>
          </tr>
        </thead>
        <tbody>
          {!athletes || athletes.length <= 0 ? (
            <tr>
              <td colSpan="6" align="center">
                <b>Ops, no one here yet</b>
              </td>
            </tr>
          ) : (
            athletes.map(athlete => (
              <tr key={athlete.pk}>
                <td>{athlete.name}, {athlete.value} +/- {athlete.percent_change}</td>
              </tr>
            ))
          )}
        </tbody>
      </Table>
    );
  }
}

export default AthleteList;