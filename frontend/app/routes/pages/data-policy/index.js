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
                                                        sx={{ textAlign: 'center' }}
                                                    >
                                                        User Consent for Participation and Data Processing
                                                    </Typography>
                                                </Stack>
                                            </Grid>
                                        </Grid>
                                    </Grid>
                                    <Grid item xs={12}>
                                        <Typography variant="body2" sx={{ textAlign: 'justify', mb: 2 }}>
                                            Thank you for your interest in participating in this research project, part of the PLAN'EAT
                                            project funded by the European Union.
                                        </Typography>
                                        <Typography variant="body2" sx={{ textAlign: 'justify', mb: 2 }}>
                                            By creating an account and using this app, you voluntarily agree to participate in the testing
                                            phase. You consent to the collection and processing of your personal data, including username,
                                            email address, demographic and dietary information, and app usage data, for the purposes of:
                                            Evaluating the app’s usability, functionality, and performance; Supporting the research
                                            objectives of the PLAN'EAT project.
                                        </Typography>
                                        <Typography variant="body2" sx={{ textAlign: 'justify', mb: 2 }}>
                                            Your data will be stored securely on OVH servers located in the EU, and will only be accessible
                                            to authorized personnel from the Centre for Research and Technology Hellas (CERTH).
                                        </Typography>
                                        <Typography variant="body2" sx={{ textAlign: 'justify', mb: 2 }}>
                                            During the study, your data will be pseudonymised (linked only to your username and email), and
                                            at the end of the study, your data will be fully anonymised. No personal identifiers will be
                                            retained after anonymisation.
                                        </Typography>
                                        <Typography variant="body2" sx={{ textAlign: 'justify', mb: 2 }}>
                                            Your participation is voluntary, and you may withdraw your consent and request deletion of your
                                            data at any time without penalty. Data will be securely stored for 5 years following the end of
                                            the PLAN'EAT project and will then be destroyed.
                                        </Typography>
                                        <Typography variant="body2" sx={{ textAlign: 'justify' }}>
                                            For more detailed information about how your data is processed, please read our{' '}
                                            <Link to="/pages/privacy-policy" target="_blank" rel="noopener">
                                                Privacy Policy
                                            </Link>{' '}
                                            .
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
