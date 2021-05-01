import React, {Component} from 'react';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import {Link} from 'react-router-dom';

class ResultList extends Component {
  render() {
    const results = this.props.results;
    return (
      <div>
        {!results || results.length <= 0 ? (
                <b>No results found</b>
          ) : (
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Pos</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Time</TableCell>
                  <TableCell>Dividend</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>

                {results.map((result, index) => (
                  <TableRow key={result.pk}>
                    <TableCell>{index+1}</TableCell>
                    <TableCell><Link to={'/athletes/' + result.athlete.pk + '/'}>{result.athlete.name}</Link></TableCell>
                    <TableCell>{result.time}</TableCell>
                    <TableCell>
                      {result.dividend && result.dividend>0 ?
                      result.dividend : '' }</TableCell>
                  </TableRow>
                ))}

              </TableBody>
            </Table>

          )}
      </div>
    );
  }
}

export default ResultList;
