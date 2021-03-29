import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import {CardActionArea} from '@material-ui/core';
import {Link} from 'react-router-dom';
import Grid from '@material-ui/core/Grid';
import {green} from '@material-ui/core/colors';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
// import {formatPercentChange } from "../utils/races";

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    margin: theme.spacing(2),
  },
  details: {
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  content: {
    flex: '1 0 auto',
    marginBottom: 0,

  },

  value: {
    display: 'flex',
    alignItems: 'right',
    paddingLeft: theme.spacing(1),
    paddingBottom: theme.spacing(1),
  },

}));

export default function RaceCard({race}) {
  const classes = useStyles();

  const date = new Date(race.time);
  return (
    <Card className={classes.root} key={race.pk}>
      <CardActionArea component={Link} to={'/races/' + race.pk + '/'}>

        <CardContent className={classes.content} style={{paddingBottom: 0}}>
          <Grid container spacing={2}
            direction="row"
            justify="space-between">
            <Grid item xs={8}>
              <Typography variant="h5">
                {race.name}
              </Typography>
            </Grid>
            <Grid item xs={4} style={{textAlign: 'right'}}>
              <Typography variant="subtitle1">
                {race.has_results ?
              'Results' :
              ''}
                <CheckCircleIcon style={{color: green[500],
                  display: race.has_results ? '' : 'none'}}
                />
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="subtitle1">
                {/* {date.toLocaleDateString()}  */}
                {date.toLocaleTimeString()}
              </Typography>
            </Grid>

            <Grid item xs={6} style={{textAlign: 'right'}}>
              <Typography variant="subtitle1">
            Dividend: ${race.min_dividend} - ${race.max_dividend}
              </Typography>
            </Grid>


          </Grid>


        </CardContent>
        {/* <div className={classes.change}>
        <CardContent className={classes.content}  style={{paddingBottom: 0}}>
        <Typography variant="subtitle1" style={{ color: changeColor  }}>
            {change}
            {(race.percent_change < 0) ? <ArrowDownwardIcon style={{ color: changeColor  }} />  :
            (race.percent_change > 0) ? <ArrowUpwardIcon style={{ color: changeColor  }} /> : ""}
          </Typography>
        </CardContent>
        </div> */}

        {/* <div className={classes.value}>
        <CardContent className={classes.content}  style={{paddingBottom: 0}}>
        <Typography variant="subtitle1">
        ${Number(race.value).toFixed(2)}
          </Typography>
          </CardContent>
        </div>
         */}

        {/* </div> */}
      </CardActionArea>
    </Card>
  );
}
