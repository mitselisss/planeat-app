import React, { useEffect, useState } from 'react';
import MainCard from 'ui-component/cards/MainCard';

// material-ui
import { Box, Button, Grid, Typography, Switch } from '@mui/material';
import { styled, useTheme } from '@mui/material/styles';

const NutritionalInfo = ({ checked, mealInfo, dishInfo }) => {
    const theme = useTheme();
    const [displayInfo, setDisplayInfo] = useState({});

    useEffect(() => {
        {
            checked === 'meal' ? setDisplayInfo(mealInfo) : setDisplayInfo(dishInfo);
        }
    });

    return (
        <MainCard>
            <Grid container spacing={3}>
                {' '}
                {/* Apply spacing to the container */}
                <Grid item sx={{ display: 'flex', alignItems: 'center', justifyContent: 'left' }}>
                    <Typography variant="h5">Nutritional Info</Typography>
                </Grid>
                {(Object.keys(mealInfo).length > 0 || Object.keys(dishInfo).length > 0) && (
                    <Grid container item sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Grid
                            item
                            sx={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center'
                            }}
                        >
                            <Typography variant="body2">{Math.round(displayInfo.Total_Energy)} kcal</Typography>
                            <Typography variant="body2">Calories</Typography>
                        </Grid>
                        <Grid
                            item
                            sx={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center'
                            }}
                        >
                            <Typography variant="body2">{Math.round(displayInfo.Total_Carbs)} g</Typography>
                            <Typography variant="body2">Carbohydrates</Typography>
                        </Grid>
                        <Grid
                            item
                            sx={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center'
                            }}
                        >
                            <Typography variant="body2">{Math.round(displayInfo.Total_Protein)} g</Typography>
                            <Typography variant="body2">Protein</Typography>
                        </Grid>
                        <Grid
                            item
                            sx={{
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'center'
                            }}
                        >
                            <Typography variant="body2">{Math.round(displayInfo.Total_Fat)} g</Typography>
                            <Typography variant="body2">Fat</Typography>
                        </Grid>
                    </Grid>
                )}
            </Grid>
        </MainCard>
    );
};

export default NutritionalInfo;
