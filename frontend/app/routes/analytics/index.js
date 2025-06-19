import React, { useState, useEffect } from 'react';
import EnergyIntake from 'components/analytics/energyIntake';
import FoodGroups from 'components/analytics/foodGroups';
import FoodGroupsPyramid from 'components/analytics/foodGroupsPyramid';
import TotalEnergyRequirements from 'components/analytics/totalEnergyRequirements';
import { getDecodedToken } from 'utils/tokenUtils';
import { useNavigate } from '@remix-run/react';
import LogoutAfterInactivity from 'utils/logoutAfterInactivity';
import MainCard from 'ui-component/cards/MainCard';
import { userActions } from 'services/api';
import { styled, useTheme } from '@mui/material/styles';

// material-ui
import { Grid, Box, Snackbar, Alert } from '@mui/material';

// ==============================|| MEAL PLAN PAGE ||============================== //

const Analytics = () => {
    const [isLoading, setLoading] = useState(true);
    const decodedToken = getDecodedToken();
    const [week, setWeek] = useState(null);
    const navigate = useNavigate();
    const theme = useTheme();
    const [open, setOpen] = React.useState(false);
    const [messageQueue, setMessageQueue] = useState([]);
    const [message, setMessage] = useState();

    // Call this function when you receive new feedback messages
    const addMessages = (messages) => {
        if (messages && messages.length > 0) {
            setMessageQueue((prevQueue) => [...prevQueue, ...messages]);
        }
    };

    useEffect(() => {
        if (!open && messageQueue.length > 0) {
            setMessage(messageQueue[0]);
            setMessageQueue((prev) => prev.slice(1));
            setOpen(true);
        }
    }, [messageQueue, open]);

    useEffect(() => {
        const trackLogin = async () => {
            if (!decodedToken || Object.keys(decodedToken).length === 0) {
                navigate('/pages/login');
            } else {
                let achievements;
                try {
                    achievements = await userActions(decodedToken.user_id, 'analytics');
                } catch (error) {
                    console.log(error.response?.data?.error || 'An unexpected error occurred');
                }
                addMessages(achievements?.data?.feedback);
            }
        };

        trackLogin();
        setLoading(false);
    }, []);

    const handleSnackbarClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }
        setOpen(false);
    };

    LogoutAfterInactivity();

    return (
        <MainCard sx={{ backgroundColor: theme.palette.success.light }}>
            <Grid container spacing={2}>
                <Grid item xs={12}>
                    <Grid container spacing={2}>
                        <Grid item xs={12} md={7}>
                            <TotalEnergyRequirements
                                isLoading={isLoading}
                                setSelectedWeek={(selectedWeek) => {
                                    setWeek(selectedWeek);
                                }}
                            />
                            <Box my={2} />
                            <EnergyIntake isLoading={isLoading} week={week} />
                            <Box my={2} />
                            <FoodGroups isLoading={isLoading} week={week} />
                        </Grid>
                        <Grid item xs={12} md={5}>
                            {/* <TotalEnergyRequirements
                            isLoading={isLoading}
                            setSelectedWeek={(selectedWeek) => {
                                setWeek(selectedWeek);
                            }}
                        /> */}

                            {/* <Ility isLoading={isLoading} week={week} />
                            <Box my={2} /> */}
                            <FoodGroupsPyramid isLoading={isLoading} week={week} />
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
            <Snackbar
                open={open}
                autoHideDuration={4000}
                onClose={handleSnackbarClose}
                anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
            >
                <Alert severity="success" sx={{ width: '100%' }}>
                    {message}
                </Alert>
            </Snackbar>
        </MainCard>
    );
};

export default Analytics;
