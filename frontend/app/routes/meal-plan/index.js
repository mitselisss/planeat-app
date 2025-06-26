import { useState, useEffect } from 'react';

// material-ui
import { Grid } from '@mui/material';

import { getDecodedToken } from 'utils/tokenUtils';
import { useNavigate } from '@remix-run/react';
import { userActions } from 'services/api';

import Meals from 'components/mealPlans/meals';
import MealsWeekly from 'components/mealPlans/meals_weekly';
import Dishes from 'components/mealPlans/dishes';
import LogoutAfterInactivity from 'utils/logoutAfterInactivity';
import { getUserProfile } from 'services/api';

// ==============================|| MEAL PLAN PAGE ||============================== //

const MealPlan = () => {
    const [selectedMealId, setSelectedMealId] = useState(); // State to track selected meal ID
    const [mealRatio, setMealRatio] = useState(1); // Store ratio in parent
    const [isFetchingData, setIsFetchingData] = useState(false);
    const [weekly, setWeekly] = useState();
    const [weeklyMealSelection, setWeeklyMealSelection] = useState({});
    const decodedToken = getDecodedToken();
    const navigate = useNavigate();

    const [isLoading, setLoading] = useState(true);
    useEffect(() => {
        const trackLogin = async () => {
            if (!decodedToken || Object.keys(decodedToken).length === 0) {
                navigate('/pages/login');
            } else {
                try {
                    const userProfile = await getUserProfile(decodedToken.user_id);
                    setWeekly(userProfile.main_screen === 'weekly' ? true : false);
                    await userActions(decodedToken.user_id, 'meal-plan');
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
        <Grid container spacing={2}>
            {weekly ? (
                <Grid item xs={12}>
                    <Grid container>
                        <Grid item xs={12} md={12}>
                            {/* Pass the callback to update selectedMealId */}
                            <MealsWeekly
                                isLoading={isLoading}
                                isFetchingData={isFetchingData}
                                setIsFetchingData={setIsFetchingData}
                                mealId={(meal_id) => setSelectedMealId(meal_id)}
                                setRatio={(ratio) => setMealRatio(ratio)} // Update ratio from Meals
                                setWeekly={setWeekly}
                                weekly={weekly}
                                setWeeklyMealSelection={setWeeklyMealSelection}
                                weeklyMealSelection={weeklyMealSelection}
                            />
                        </Grid>
                    </Grid>
                </Grid>
            ) : (
                <Grid item xs={12}>
                    <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                            {/* Pass the callback to update selectedMealId */}
                            <Meals
                                isLoading={isLoading}
                                isFetchingData={isFetchingData}
                                setIsFetchingData={setIsFetchingData}
                                mealId={(meal_id) => setSelectedMealId(meal_id)}
                                setRatio={(ratio) => setMealRatio(ratio)} // Update ratio from Meals
                                setWeekly={setWeekly}
                                weekly={weekly}
                                setWeeklyMealSelection={setWeeklyMealSelection}
                                weeklyMealSelection={weeklyMealSelection}
                            />
                        </Grid>
                        <Grid item xs={12} md={6}>
                            {/* Pass the selectedMealId to Dishes */}
                            <Dishes
                                isLoading={isLoading}
                                isFetchingData={isFetchingData}
                                mealId={selectedMealId}
                                ratio={mealRatio} // Pass ratio to Dishes
                            />
                        </Grid>
                    </Grid>
                </Grid>
            )}

            {/* <Grid item xs={12}>
                <Grid container spacing={2}>
                    <Grid item xs={12} md={8}></Grid>
                </Grid>
            </Grid> */}

            {/* <Grid item xs={12}>
                <Footer />
            </Grid> */}
        </Grid>
    );
};

export default MealPlan;
