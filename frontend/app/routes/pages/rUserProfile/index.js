import { Link } from '@remix-run/react';
import { useEffect, useState } from 'react';

// material-ui
import { useTheme } from '@mui/material/styles';
import { Divider, Grid, Stack, Typography, useMediaQuery } from '@mui/material';

import LinearProgress, { linearProgressClasses } from '@mui/material/LinearProgress';
import { styled } from '@mui/system';

import { getDecodedToken } from 'utils/tokenUtils';
import { useNavigate } from '@remix-run/react';

// project imports
import AuthWrapper1 from 'components/authentication/AuthWrapper1';
import AuthCardWrapper from 'components/authentication/AuthCardWrapper';
import AuthRegister from 'components/authentication/auth-forms/AuthRegister';
import Logo from 'ui-component/Logo';
import AuthFooter from 'ui-component/cards/AuthFooter';
import ProfileForm1 from 'components/ProfileRegistration/profileForm1';
import ProfileForm2 from 'components/ProfileRegistration/profileForm2';
import LogoutAfterInactivity from 'utils/logoutAfterInactivity';

// assets

// ===============================|| AUTH3 - REGISTER ||=============================== //

const rUserProfile = () => {
    const theme = useTheme();
    const matchDownSM = useMediaQuery(theme.breakpoints.down('md'));
    const decodedToken = getDecodedToken();
    const navigate = useNavigate();

    const [page, setPage] = useState(0);
    const [progressBarState, setProgressBarState] = useState(50);

    const [formData, setFormData] = useState({
        role: '',
        roleStatus: '',
        country: '',
        countryStatus: '',
        sex: '',
        sexStatus: '',
        yob: '',
        yobStatus: '',
        height: '',
        heightStatus: '',
        weight: '',
        weightStatus: '',
        PAL: '',
        palStatus: '',
        target_weight: '',
        target_weight_status: '',
        goal: '',
        targetGoal: 'normal',
        allergies: '',
        allergiesStatus: '',
        dietaryPreferences: '',
        dietaryPreferencesStatus: '',
        selectedCuisines: [],
        selectedCuisinesStatus: ''
    });

    const PageDisplay = () => {
        if (page === 0) {
            return <ProfileForm1 page={page} setPage={setPage} formData={formData} setFormData={setFormData} />;
        } else if (page === 1) {
            return <ProfileForm2 page={page} setPage={setPage} formData={formData} setFormData={setFormData} />;
        }
    };

    const BorderLinearProgress = styled(LinearProgress)(({ theme }) => ({
        height: 10,
        borderRadius: 5,
        [`&.${linearProgressClasses.colorPrimary}`]: {
            backgroundColor: theme.palette.mode === 'dark' ? theme.palette.grey[800] : theme.palette.grey[200]
        },
        [`& .${linearProgressClasses.bar}`]: {
            borderRadius: 5,
            backgroundColor: theme.palette.mode === 'dark' ? '#308fe8' : '#1a90ff'
        }
    }));

    useEffect(() => {
        if (!decodedToken || Object.keys(decodedToken).length === 0) {
            navigate('/pages/login');
        }
        if (page === 0) {
            setProgressBarState(50);
        } else {
            setProgressBarState(100);
        }
    }, [page]);
    LogoutAfterInactivity();

    return (
        <AuthWrapper1>
            <Grid container direction="column" justifyContent="flex-end" sx={{ minHeight: '100vh' }}>
                <Grid item xs={12}>
                    <Grid container justifyContent="center" alignItems="center" sx={{ minHeight: 'calc(100vh - 68px)' }}>
                        <Grid item sx={{ m: { xs: 1, sm: 3 }, mb: 0 }}>
                            <AuthCardWrapper>
                                <Grid container spacing={2} alignItems="center" justifyContent="center">
                                    <Grid item sx={{ mb: 1 }}>
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
                                                <BorderLinearProgress variant="determinate" value={progressBarState} sx={{ mb: 3 }} />
                                                <Stack alignItems="center" justifyContent="center" spacing={1}>
                                                    <Typography
                                                        color={theme.palette.success.dark}
                                                        gutterBottom
                                                        variant={matchDownSM ? 'h3' : 'h2'}
                                                    >
                                                        User Profile Form
                                                    </Typography>
                                                    <Typography variant="caption" fontSize="16px" textAlign="center">
                                                        Please, provide your profile characteristics/goals in order to continue
                                                    </Typography>
                                                </Stack>
                                            </Grid>
                                        </Grid>
                                    </Grid>
                                    <Grid item xs={12}>
                                        {PageDisplay()}
                                    </Grid>
                                </Grid>
                            </AuthCardWrapper>
                        </Grid>
                    </Grid>
                </Grid>
                <Grid item xs={12}>
                    <AuthFooter />
                </Grid>
            </Grid>
        </AuthWrapper1>
    );
};

export default rUserProfile;
