import { useEffect, useState } from 'react';

// material-ui
import { Grid, Typography, Button } from '@mui/material';
import { styled, useTheme } from '@mui/material/styles';

// project imports
import { gridSpacing } from 'store/constant';
import MainCard from 'ui-component/cards/MainCard';
import SkeletonTotalGrowthBarChart from 'ui-component/cards/Skeleton/TotalGrowthBarChart';
import EnergyIntakeChart from './charts/energyIntakeChart';
import MacroChart from './charts/macroChart';
import { getDecodedToken } from 'utils/tokenUtils';

import { fetchNPsAnalytics } from 'services/api';

// types
import PropTypes from 'prop-types';

// ==============================|| DASHBOARD DEFAULT - TOTAL GROWTH BAR CHART CARD ||============================== //

const EnergyIntake = ({ isLoading, week }) => {
    const theme = useTheme();
    const decodedToken = getDecodedToken();
    const [analytics, setAnalytics] = useState();
    const [isFetchingData, setIsFetchingData] = useState(false);
    const [checked, setChecked] = useState('energy_intake');

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
                            <Grid container direction="column" spacing={1}>
                                <Grid item sx={{ textAlign: 'right' }}>
                                    <Button
                                        disableElevation
                                        variant={checked === 'energy_intake' ? 'contained' : 'text'}
                                        size="small"
                                        sx={{ color: theme.palette.primary[200] }}
                                        onClick={() => setChecked('energy_intake')}
                                    >
                                        <Typography
                                            color={checked === 'energy_intake' ? theme.palette.primary.light : theme.palette.primary.main}
                                        >
                                            Weekly Energy Intake
                                        </Typography>
                                    </Button>
                                    <Button
                                        disableElevation
                                        variant={checked === 'macronutrients' ? 'contained' : 'text'}
                                        size="small"
                                        sx={{ color: theme.palette.primary[200] }}
                                        onClick={() => setChecked('macronutrients')}
                                    >
                                        <Typography
                                            color={checked === 'macronutrients' ? theme.palette.primary.light : theme.palette.primary.main}
                                        >
                                            Macronutrients
                                        </Typography>
                                    </Button>
                                </Grid>

                                {checked === 'energy_intake' ? (
                                    <Grid container alignItems="center" justifyContent="space-between">
                                        <Grid item>
                                            <Grid item>
                                                <Typography variant="h3" color={theme.palette.success.dark}>
                                                    Weekly Energy Intake
                                                </Typography>
                                            </Grid>
                                            <Grid item>
                                                <Typography variant="subtitle2">
                                                    Suggested daily plans energy intake compared to the user’s daily energy requirements.
                                                </Typography>
                                            </Grid>
                                        </Grid>
                                    </Grid>
                                ) : (
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
                                )}
                            </Grid>
                        </Grid>
                        <Grid item xs={12}>
                            {checked === 'energy_intake' ? (
                                <EnergyIntakeChart analytics={analytics} />
                            ) : (
                                <MacroChart analytics={analytics} />
                            )}
                        </Grid>
                    </Grid>
                </MainCard>
            )}
        </>
    );
};

EnergyIntake.propTypes = {
    isLoading: PropTypes.bool
};

export default EnergyIntake;
