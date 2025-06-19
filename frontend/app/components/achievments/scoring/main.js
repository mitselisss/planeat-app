import React, { useEffect, useState } from 'react';
import MainCard from 'ui-component/cards/MainCard';
import { Grid, Typography, Button, Box } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { getUserAchievments } from 'services/api';
import { getDecodedToken } from 'utils/tokenUtils';
import Badges from './badges';
import Trails from './trails';
import Levels from './levels';
import PointsTable from './points';

const Main = () => {
    const [checked, setChecked] = useState('badges');
    const theme = useTheme();
    const [achievements, setAchievements] = useState();
    const decodedToken = getDecodedToken();
    const [isFetchingData, setIsFetchingData] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            setIsFetchingData(true);

            try {
                const userAchievements = await getUserAchievments(decodedToken.user_id);
                setAchievements(userAchievements);
            } catch (error) {
                console.log(error.response?.data?.error || 'An unexpected error occurred');
            }

            setIsFetchingData(false);
        };

        fetchData();
    }, []);

    return (
        <MainCard sx={{ backgroundColor: theme.palette.success.light }}>
            <Grid item sx={{ textAlign: 'right' }}>
                <Button
                    disableElevation
                    variant={checked === 'badges' ? 'contained' : 'text'}
                    size="small"
                    sx={{ color: theme.palette.primary[200] }}
                    onClick={() => {
                        setChecked('badges');
                    }}
                >
                    <Typography color={checked === 'badges' ? theme.palette.primary.light : theme.palette.primary.main}>Badges</Typography>
                </Button>
                <Button
                    disableElevation
                    variant={checked === 'trails' ? 'contained' : 'text'}
                    size="small"
                    sx={{ color: theme.palette.primary[200] }}
                    onClick={() => {
                        setChecked('trails');
                    }}
                >
                    <Typography color={checked === 'trails' ? theme.palette.primary.light : theme.palette.primary.main}>Trails</Typography>
                </Button>
                <Button
                    disableElevation
                    variant={checked === 'levels' ? 'contained' : 'text'}
                    size="small"
                    sx={{ color: theme.palette.primary[200] }}
                    onClick={() => {
                        setChecked('levels');
                    }}
                >
                    <Typography color={checked === 'levels' ? theme.palette.primary.light : theme.palette.primary.main}>Levels</Typography>
                </Button>
                <Button
                    disableElevation
                    variant={checked === 'points' ? 'contained' : 'text'}
                    size="small"
                    sx={{ color: theme.palette.primary[200] }}
                    onClick={() => {
                        setChecked('points');
                    }}
                >
                    <Typography color={checked === 'points' ? theme.palette.primary.light : theme.palette.primary.main}>Points</Typography>
                </Button>
            </Grid>

            <Grid item xs={12}>
                {checked === 'badges' ? (
                    <Badges achievements={achievements} />
                ) : checked === 'trails' ? (
                    <Trails achievements={achievements} />
                ) : checked === 'levels' ? (
                    <Levels achievements={achievements} />
                ) : checked === 'points' ? (
                    <PointsTable />
                ) : null}
            </Grid>
        </MainCard>
    );
};

export default Main;
