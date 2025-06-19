import { Link } from '@remix-run/react';

// material-ui
import { useTheme } from '@mui/material/styles';
import { Divider, Grid, Stack, Typography, useMediaQuery } from '@mui/material';

// project imports
import Logo from 'ui-component/Logo';
import Footer from 'ui-component/cards/AuthFooter';
import AuthWrapper1 from 'components/authentication/AuthWrapper1';
import AuthCardWrapper from 'components/authentication/AuthCardWrapper';

// assets

// ================================|| AUTH3 - LOGIN ||================================ //

const AccountActivationMessage = () => {
    const theme = useTheme();
    const matchDownSM = useMediaQuery(theme.breakpoints.down('md'));

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
                                                        Account Activation Email Sent
                                                    </Typography>
                                                    <Typography variant="caption" fontSize="16px" textAlign={'center'}>
                                                        Αn account activation email was sent to your registered email address.
                                                    </Typography>
                                                    <Typography variant="caption" fontSize="16px" textAlign={'center'}>
                                                        Please check your inbox and follow the instructions to activate your account.
                                                    </Typography>
                                                    <Typography variant="caption" fontSize="16px" textAlign={'center'}>
                                                        Note that activation link expires after 24 hour.
                                                    </Typography>
                                                    <Typography variant="caption" fontSize="16px" textAlign={'center'}>
                                                        After activation you can{' '}
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
                                                        If you do not receive the email within the next few minutes, please check your spam
                                                        folder or contact our support team at{' '}
                                                        <a href="mailto:planeat_project@iti.gr">planeat_project@iti.gr</a>.
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

export default AccountActivationMessage;
