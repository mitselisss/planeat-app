import { useEffect, useState } from 'react';
import { IconShoppingCart } from '../../../../../node_modules/@tabler/icons-react';
import { IconButton, Badge } from '@mui/material';
import { useNavigate } from '@remix-run/react';
import { styled, useTheme } from '@mui/material/styles';
import { getDecodedToken } from 'utils/tokenUtils';
import { getCurrentDayAndWeekDates } from 'utils/getCurrentDayAndWeekDates';
import { getShoppingList } from 'services/api';

const ShoppingList = () => {
    const navigate = useNavigate();
    const theme = useTheme();
    const decodedToken = getDecodedToken();
    const [shoppingList, setShoppingList] = useState();

    useEffect(() => {
        // window.addEventListener('shoppingListUpdated', setShoppingList(localStorage.getItem('shoppingListItems')));
        setShoppingList(localStorage.getItem('shoppingListItems'));
    }, []);

    return (
        <IconButton>
            <Badge badgeContent={shoppingList ? shoppingList : ''} color="success">
                <IconShoppingCart
                    onClick={() => {
                        navigate('/shopping-list');
                    }}
                />
            </Badge>
        </IconButton>
    );
};

export default ShoppingList;
