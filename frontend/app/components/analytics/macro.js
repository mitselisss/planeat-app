import { useEffect, useState } from 'react';

// material-ui
import { Grid, Typography } from '@mui/material';
import { styled, useTheme } from '@mui/material/styles';

// project imports
import { gridSpacing } from 'store/constant';
import MainCard from 'ui-component/cards/MainCard';
import SkeletonTotalGrowthBarChart from 'ui-component/cards/Skeleton/TotalGrowthBarChart';
import MacroChart from './charts/macroChart';
import { getDecodedToken } from 'utils/tokenUtils';

import { fetchNPsAnalytics } from 'services/api';

// types
import PropTypes from 'prop-types';

// ==============================|| DASHBOARD DEFAULT - TOTAL GROWTH BAR CHART CARD ||============================== //

const Macro = ({ isLoading, week }) => {
    const theme = useTheme();
    const decodedToken = getDecodedToken();
    const [analytics, setAnalytics] = useState();
    const [isFetchingData, setIsFetchingData] = useState(false);

    useEffect(() => {
        if (!week) return;

        const fetchData = async () => {
            setIsFetchingData(true);

            try {
                const NPsAnalytics = await fetchNPsAnalytics(decodedToken.user_id, week);
                setAnalytics(NPsAnalytics);
            } catch (error) {
                console.log(error.response?.data?.error || 'An unexpected error occurred');
            }

            setIsFetchingData(false);
        };

        fetchData();
    }, [week]);

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
                                                Macronutrients
                                            </Typography>
                                        </Grid>
                                        <Grid item>
                                            <Typography variant="subtitle2">
                                                Suggested daily plans macronutrients (carbohydrates, fat, protein) distribution.
                                            </Typography>
                                        </Grid>
                                    </Grid>
                                </Grid>
                                <Grid item></Grid>
                            </Grid>
                        </Grid>
                        <Grid item xs={12}>
                            <MacroChart analytics={analytics} />
                        </Grid>
                    </Grid>
                </MainCard>
            )}
        </>
    );
};

Macro.propTypes = {
    isLoading: PropTypes.bool
};

export default Macro;
