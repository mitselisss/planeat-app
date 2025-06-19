import { useState, useEffect } from 'react';

// material-ui
import { Grid, Box, Typography } from '@mui/material';

// project imports
import MainCard from 'ui-component/cards/MainCard';
import { getDecodedToken } from 'utils/tokenUtils';
import { useNavigate } from '@remix-run/react';
import LogoutAfterInactivity from 'utils/logoutAfterInactivity';

// material-ui
import { useTheme, styled } from '@mui/material/styles';

// ==============================|| SAMPLE PAGE ||============================== //

// styles
const CardWrapper = styled(MainCard)(({ theme }) => ({
    overflow: 'hidden',
    position: 'relative',
    '&:after': {
        content: '""',
        position: 'absolute',
        width: 210,
        height: 210,
        background: `linear-gradient(210.04deg, ${theme.palette.success.light} -50.94%, rgba(144, 202, 249, 0) 83.49%)`,
        borderRadius: '50%',
        top: -30,
        right: -180
    },
    '&:before': {
        content: '""',
        position: 'absolute',
        width: 210,
        height: 210,
        background: `linear-gradient(140.9deg, ${theme.palette.success.light} -14.02%, rgba(144, 202, 249, 0) 70.50%)`,
        borderRadius: '50%',
        top: -160,
        right: -130
    }
}));

const Home = () => {
    const decodedToken = getDecodedToken();
    const navigate = useNavigate();
    const theme = useTheme();

    useEffect(() => {
        if (!decodedToken || Object.keys(decodedToken).length === 0) {
            navigate('/pages/login');
        }
    }, []);
    LogoutAfterInactivity();

    return (
        <MainCard sx={{ backgroundColor: theme.palette.success.light }}>
            <Grid container spacing={2}>
                <Grid item xs={12}>
                    <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                            <CardWrapper></CardWrapper>
                            <Box my={2} />
                            <CardWrapper></CardWrapper>
                            <Box my={2} />
                            <CardWrapper></CardWrapper>
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <CardWrapper></CardWrapper>
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
        </MainCard>
    );
};

export default Home;
