import React, {Component} from 'react';
import {Table} from 'reactstrap';
import {Link} from 'react-router-dom';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';

class AthleteResultList extends Component {
  render() {
    const results = this.props.results;
    return (
      <Card style={{marginTop:10}}>
      <CardContent>
        <h4>Results</h4>
        {!results || results.length <= 0 ? (
                <b>No results to display</b>
          ) : (
            <Table>
              <thead>
                <tr>
                  <th>Race</th>
                  <th>Pos</th>
                  <th>Dividend</th>
                </tr>
              </thead>
              <tbody>

                {results.map((result, index) => (
                  <tr key={result.pk}>
                    <td><Link to={'/races/' + result.race.pk + '/'}>{result.race.name}</Link></td>
                    <td>{result.position}</td>
                    <td>
                      {result.dividend && result.dividend>0 ?
                      result.dividend : '' }</td>
                  </tr>
                ))}

              </tbody>
            </Table>

          )}
      </CardContent></Card>
    );
  }
}

export default AthleteResultList;
