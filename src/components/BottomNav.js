import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import BottomNavigation from '@material-ui/core/BottomNavigation';
import BottomNavigationAction from '@material-ui/core/BottomNavigationAction';
import {NavLink} from 'react-router-dom';
import {getNavLinks, breakpointSize} from '../utils/links';

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
    position: 'fixed',
    bottom: 0,
    zIndex: 1100,
    [theme.breakpoints.up(breakpointSize)]: {
      display: 'none',
    },
  },
}));

export default function BottomNav({hasAuction}) {
  const classes = useStyles();

  return (
    <BottomNavigation
      showLabels
      className={classes.root}
    >
      {getNavLinks(hasAuction).map((link, index) => (
        <BottomNavigationAction component={NavLink} to={'/' + link.link}
          label={link.text} icon={link.icon}
          activeClassName="Mui-selected"
          key={index} />
      ))}
    </BottomNavigation>
  );
}
