import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import BottomNavigation from '@material-ui/core/BottomNavigation';
import BottomNavigationAction from '@material-ui/core/BottomNavigationAction';
import RestoreIcon from '@material-ui/icons/Restore';
import DirectionsRunIcon from '@material-ui/icons/DirectionsRun';
import FormatListNumberedIcon from '@material-ui/icons/FormatListNumbered';
import LocationOnIcon from '@material-ui/icons/LocationOn';
import MonetizationOnIcon from '@material-ui/icons/MonetizationOn';
import SyncAltIcon from '@material-ui/icons/SyncAlt';
import { Link, NavLink } from 'react-router-dom';
import TrendingUpIcon from '@material-ui/icons/TrendingUp';

const useStyles = makeStyles({
  root: {
    width: '100%',
    position: 'fixed',
    bottom: 0,
  },
});

export default function BottomNav() {
  const classes = useStyles();
  const [value, setValue] = React.useState(0);

  return (
    <BottomNavigation
      value={value}
      onChange={(event, newValue) => {
        setValue(newValue);
      }}
      showLabels
      className={classes.root}
    >
      <BottomNavigationAction component={NavLink}
        to="/Athletes" label="Trade" icon={<SyncAltIcon />} />
      <BottomNavigationAction component={NavLink}
        to="/Leaderboard" label="Leaderboard" icon={<FormatListNumberedIcon />} />
      <BottomNavigationAction component={Link}
        to="/Profile" label="Portfolio" icon={<TrendingUpIcon />} />
<BottomNavigationAction component={Link}
        to="/Races" label="Races" icon={<DirectionsRunIcon />} />
    </BottomNavigation>
  );
}
