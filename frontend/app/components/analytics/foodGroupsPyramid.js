import { useState, useEffect } from 'react';

// material-ui
import { Grid, MenuItem, TextField, Typography } from '@mui/material';
import { useTheme } from '@mui/material/styles';

// project imports
import { gridSpacing } from 'store/constant';
import MainCard from 'ui-component/cards/MainCard';
import SkeletonTotalGrowthBarChart from 'ui-component/cards/Skeleton/TotalGrowthBarChart';
import FoodGroupsPyramidChart from './charts/foodGroupsPyramidChart';

import { getDecodedToken } from 'utils/tokenUtils';
import { fetchNPsFoodCategories, fetchNPsFoodCategoriesWeekly } from 'services/api';

// types
import PropTypes from 'prop-types';

const days = [
    { value: 'Weekly', label: 'Weekly' }, // ✅ Weekly is now first in the list
    { value: 'Monday', label: 'Monday' },
    { value: 'Tuesday', label: 'Tuesday' },
    { value: 'Wednesday', label: 'Wednesday' },
    { value: 'Thursday', label: 'Thursday' },
    { value: 'Friday', label: 'Friday' },
    { value: 'Saturday', label: 'Saturday' },
    { value: 'Sunday', label: 'Sunday' }
];

const FoodGroupsPyramid = ({ isLoading, week }) => {
    const theme = useTheme();
    const decodedToken = getDecodedToken();

    // ✅ Default to "Weekly"
    const [currDay, setCurrDay] = useState(0);
    const [analytics, setAnalytics] = useState();
    const [isFetchingData, setIsFetchingData] = useState(false);

    useEffect(() => {
        if (!week) return;
        const fetchData = async () => {
            setIsFetchingData(true);
            try {
                // ✅ Fetch weekly data by default
                const data = await fetchNPsFoodCategoriesWeekly(decodedToken.user_id, week);
                // console.log(data);
                setAnalytics(data);
            } catch (error) {
                console.log(error.response?.data?.error || 'An unexpected error occurred');
            }
            setIsFetchingData(false);
        };

        fetchData();
    }, [week]); // ✅ Reload when the week changes

    const handleDayChange = async (event) => {
        const selectedDay = event.target.value;
        const dayIndex = days.findIndex((day) => day.value === selectedDay);
        setCurrDay(dayIndex);

        try {
            let data;
            if (selectedDay === 'Weekly') {
                data = await fetchNPsFoodCategoriesWeekly(decodedToken.user_id, week);
            } else {
                data = await fetchNPsFoodCategories(decodedToken.user_id, week, selectedDay);
            }
            setAnalytics(data);
        } catch (error) {
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }
    };

    return (
        <>
            {isLoading || isFetchingData ? (
                <SkeletonTotalGrowthBarChart />
            ) : (
                <MainCard>
                    <Grid container spacing={gridSpacing}>
                        <Grid item xs={12}>
                            <Grid container alignItems="center" justifyContent="space-between">
                                <Grid item>
                                    <Grid container direction="column" spacing={1}>
                                        <Grid item>
                                            <Typography variant="h3" color={theme.palette.success.dark}>
                                                Food Groups
                                            </Typography>
                                        </Grid>
                                        <Grid item>
                                            <Typography variant="subtitle2">
                                                {currDay === 0 ? `Weekly food groups consumption.` : `Daily food groups consumption.`}
                                            </Typography>
                                        </Grid>
                                    </Grid>
                                </Grid>
                                <Grid item>
                                    <TextField
                                        id="day-select"
                                        select
                                        value={days[currDay].value} // ✅ Default to "Weekly"
                                        onChange={handleDayChange}
                                    >
                                        {days.map((option) => (
                                            <MenuItem key={option.value} value={option.value}>
                                                <Typography variant="body1" sx={{ color: theme.palette.success.dark }}>
                                                    {option.label}
                                                </Typography>
                                            </MenuItem>
                                        ))}
                                    </TextField>
                                </Grid>
                            </Grid>
                        </Grid>
                        <Grid item xs={12}>
                            <FoodGroupsPyramidChart analytics={analytics} />
                        </Grid>
                    </Grid>
                </MainCard>
            )}
        </>
    );
};

FoodGroupsPyramid.propTypes = {
    isLoading: PropTypes.bool,
    week: PropTypes.string.isRequired
};

export default FoodGroupsPyramid;
