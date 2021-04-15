
import DirectionsRunIcon from '@material-ui/icons/DirectionsRun';
import FormatListNumberedIcon from '@material-ui/icons/FormatListNumbered';
import SyncAltIcon from '@material-ui/icons/SyncAlt';
import TrendingUpIcon from '@material-ui/icons/TrendingUp';
import AccountBalanceIcon from '@material-ui/icons/AccountBalance';
import GavelIcon from '@material-ui/icons/Gavel';
import API from '../utils/api';

const navLinks = [
  {text: 'Trade', link: 'Athletes', icon: <SyncAltIcon />, needsLogin: false},
  {text: 'Leaderboard', link: 'Leaderboard', icon: <FormatListNumberedIcon />, needsLogin: false},
  {text: 'Portfolio', link: 'Portfolio', icon: <TrendingUpIcon />, needsLogin: true},
  {text: 'Races', link: 'Races', icon: <DirectionsRunIcon />, needsLogin: false},
  {text: 'Auction', link: 'Auction', icon: <GavelIcon />, needsLogin: true},
];

const bank = {text: 'Bank', link: 'Bank', icon: <AccountBalanceIcon />, needsLogin: true};

export function getNavLinks() {
  let links = navLinks.filter(link => !link.needsLogin || API.isAuthorised());

  if (false) {
    links.push(bank);
  }
  return links;
}

export const drawerWidth = 200;
export const breakpointSize = "md";