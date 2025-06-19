import { useEffect, useState } from 'react';

// material-ui
import { Grid, Box, Typography, TextField, MenuItem } from '@mui/material';
import { styled, useTheme } from '@mui/material/styles';

// project imports
import { gridSpacing } from 'store/constant';
import MainCard from 'ui-component/cards/MainCard';
import SkeletonTotalGrowthBarChart from 'ui-component/cards/Skeleton/TotalGrowthBarChart';
import IlityChart from './charts/ilityChart';
import { getDecodedToken } from 'utils/tokenUtils';

import { fetchNPsAnalytics } from 'services/api';

// types
import PropTypes from 'prop-types';

// ==============================|| DASHBOARD DEFAULT - TOTAL GROWTH BAR CHART CARD ||============================== //

const Ility = ({ isLoading, week }) => {
    const theme = useTheme();
    const decodedToken = getDecodedToken();
    const [analytics, setAnalytics] = useState();
    const [isFetchingData, setIsFetchingData] = useState(false);
    const [currDay, setCurrDay] = useState(0);

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

    const handleDayChange = async (event) => {
        const selectedDay = event.target.value;
        const dayIndex = days.findIndex((day) => day.value === selectedDay);
        setCurrDay(dayIndex);
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
                                                Sustainability, Affordability, Accessibility
                                            </Typography>
                                        </Grid>
                                        <Grid item>
                                            <Typography variant="subtitle2">
                                                Suggested daily plans impact on the planet, economy, and lifestyle.
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
                            <IlityChart />
                        </Grid>
                    </Grid>
                    <Box mb={2}>
                        <Typography variant="subtitle2" color={theme.palette.error.dark}>
                            ⚠️ This diagram is for demonstration purposes only. Full functionality will be included in future versions.
                        </Typography>
                    </Box>
                </MainCard>
            )}
        </>
    );
};

Ility.propTypes = {
    isLoading: PropTypes.bool
};

export default Ility;
