// assets
import {
    IconSoup,
    IconTrophy,
    IconShoppingCart,
    IconShoppingBag,
    IconBrandGoogleAnalytics,
    IconInfoCircle
} from '../../node_modules/@tabler/icons-react';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import Badge from '@mui/material/Badge';

// constant
// const icons = {
//     IconSoup,
//     IconTrophy,
//     IconShoppingBag,
//     IconBrandGoogleAnalytics,
//     IconInfoCircle
// };

// ==============================|| SAMPLE PAGE & DOCUMENTATION MENU ITEMS ||============================== //

const planEatMenu = {
    id: 'planEat',
    title: 'Menu',
    type: 'group',
    children: [
        {
            id: 'meal-plan',
            title: 'Meal Plan',
            type: 'item',
            url: '/meal-plan',
            icon: IconSoup,
            breadcrumbs: false
        },
        {
            id: 'achievements',
            title: 'Achievements',
            type: 'item',
            url: '/achievements',
            icon: IconTrophy,
            breadcrumbs: false
        },
        {
            id: 'shopping-list',
            title: 'Shopping List',
            type: 'item',
            url: '/shopping-list',
            icon: IconShoppingCart,
            breadcrumbs: false
        },
        {
            id: 'Analytics',
            title: 'Analytics',
            type: 'item',
            url: '/analytics',
            icon: IconBrandGoogleAnalytics,
            breadcrumbs: false
        },
        {
            id: 'about',
            title: 'About',
            type: 'item',
            url: '/about',
            icon: IconInfoCircle,
            breadcrumbs: false
        }
    ]
};

export default planEatMenu;
