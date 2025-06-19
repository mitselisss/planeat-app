import { useEffect, useState } from 'react';

// material-ui
import { Grid } from '@mui/material';

// project imports
import { gridSpacing } from 'store/constant';
import EarningCard from 'components/dashboard/EarningCard';
import TotalOrderLineCard from 'components/dashboard/TotalOrderLineCard';
import TotalIncomeDarkCard from 'components/dashboard/TotalIncomeDarkCard';
import TotalIncomeLightCard from 'components/dashboard/TotalIncomeLightCard';
import TotalGrowthBarCard from 'components/dashboard/TotalGrowthBarCard';
import PopularCard from 'components/dashboard/PopularCard';

import WeeklyMeals from 'components/planEatDashboard/weekly_meals';
import CurrentState from 'components/achievments/currentState';

// meta export
export const meta = () => ({
    title: 'Dashboard | Berry - React Material Admin Dashboard Template',
    description:
        'Start your next React project with Berry admin template. It build with Reactjs, Material-UI, Redux, and Hook for faster web development.'
});

// ==============================|| DEFAULT DASHBOARD ||============================== //

const Dashboard = () => {
    const [isLoading, setLoading] = useState(true);
    useEffect(() => {
        setLoading(false);
    }, []);

    const [selectedMealId, setSelectedMealId] = useState(); // State to track selected meal ID
    const [mealRatio, setMealRatio] = useState(1); // Store ratio in parent
    const [isFetchingData, setIsFetchingData] = useState(false);
    const [weekly, setWeekly] = useState(false);
    const [weeklyMealSelection, setWeeklyMealSelection] = useState({});

    return (
        <Grid container spacing={gridSpacing}>
            <Grid item xs={12}>
                <Grid container spacing={gridSpacing}>
                    <Grid item lg={4} md={6} sm={6} xs={12}>
                        <CurrentState />
                    </Grid>
                    <Grid item lg={4} md={6} sm={6} xs={12}>
                        <TotalOrderLineCard isLoading={isLoading} />
                    </Grid>
                    <Grid item lg={4} md={12} sm={12} xs={12}>
                        <Grid container spacing={gridSpacing}>
                            <Grid item sm={6} xs={12} md={6} lg={12}>
                                <TotalIncomeDarkCard isLoading={isLoading} />
                            </Grid>
                            <Grid item sm={6} xs={12} md={6} lg={12}>
                                <TotalIncomeLightCard isLoading={isLoading} />
                            </Grid>
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
            <Grid item xs={12}>
                <Grid container spacing={gridSpacing}>
                    <Grid item xs={12} md={10}>
                        <WeeklyMeals
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
                    <Grid item xs={12} md={2}>
                        <PopularCard isLoading={isLoading} />
                    </Grid>
                </Grid>
            </Grid>
        </Grid>
    );
};

export default Dashboard;
