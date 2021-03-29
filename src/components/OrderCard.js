import React from 'react';
import {makeStyles, useTheme} from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';

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

export default function OrderCard({order}) {
  const classes = useStyles();
  const theme = useTheme();

  return (
    <Card className={classes.root} key={athlete.pk}>

      <div className={classes.details}>
        <CardContent className={classes.content} style={{paddingBottom: 0}}>
          <div className={classes.name}>
            <Typography component="h6" variant="h6">
              {athlete.name}
            </Typography>
          </div>
        </CardContent>
        <div className={classes.change}>
          <CardContent className={classes.content} style={{paddingBottom: 0}}>
            <Typography variant="subtitle1" style={{color: changeColor}}>
              {change}
              {(athlete.percent_change < 0) ? <ArrowDownwardIcon style={{color: changeColor}} /> :
            (athlete.percent_change > 0) ? <ArrowUpwardIcon style={{color: changeColor}} /> : ''}
            </Typography>
          </CardContent>
        </div>

        <div className={classes.value}>
          <CardContent className={classes.content} style={{paddingBottom: 0}}>
            <Typography component="h6" variant="h6">
        ${Number(athlete.value).toFixed(2)}
            </Typography>
          </CardContent>
        </div>


      </div>
    </Card>
  );
}
