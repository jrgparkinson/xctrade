import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import {CardActionArea} from '@material-ui/core';
import {Link} from 'react-router-dom';
import ArrowUpwardIcon from '@material-ui/icons/ArrowUpward';
import ArrowDownwardIcon from '@material-ui/icons/ArrowDownward';
import {formatPercentChange} from '../utils/athletes';
import EqualizerIcon from '@material-ui/icons/Equalizer';
import Tooltip from '@material-ui/core/Tooltip';


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

export default function AthleteCard({athlete}) {
  const classes = useStyles();
  // const theme = useTheme();

  // var change = athlete.percent_change;
  // let changeColor = "red";
  // if (change == null) { change = "N/A"; }
  // else {
  //   change = Number(change).toFixed(0);
  //   if (change >= 0) { change = "+" + change;
  //   changeColor="green"; }
  //   change = change + "%";
  // }

  const {change, changeColor} = formatPercentChange(athlete.percent_change);

  return (
    <Card className={classes.root} key={athlete.pk}>
      <CardActionArea component={Link} to={'/athletes/' + athlete.pk + '/'}>
        <div className={classes.details}>
          <CardContent className={classes.content} style={{paddingBottom: 0}}>
            <div className={classes.name}>
              <Typography variant="subtitle1">
                {athlete.name}
              </Typography>
            </div>
          </CardContent>
          <div className={classes.change}>
            <CardContent className={classes.content} style={{paddingBottom: 0}}>
            <Tooltip title="7-day change">
                   
              <Typography variant="subtitle1" style={{color: changeColor}}>
                {change}
                {(athlete.percent_change < 0) ? <ArrowDownwardIcon style={{color: changeColor}} /> :
            (athlete.percent_change > 0) ? <ArrowUpwardIcon style={{color: changeColor}} /> : ''}
              </Typography>
              </Tooltip>
            </CardContent>
          </div>

          <div className={classes.value}>
            <CardContent className={classes.content} style={{paddingBottom: 0}}>
              <Typography variant="subtitle1">
              <Tooltip title="Value">
                <span>${Number(athlete.value).toFixed(2)}
                </span>
                </Tooltip>
                / <Tooltip title="7-day volume">
                <span><EqualizerIcon />{athlete.weekly_volume}
                </span>
                </Tooltip>
              </Typography>
            </CardContent>
          </div>


        </div>
      </CardActionArea>
    </Card>
  );
}
