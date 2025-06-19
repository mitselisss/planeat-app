import React, { useEffect, useState } from 'react';
import MainCard from 'ui-component/cards/MainCard';

// material-ui
import { Box, Button, Grid, Typography, Switch } from '@mui/material';
import { styled, useTheme } from '@mui/material/styles';
import FormControlLabel from '@mui/material/FormControlLabel';

// project imports
import { gridSpacing } from 'store/constant';
import { fetchMealInfo } from 'services/api';
import { fetchDishesInfo } from 'services/api';

import NutritionalInfo from './nutritionalInfo';
import Ingredients from './ingredients';
import Sustainability from './sustainability';
import Recipe from './recipe';

import SkeletonDishes from 'ui-component/cards/Skeleton/MealPlan/Dishes';

// types
import PropTypes from 'prop-types';

const Dishes = ({ isLoading, isFetchingData, mealId, ratio }) => {
    const theme = useTheme();
    const label = { inputProps: { 'aria-label': 'Color switch demo' } };

    const [mealInfo, setMealInfo] = useState({});
    const [dishesInfo, setDishesInfo] = useState({});
    const [dishInfo, setDishInfo] = useState({});
    const [checked, setChecked] = useState('meal');

    const [errorMessage, setErrorMessage] = useState('');

    useEffect(() => {
        // console.log(mealId);
        setChecked('meal');
        setErrorMessage('');
        const fetchData = async () => {
            try {
                const [getMealInfo, getDishesInfo] = await Promise.all([fetchMealInfo(mealId), fetchDishesInfo(mealId)]);

                // console.log(getMealInfo);
                // console.log(getDishesInfo);
                setMealInfo(getMealInfo);
                setDishesInfo(getDishesInfo);
                setDishInfo(Object.values(getDishesInfo)[0]);
            } catch (error) {
                setMealInfo({});
                setDishesInfo({});
                setDishInfo({});

                setErrorMessage(error.response?.data?.error || 'An unexpected error occurred');
                // console.log(error.response?.data?.error || 'An unexpected error occurred');
            }
        };

        if (mealId && mealId >= 1) {
            fetchData();
        } else {
            setMealInfo({});
            setDishesInfo({});
            setDishInfo({});
        }
    }, [mealId]);

    const handleClick = () => {
        setChecked((prev) => (prev === 'meal' ? 'dishes' : 'meal'));
    };

    return (
        <>
            {isLoading || isFetchingData ? (
                <SkeletonDishes />
            ) : (
                <MainCard sx={{ backgroundColor: theme.palette.success[100] }}>
                    {/* Main Card displaying the week range */} {/* Apply spacing */}
                    <Grid item mt={2}>
                        {Object.keys(mealInfo).length > 0 || Object.keys(dishesInfo).length > 0 ? (
                            // <Grid item sx={{ textAlign: 'right' }}>
                            //     <FormControlLabel
                            //         control={<Switch defaultChecked onClick={handleClick} />}
                            //         label={checked === 'meal' ? 'Meal Info' : 'Dishes Info'}
                            //         disabled={Object.keys(dishesInfo).length === 1}
                            //     />
                            // </Grid>
                            <Grid item sx={{ textAlign: 'right' }}>
                                <Button
                                    disableElevation
                                    variant={checked === 'meal' ? 'contained' : 'text'}
                                    size="small"
                                    sx={{ color: theme.palette.primary[200] }}
                                    onClick={() => setChecked('meal')}
                                >
                                    <Typography color={checked === 'meal' ? theme.palette.primary.light : theme.palette.primary.main}>
                                        Meal Info
                                    </Typography>
                                </Button>
                                {Object.keys(dishesInfo).length > 1 && (
                                    <Button
                                        disableElevation
                                        variant={checked === 'dishes' ? 'contained' : 'text'}
                                        size="small"
                                        sx={{ color: theme.palette.primary[200] }}
                                        onClick={() => setChecked('dishes')}
                                    >
                                        <Typography color={checked === 'dishes' ? theme.palette.primary.light : theme.palette.primary.main}>
                                            Dishes Info
                                        </Typography>
                                    </Button>
                                )}
                            </Grid>
                        ) : (
                            <Grid item sx={{ textAlign: 'center' }}>
                                {errorMessage ? (
                                    <Typography variant="body1" color={theme.palette.error.main}>
                                        {errorMessage}
                                    </Typography>
                                ) : (
                                    <Typography variant="body1">Select one of the avaliable meals to see more information</Typography>
                                )}
                            </Grid>
                        )}
                        <Grid container sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                            {checked === 'meal' ? (
                                <Grid item>
                                    <Button
                                        disableElevation
                                        size="small"
                                        variant="text"
                                        disabled
                                        sx={{
                                            bgcolor: mealInfo.meal_id === mealId ? theme.palette.secondary.light : 'transparent'
                                            // '&:hover': {
                                            //     bgcolor: theme.palette.secondary.light
                                            // }
                                        }}
                                        onClick={() => setDishInfo(dish)}
                                    >
                                        <Typography
                                            variant="h5"
                                            sx={{
                                                color: theme.palette.secondary.dark
                                                // '&:hover': {
                                                //     bgcolor: theme.palette.secondary.light
                                                // }
                                            }}
                                        >
                                            {mealInfo.meal_name}
                                        </Typography>
                                    </Button>
                                </Grid>
                            ) : (
                                <>
                                    {Object.values(dishesInfo).map((dish) => (
                                        <Grid item key={dish.id}>
                                            {' '}
                                            {/* Assuming `dish.id` is a unique identifier */}
                                            <Button
                                                disableElevation
                                                size="small"
                                                variant="text"
                                                disabled={dishInfo === dish}
                                                sx={{
                                                    bgcolor: dishInfo === dish ? theme.palette.secondary.light : 'transparent',
                                                    '&:hover': {
                                                        bgcolor: theme.palette.secondary.light
                                                    }
                                                }}
                                                onClick={() => setDishInfo(dish)}
                                            >
                                                <Typography
                                                    variant="h5"
                                                    sx={{
                                                        color: theme.palette.secondary.dark
                                                        // '&:hover': {
                                                        //     bgcolor: theme.palette.secondary.light
                                                        // }
                                                    }}
                                                >
                                                    {dish.dish_name ? dish.dish_name : 'Dish'}
                                                </Typography>
                                            </Button>
                                        </Grid>
                                    ))}
                                </>
                            )}
                        </Grid>
                    </Grid>
                    <Grid item mt={2}>
                        <NutritionalInfo checked={checked} mealInfo={mealInfo} dishInfo={dishInfo} />
                    </Grid>
                    <Grid item mt={2}>
                        <Ingredients checked={checked} mealInfo={mealInfo} dishInfo={dishInfo} />
                    </Grid>
                    {/* <Grid item mt={2}>
                        <Sustainability />
                    </Grid> */}
                    {/* {checked === 'dishes' && dishInfo.dish_recipe !== '' && (
                        <Grid item mt={2}>
                            <Recipe dishRecipe={dishInfo.dish_recipe} />
                        </Grid>
                    )} */}
                </MainCard>
            )}
        </>
    );
};

Dishes.propTypes = {
    isLoading: PropTypes.bool
};

export default Dishes;
