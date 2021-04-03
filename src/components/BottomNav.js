import { Link } from 'react-router-dom';

import BottomNavigation from '@material-ui/core/BottomNavigation';
import BottomNavigationAction from '@material-ui/core/BottomNavigationAction';

export default function Header() {
  return (

<BottomNavigation value={value} onChange={this.handleChange}>
    <BottomNavigationAction
        component={Link}
        to="/Athletes"
        label="Athletes"
        value="Athletes"
    />
<BottomNavigationAction
        component={Link}
        to="/Orders"
        label="Orders"
        value="Orders"
        
    />
</BottomNavigation>
);
}
