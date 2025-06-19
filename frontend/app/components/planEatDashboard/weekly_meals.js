import React, { useState, useEffect } from 'react';

// material-ui
import { Box, Typography, Alert, Snackbar } from '@mui/material';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
import { styled, useTheme } from '@mui/material/styles';
// import { IconShoppingBagPlus } from '@tabler/icons-react';

// project imports
import MainCard from 'ui-component/cards/MainCard';
import { getDecodedToken } from 'utils/tokenUtils';
import { formatDate } from 'utils/formatDate';
import { fetchWeeklyNPs, fetchUserWeeks, fetchWeeklyNP, createNPs } from 'services/api';
import { getCurrentDayAndWeekDates } from 'utils/getCurrentDayAndWeekDates';

import SkeletonMealPlan from 'ui-component/cards/Skeleton/MealPlan/MealPlan';

// types
import PropTypes from 'prop-types';

// styles
const CardWrapper = styled(MainCard)(({ theme }) => ({
    overflow: 'hidden',
    position: 'relative',
    backgroundColor: theme.palette.success.light,
    '&:after': {
        content: '""',
        position: 'absolute',
        width: 210,
        height: 210,
        background: `linear-gradient(210.04deg, ${theme.palette.success.light} -50.94%, rgba(144, 202, 249, 0) 83.49%)`,
        borderRadius: '50%',
        top: -30,
        right: -180
    },
    '&:before': {
        content: '""',
        position: 'absolute',
        width: 210,
        height: 210,
        background: `linear-gradient(140.9deg, ${theme.palette.success.light} -14.02%, rgba(144, 202, 249, 0) 70.50%)`,
        borderRadius: '50%',
        top: -160,
        right: -130
    }
}));

const WeeklyMeals = ({
    isLoading,
    isFetchingData,
    setIsFetchingData,
    mealId,
    setWeekly,
    weekly,
    setWeeklyMealSelection,
    weeklyMealSelection
}) => {
    const theme = useTheme();
    const decodedToken = getDecodedToken();
    const label = { inputProps: { 'aria-label': 'Checkbox demo' } };
    const [anchorEl, setAnchorEl] = useState(null);
    // const [currDay, setCurrDay] = useState();
    const [NP, setNP] = useState({});
    const [NPsWeeks, setNPsWeeks] = useState({});
    // const [selectedDay, setSelectedDay] = useState();
    const [selectedWeek, setSelectedWeek] = useState();
    const [selectedMealId, setSelectedMealId] = useState();
    const [message, setMessage] = useState();
    const [open, setOpen] = React.useState(false);

    const days = [
        {
            value: 'Monday',
            label: 'Monday'
        },
        {
            value: 'Tuesday',
            label: 'Tuesday'
        },
        {
            value: 'Wednesday',
            label: 'Wednesday'
        },
        {
            value: 'Thursday',
            label: 'Thursday'
        },
        {
            value: 'Friday',
            label: 'Friday'
        },
        {
            value: 'Saturday',
            label: 'Saturday'
        },
        {
            value: 'Sunday',
            label: 'Sunday'
        }
    ];

    const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

    const mealTypes = ['Breakfast', 'Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner'];

    // console.log(decodedToken.user_id);

    useEffect(() => {
        const { currday, currMondayDate, currSundayDate } = getCurrentDayAndWeekDates();

        // setCurrDay(currday);
        // setSelectedDay(days[currday].value);
        setSelectedWeek(currMondayDate);

        const fetchData = async () => {
            setIsFetchingData(true);

            try {
                const checkNP = await fetchWeeklyNP(decodedToken.user_id, currMondayDate, currSundayDate);
                if (checkNP.status === 200) {
                    try {
                        // Using the custom fetch functions
                        const [NPsWeeksResponse, MealsResponse] = await Promise.all([
                            fetchUserWeeks(decodedToken.user_id),
                            fetchWeeklyNPs(decodedToken.user_id, currMondayDate)
                        ]);

                        // console.log(MealsResponse);

                        // Set the state if the response is successful
                        setNPsWeeks(NPsWeeksResponse); // NPsWeeksResponse contains the data directly
                        setNP(MealsResponse); // MealsResponse contains the data directly
                        // setRatio(MealsResponse.meal_0.ratio);
                    } catch (error) {
                        // Handle error
                        console.log(error.response?.data?.error || 'An unexpected error occurred');
                    }
                }
            } catch (error) {
                console.log(error.response?.data?.error || 'An unexpected error occurred');

                try {
                    const createnps = await createNPs(decodedToken.user_id, currMondayDate, currSundayDate);
                    if (createnps.status === 200) {
                        try {
                            // Using the custom fetch functions
                            const [NPsWeeksResponse, MealsResponse] = await Promise.all([
                                fetchUserWeeks(decodedToken.user_id), // Call fetchUserWeeks with userId 30
                                fetchWeeklyNPs(decodedToken.user_id, currMondayDate)
                            ]);

                            // Set the state if the response is successful
                            setNPsWeeks(NPsWeeksResponse); // NPsWeeksResponse contains the data directly
                            setNP(MealsResponse); // MealsResponse contains the data directly
                            // setRatio(MealsResponse.meal_0.ratio);
                        } catch (error) {
                            // Handle error
                            console.log(error.response?.data?.error || 'An unexpected error occurred');
                        }
                    }
                } catch (error) {
                    console.log(error.response?.data?.error || 'An unexpected error occurred');
                }
            }

            setIsFetchingData(false);
        };

        fetchData();
    }, []); // Empty dependency array to run on component mount

    const convertDateFormat = (dateString) => {
        // Split the date string into day, month, and year
        const [day, month, year] = dateString.split('-');

        // Rearrange to the format YYYY-MM-DD
        return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    };

    const convertDateFormatReverse = (dateString) => {
        // Split the date string into day, month, and year
        const [year, month, day] = dateString.split('-');

        // Rearrange to the format YYYY-MM-DD
        return `${day.padStart(2, '0')}-${month.padStart(2, '0')}-${year}`;
    };

    const handleMealClick = (week, day, type, meal_id) => {
        // console.log(week, day, type, meal_id);
        setWeeklyMealSelection({
            week: week,
            day: day,
            type: type,
            meal_id: meal_id
        });
        mealId(meal_id); // Send selected meal to parent
        setSelectedMealId(meal_id);
        setWeekly((prevWeekly) => !prevWeekly);
    };

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const handleSnackbarClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }

        setOpen(false);
    };

    return (
        <>
            {isLoading || isFetchingData ? (
                <SkeletonMealPlan />
            ) : (
                <CardWrapper border={false} content={false}>
                    {/* Meal Cards */}
                    <Box
                        sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            p: 2,
                            gap: 2
                        }}
                    >
                        <Paper sx={{ p: 2 }}>
                            {/* Meal Plan Table */}
                            <Typography variant="h5" sx={{ mb: 2 }}>
                                Weekly Meal Plan
                            </Typography>
                            <TableContainer component={Paper}>
                                <Table>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell align="center"></TableCell>
                                            {daysOfWeek.map((day) => (
                                                <TableCell key={day} align="center">
                                                    {day}
                                                </TableCell>
                                            ))}
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {mealTypes.map((mealType) => (
                                            <TableRow key={mealType}>
                                                <TableCell component="th" scope="row">
                                                    <Typography>{mealType}</Typography>
                                                </TableCell>

                                                {daysOfWeek.map((day) => {
                                                    // Find the meal object with the correct meal type
                                                    const meal = NP[day]
                                                        ? Object.values(NP[day]).find((m) => m.meal_type === mealType)
                                                        : null;

                                                    return (
                                                        <TableCell key={`${day}-${mealType}`} align="center">
                                                            <Typography
                                                                sx={{
                                                                    '&:hover': { color: theme.palette.secondary.dark },
                                                                    cursor: 'pointer'
                                                                }}
                                                                onClick={() =>
                                                                    handleMealClick(selectedWeek, day, meal.meal_type, meal.meal_id)
                                                                }
                                                            >
                                                                {meal ? meal.meal_name : '-'}
                                                            </Typography>
                                                        </TableCell>
                                                    );
                                                })}
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                            <Snackbar
                                open={open}
                                autoHideDuration={5000}
                                onClose={handleSnackbarClose}
                                anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
                            >
                                <Alert severity="success" sx={{ width: '100%' }}>
                                    {message}
                                </Alert>
                            </Snackbar>
                        </Paper>
                    </Box>
                </CardWrapper>
            )}
        </>
    );
};

WeeklyMeals.propTypes = {
    isLoading: PropTypes.bool
};

export default WeeklyMeals;
