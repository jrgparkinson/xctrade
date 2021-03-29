import React, {Component} from 'react';
import {Table} from 'reactstrap';
import {Link} from 'react-router-dom';

class ResultList extends Component {
  render() {
    const results = this.props.results;
    return (
      <div>
        {!results || results.length <= 0 ? (
                <b>No results to display</b>
          ) : (
            <Table>
              <thead>
                <tr>
                  <th>Pos</th>
                  <th>Name</th>
                  <th>Time</th>
                  <th>Dividend</th>
                </tr>
              </thead>
              <tbody>

                {results.map((result, index) => (
                  <tr key={result.pk}>
                    <td>{index+1}</td>
                    <td><Link to={'/athletes/' + result.athlete.pk + '/'}>{result.athlete.name}</Link></td>
                    <td>{result.time}</td>
                    <td>
                      {result.dividend && result.dividend>0 ?
                      result.dividend : '' }</td>
                  </tr>
                ))}

              </tbody>
            </Table>

          )}
      </div>
    );
  }
}

export default ResultList;
