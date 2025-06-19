import React, { useState, useEffect } from 'react';
import MainCard from 'ui-component/cards/MainCard';
import { Typography, Box, Grid, FormControl, Radio, RadioGroup, FormControlLabel } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { updateUserMainScreen } from 'services/api';
import { getDecodedToken } from 'utils/tokenUtils';
import { getUserProfile } from 'services/api';

import daily_plan from '../../assets/images/settings/daily_plan.png';
import weekly_menu from '../../assets/images/settings/weekly_menu.png';

const MainScreen = () => {
    const theme = useTheme();
    const decodedToken = getDecodedToken();
    const [screen, setScreen] = useState();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const userProfile = await getUserProfile(decodedToken.user_id);
                setScreen(userProfile.main_screen);
            } catch (error) {
                console.log(error.response?.data?.error || 'An unexpected error occurred');
            }
        };

        fetchData();
    }, []);

    const handleChange = async (value) => {
        try {
            const updateUserScreen = await updateUserMainScreen(decodedToken.user_id, value);
            // setSuccessMessage(updateUserScreen.data.message);
            console.log(updateUserScreen.data.message);
        } catch (error) {
            console.log(error.updateUserScreen?.data?.error || 'An unexpected error occurred');
        }
    };

    return (
        <MainCard>
            <Grid container direction="column" spacing={3}>
                <Grid item>
                    <Typography variant="h3" color={theme.palette.success.dark}>
                        Main Screen
                    </Typography>
                    <Typography variant="subtitle2">Select your preferred main screen to display when launching the app.</Typography>
                </Grid>

                <Grid item>
                    <FormControl>
                        {screen && (
                            <RadioGroup
                                row
                                name="main-screen-selection"
                                value={screen}
                                onChange={(event) => {
                                    handleChange(event.target.value);
                                    setScreen(event.target.value);
                                }}
                            >
                                {/* Daily Option */}
                                <Grid container spacing={2} justifyContent="center">
                                    <Grid item xs={12} sm={6}>
                                        <Box textAlign="center">
                                            <Box
                                                component="img"
                                                src={daily_plan}
                                                alt="Daily Plan"
                                                sx={{ width: '100%', maxWidth: 500, borderRadius: 2, mb: 1 }}
                                            />
                                            <FormControlLabel value="daily" control={<Radio />} label="Daily Plans" />
                                        </Box>
                                    </Grid>

                                    {/* Weekly Option */}
                                    <Grid item xs={12} sm={6}>
                                        <Box textAlign="center">
                                            <Box
                                                component="img"
                                                src={weekly_menu}
                                                alt="Weekly Menu"
                                                sx={{ width: '100%', maxWidth: 500, borderRadius: 2, mb: 1 }}
                                            />
                                            <FormControlLabel value="weekly" control={<Radio />} label="Weekly Menu" />
                                        </Box>
                                    </Grid>
                                </Grid>
                            </RadioGroup>
                        )}
                    </FormControl>
                </Grid>
            </Grid>
        </MainCard>
    );
};

export default MainScreen;
