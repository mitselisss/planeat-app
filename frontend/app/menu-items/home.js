// assets
import { IconHome } from '../../node_modules/@tabler/icons-react';

// constant
const icons = {
    IconHome
};

// ==============================|| HOME PAGE ||============================== //

const home = {
    id: 'home',
    // title: 'Home',
    type: 'group',
    children: [
        {
            id: 'home',
            title: 'Home',
            type: 'item',
            url: '/home',
            icon: icons.IconHome,
            breadcrumbs: false
        }
    ]
};

export default home;
