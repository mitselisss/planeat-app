import { Link } from '@remix-run/react';
import { useState, useEffect } from 'react';

// material-ui
import { useTheme } from '@mui/material/styles';
import { Divider, Grid, Stack, Typography, useMediaQuery } from '@mui/material';

// project imports
import Logo from 'ui-component/Logo';
import Footer from 'ui-component/cards/AuthFooter';
import AuthWrapper1 from 'components/authentication/AuthWrapper1';
import AuthCardWrapper from 'components/authentication/AuthCardWrapper';
import { accountActivation } from 'services/api';

import { useParams, useNavigate } from '@remix-run/react';
import axios from 'axios';

// assets

// ================================|| AUTH3 - LOGIN ||================================ //

const AccountActivationPage = () => {
    const theme = useTheme();
    const matchDownSM = useMediaQuery(theme.breakpoints.down('md'));

    const { token } = useParams();
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
            try {
                await accountActivation(token)
            } catch (error) {
                navigate('/pages/activation/accountExpirePage');
            }
        };
        fetchData();
    }, [token]);

    return (
        <AuthWrapper1>
            <Grid container direction="column" justifyContent="flex-end" sx={{ minHeight: '100vh' }}>
                <Grid item xs={12}>
                    <Grid container justifyContent="center" alignItems="center" sx={{ minHeight: 'calc(100vh - 68px)' }}>
                        <Grid item sx={{ m: { xs: 1, sm: 3 }, mb: 0 }}>
                            <AuthCardWrapper>
                                <Grid container spacing={2} alignItems="center" justifyContent="center">
                                    <Grid item sx={{ mb: 3 }}>
                                        <Link to="#">
                                            <Logo />
                                        </Link>
                                    </Grid>
                                    <Grid item xs={12}>
                                        <Grid
                                            container
                                            direction={matchDownSM ? 'column-reverse' : 'row'}
                                            alignItems="center"
                                            justifyContent="center"
                                        >
                                            <Grid item>
                                                <Stack alignItems="center" justifyContent="center" spacing={3}>
                                                    <Typography
                                                        color={theme.palette.success.dark}
                                                        gutterBottom
                                                        variant={matchDownSM ? 'h3' : 'h2'}
                                                    >
                                                        Account Activation Successful
                                                    </Typography>
                                                    <Typography variant="caption" fontSize="16px" textAlign={'center'}>
                                                        Congratulations!
                                                    </Typography>
                                                    <Typography variant="caption" fontSize="16px" textAlign={'center'}>
                                                        Your account has been successfully activated.
                                                    </Typography>
                                                    <Typography variant="caption" fontSize="16px" textAlign={'center'}>
                                                        You can now{' '}
                                                        <Typography
                                                            component={Link}
                                                            to="/pages/login"
                                                            variant="caption"
                                                            fontSize="16px"
                                                            color="primary"
                                                            sx={{ textDecoration: 'none', cursor: 'pointer' }}
                                                        >
                                                            Login
                                                        </Typography>{' '}
                                                        to your account and start using our service.
                                                    </Typography>
                                                    <Typography variant="caption" fontSize="16px" textAlign={'center'}>
                                                        Thank you!
                                                    </Typography>
                                                </Stack>
                                            </Grid>
                                        </Grid>
                                    </Grid>
                                </Grid>
                            </AuthCardWrapper>
                        </Grid>
                    </Grid>
                </Grid>
                <Grid item xs={12}>
                    <Footer />
                </Grid>
            </Grid>
        </AuthWrapper1>
    );
};

export default AccountActivationPage;