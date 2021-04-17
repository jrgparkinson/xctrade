import React, {Component} from 'react';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
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
              <TableHead>
                <TableRow>
                  <TableCell>Race</TableCell>
                  <TableCell>Pos</TableCell>
                  <TableCell>Dividend</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>

                {results.map((result, index) => (
                  <TableRow key={result.pk}>
                    <TableCell><Link to={'/races/' + result.race.pk + '/'}>{result.race.name}</Link></TableCell>
                    <TableCell>{result.position}</TableCell>
                    <TableCell>
                      {result.dividend && result.dividend>0 ?
                      result.dividend : '' }</TableCell>
                  </TableRow>
                ))}

              </TableBody>
            </Table>

          )}
      </CardContent></Card>
    );
  }
}

export default AthleteResultList;
