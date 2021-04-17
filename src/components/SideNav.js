import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import Drawer from '@material-ui/core/Drawer';
import Toolbar from '@material-ui/core/Toolbar';
import List from '@material-ui/core/List';
import {NavLink} from 'react-router-dom';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import {ListItemIcon} from '@material-ui/core';
import {getNavLinks, drawerWidth, breakpointSize} from '../utils/links';

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
  },
  drawer: {
    // width: drawerWidth,
    // flexShrink: 0,
    // [theme.breakpoints.down('xs')]: {
    //   width: 0,
    //   display: 'none',
    // },
      width: 0,
      display: 'none',
      flexShrink: 0,
    [theme.breakpoints.up(breakpointSize)]: {
      width: drawerWidth,
      display: 'inline',
    },
  },
  drawerPaper: {
    width: drawerWidth,
  },
  drawerContainer: {
    overflow: 'auto',
  },
  content: {
    flexGrow: 1,
    padding: theme.spacing(3),
  },
}));

export default function SideNav({hasAuction}) {
  const classes = useStyles();

  return (

    <Drawer
      className={classes.drawer}
      variant="permanent"
      classes={{
        paper: classes.drawerPaper,
      }}
    >
      <Toolbar />
      <div className={classes.drawerContainer}>
        <List>
          {getNavLinks(hasAuction).map((link, index) => (
            <ListItem button key={link.text} component={NavLink}
              activeClassName="Mui-selected"
              to={'/' + link.link}>
              <ListItemIcon>{link.icon}</ListItemIcon>
              <ListItemText primary={link.text} />
            </ListItem>
          ))}
        </List>
      </div>
    </Drawer>
  );
}
