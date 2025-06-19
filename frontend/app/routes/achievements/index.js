import { useState, useEffect } from 'react';

// material-ui
import { Grid, Box, Typography } from '@mui/material';

// project imports
import Main from 'components/achievments/scoring/main';
import LevelCard from 'components/achievments/levelCard';

import { getDecodedToken } from 'utils/tokenUtils';
import { useNavigate } from '@remix-run/react';
import LogoutAfterInactivity from 'utils/logoutAfterInactivity';
import CurrentState from 'components/achievments/currentState';
import MainCard from 'ui-component/cards/MainCard';
import { userActions } from 'services/api';

import { useTheme, styled } from '@mui/material/styles';

// ==============================|| SAMPLE PAGE ||============================== //

const SamplePage = () => {
    const decodedToken = getDecodedToken();
    const navigate = useNavigate();
    const theme = useTheme();

    useEffect(() => {
        const trackLogin = async () => {
            if (!decodedToken || Object.keys(decodedToken).length === 0) {
                navigate('/pages/login');
            } else {
                try {
                    await userActions(decodedToken.user_id, 'achievments');
                } catch (error) {
                    console.log(error.response?.data?.error || 'An unexpected error occurred');
                }
            }
        };

        trackLogin();
    }, []);
    LogoutAfterInactivity();

    return (
        <Grid container spacing={2}>
            <Grid item xs={12}>
                {/* <Box mb={2}>
                    <Typography
                        variant="body2"
                        color={theme.palette.error.dark}
                        sx={{
                            backgroundColor: 'white',
                            padding: '8px 16px',
                            borderRadius: '8px',
                            textAlign: 'center'
                        }}
                    >
                        ⚠️ This page is for demonstration purposes only. Full functionality will be included in future versions.
                    </Typography>
                </Box> */}

                <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                        <MainCard sx={{ backgroundColor: theme.palette.success.light }}>
                            <CurrentState />
                            <Box my={2} />
                            <LevelCard />
                        </MainCard>
                    </Grid>

                    <Grid item xs={12} md={6}>
                        <Main />
                    </Grid>
                </Grid>
            </Grid>
        </Grid>
    );
};

export default SamplePage;
