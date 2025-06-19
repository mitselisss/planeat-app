import { Link } from '@remix-run/react';

// material-ui
import { useTheme } from '@mui/material/styles';
import { Divider, Grid, Stack, Typography, useMediaQuery } from '@mui/material';

// project imports
import Logo from 'ui-component/Logo';
import Footer from 'ui-component/cards/AuthFooter';
import AuthWrapper1 from 'components/authentication/AuthWrapper1';
import AuthLogin from 'components/authentication/auth-forms/AuthLogin';
import AuthCardWrapper from 'components/authentication/AuthCardWrapper';

// assets

// ================================|| AUTH3 - LOGIN ||================================ //

const Policy = () => {
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
                                                <Stack alignItems="center" justifyContent="center" spacing={1}>
                                                    <Typography
                                                        variant="caption"
                                                        fontSize="16px"
                                                        textAlign={matchDownSM ? 'center' : 'inherit'}
                                                    >
                                                        Privacy Policy
                                                    </Typography>
                                                </Stack>
                                            </Grid>
                                        </Grid>
                                    </Grid>
                                    <Grid item xs={12}>
                                        <Typography variant="body2" sx={{ textAlign: 'justify', mb: 2 }}>
                                            This app collects personal and usage data to support the PLAN'EAT project's research objectives.
                                        </Typography>
                                        <Typography variant="body2" sx={{ textAlign: 'justify', mb: 2 }}>
                                            Data collected include your username, email, demographic information, dietary preferences, and
                                            app usage behavior. All data is securely stored on OVH servers located within the European Union
                                            and processed in accordance with the General Data Protection Regulation (GDPR).
                                        </Typography>
                                        <Typography variant="body2" sx={{ textAlign: 'justify', mb: 2 }}>
                                            During the study, data is pseudonymised; at the conclusion of the study, data will be
                                            anonymised. Your data will be kept for 5 years after the end of the project and then securely
                                            deleted.
                                        </Typography>
                                        <Typography variant="body2" sx={{ textAlign: 'justify', mb: 2 }}>
                                            You have the right to access, correct, or request deletion of your data at any time. To exercise
                                            your rights or to withdraw your consent, please contact laz@iti.gr.
                                        </Typography>
                                        <Typography variant="body2" sx={{ textAlign: 'justify' }}>
                                            For more information on how we protect your data, please refer to our full Privacy Policy or
                                            contact us.
                                        </Typography>
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

export default Policy;
