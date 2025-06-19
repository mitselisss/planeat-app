import { useState, useEffect } from 'react';

// material-ui
import { Grid, Typography } from '@mui/material';

// project imports
import ShoppingList from 'components/shoppingList/shoppingList';
import History from 'components/shoppingList/ingredients';
import { getDecodedToken } from 'utils/tokenUtils';
import { useNavigate } from '@remix-run/react';
import LogoutAfterInactivity from 'utils/logoutAfterInactivity';
import Ingredients from 'components/shoppingList/ingredients';
import MainCard from 'ui-component/cards/MainCard';
import { userActions } from 'services/api';

import { useTheme, styled } from '@mui/material/styles';

// ==============================|| SAMPLE PAGE ||============================== //

const SamplePage = () => {
    const decodedToken = getDecodedToken();
    const navigate = useNavigate();
    const [deleteFlag, setDeleteFlag] = useState(false);
    const [isLoading, setLoading] = useState(true);
    const [isFetchingData, setIsFetchingData] = useState(false);
    const theme = useTheme();

    useEffect(() => {
        const trackLogin = async () => {
            if (!decodedToken || Object.keys(decodedToken).length === 0) {
                navigate('/pages/login');
            } else {
                try {
                    await userActions(decodedToken.user_id, 'shopping-list');
                } catch (error) {
                    console.log(error.response?.data?.error || 'An unexpected error occurred');
                }
            }
        };

        trackLogin();
        setLoading(false);
    }, []);
    LogoutAfterInactivity();

    return (
        <MainCard sx={{ backgroundColor: theme.palette.success.light }}>
            <Grid container spacing={2}>
                <Grid item xs={12}>
                    <Grid container spacing={2}>
                        <Grid item xs={12} md={5}>
                            <ShoppingList
                                isLoading={isLoading}
                                isFetchingData={isFetchingData}
                                setIsFetchingData={setIsFetchingData}
                                setDeleteFlag={setDeleteFlag}
                            />
                        </Grid>
                        <Grid item xs={12} md={7}>
                            <Ingredients
                                isLoading={isLoading}
                                isFetchingData={isFetchingData}
                                setIsFetchingData={setIsFetchingData}
                                deleteFlag={deleteFlag}
                                setDeleteFlag={setDeleteFlag}
                            />
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
        </MainCard>
    );
};

export default SamplePage;
