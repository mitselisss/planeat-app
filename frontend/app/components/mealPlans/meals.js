import React, { useState, useEffect } from 'react';
import { useLocation } from '@remix-run/react';

// material-ui
import {
    Avatar,
    Box,
    Grid,
    Menu,
    IconButton,
    MenuItem,
    TextField,
    Typography,
    Card,
    CardContent,
    Checkbox,
    FormHelperText,
    Tooltip,
    Alert,
    Button,
    Snackbar
} from '@mui/material';
import { styled, useTheme } from '@mui/material/styles';
// import { IconShoppingBagPlus } from '@tabler/icons-react';

// project imports
import MainCard from 'ui-component/cards/MainCard';
import { getDecodedToken } from 'utils/tokenUtils';
import { formatDate } from 'utils/formatDate';
import {
    fetchDailyNP,
    fetchUserWeeks,
    fetchWeeklyNP,
    fetchWeeklyNPs,
    createNPs,
    getShoppingList,
    addShoppingList,
    removeShoppingList,
    getEatenList,
    addEatenList,
    removeEatenList
} from 'services/api';
import { getCurrentDayAndWeekDates } from 'utils/getCurrentDayAndWeekDates';
import { checkDay } from 'utils/checkDay';
import { checkWeek } from 'utils/checkWeek';
import { downloadWeeklyPlan } from 'utils/downloadWeeklyPlan';
import { userActions } from 'services/api';

import MoreHorizIcon from '@mui/icons-material/MoreHoriz';
import SkeletonMealPlan from 'ui-component/cards/Skeleton/MealPlan/MealPlan';
import EventNoteIcon from '@mui/icons-material/EventNote';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import PictureAsPdfTwoToneIcon from '@mui/icons-material/PictureAsPdfOutlined';
import AddShoppingCartIcon from '@mui/icons-material/AddShoppingCart';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import TaskAltIcon from '@mui/icons-material/TaskAlt';
import RestaurantMenuIcon from '@mui/icons-material/RestaurantMenu';

// types
import PropTypes from 'prop-types';
// styles
const CardWrapper = styled(MainCard)(({ theme }) => ({
    backgroundColor: theme.palette.success.light,
    overflow: 'hidden',
    position: 'relative',
    '&:after': {
        content: '""',
        position: 'absolute',
        width: 210,
        height: 210,
        background: `linear-gradient(210.04deg, ${theme.palette.success[300]} -50.94%, rgba(144, 202, 249, 0) 83.49%)`,
        borderRadius: '50%',
        top: -30,
        right: -180
    },
    '&:before': {
        content: '""',
        position: 'absolute',
        width: 210,
        height: 210,
        background: `linear-gradient(140.9deg, ${theme.palette.success[300]} -14.02%, rgba(144, 202, 249, 0) 70.50%)`,
        borderRadius: '50%',
        top: -160,
        right: -130
    }
}));

const Meals = ({
    isLoading,
    isFetchingData,
    setIsFetchingData,
    mealId,
    setRatio,
    setWeekly,
    weekly,
    setWeeklyMealSelection,
    weeklyMealSelection
}) => {
    const theme = useTheme();
    const decodedToken = getDecodedToken();
    const location = useLocation();
    const label = { inputProps: { 'aria-label': 'Checkbox demo' } };
    const [anchorEl, setAnchorEl] = useState(null);
    const [currDay, setCurrDay] = useState();
    const [NP, setNP] = useState({});
    const [NPsWeeks, setNPsWeeks] = useState({});
    const [selectedDay, setSelectedDay] = useState();
    const [selectedWeek, setSelectedWeek] = useState();
    const [selectedMealId, setSelectedMealId] = useState();
    const [shoppingList, setShoppingList] = useState([]);
    const [eatenList, setEatenList] = useState([]);
    const [disableShoppingList, setDisableShoppingList] = useState(false);
    const [disableEatenList, setDisableEatenList] = useState(false);
    const [open, setOpen] = React.useState(false);
    const [messageQueue, setMessageQueue] = useState([]);
    const [message, setMessage] = useState();

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
    const mealOrder = ['Breakfast', 'Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner'];
    const jsDayIndex = new Date().getDay();
    const customDayIndex = jsDayIndex === 0 ? 6 : jsDayIndex - 1;

    // Call this function when you receive new feedback messages
    const addMessages = (messages) => {
        if (messages && messages.length > 0) {
            setMessageQueue((prevQueue) => [...prevQueue, ...messages]);
        }
    };

    useEffect(() => {
        if (!open && messageQueue.length > 0) {
            setMessage(messageQueue[0]);
            setMessageQueue((prev) => prev.slice(1));
            setOpen(true);
        }
    }, [messageQueue, open]);

    useEffect(() => {
        const { currday, currMondayDate, currSundayDate } = getCurrentDayAndWeekDates();

        const fetchData = async () => {
            if (Object.keys(weeklyMealSelection).length === 0) {
                // console.log('main');
                main(currday, currMondayDate, currSundayDate);
            } else {
                main2(weeklyMealSelection);
                // console.log('main2');
            }

            try {
                const [getShopping, getEaten] = await Promise.all([
                    getShoppingList(decodedToken.user_id, currMondayDate),
                    getEatenList(decodedToken.user_id, currMondayDate)
                ]);
                setShoppingList(getShopping);
                setEatenList(getEaten);
            } catch (error) {
                console.log(error.response?.data?.error || 'An unexpected error occurred');
            }
        };

        fetchData();
    }, []);

    const main = async (currday, currMondayDate, currSundayDate) => {
        setCurrDay(currday);
        setSelectedDay(days[currday].value);
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
                            fetchDailyNP(decodedToken.user_id, currMondayDate, days[currday].value)
                        ]);

                        // console.log(MealsResponse);

                        // Set the state if the response is successful
                        setNPsWeeks(NPsWeeksResponse); // NPsWeeksResponse contains the data directly
                        setNP(MealsResponse); // MealsResponse contains the data directly
                        setRatio(MealsResponse.meal_0.ratio);
                        setSelectedMealId(MealsResponse.meal_0.meal_id);
                        handleMealClick(currMondayDate, days[currday].value, MealsResponse.meal_0.meal_type, MealsResponse.meal_0.meal_id);
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
                                fetchDailyNP(decodedToken.user_id, currMondayDate, days[currday].value) // Call fetchDailyNP with userId, date, and day
                            ]);

                            // Set the state if the response is successful
                            setNPsWeeks(NPsWeeksResponse); // NPsWeeksResponse contains the data directly
                            setNP(MealsResponse); // MealsResponse contains the data directly
                            setRatio(MealsResponse.meal_0.ratio);
                            setSelectedMealId(MealsResponse.meal_0.meal_id);
                            handleMealClick(
                                currMondayDate,
                                days[currday].value,
                                MealsResponse.meal_0.meal_type,
                                MealsResponse.meal_0.meal_id
                            );
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
    };

    const main2 = async (weeklyMealSelection) => {
        console.log(weeklyMealSelection);
        setCurrDay(daysOfWeek.indexOf(weeklyMealSelection.day));
        setSelectedDay(weeklyMealSelection.day);
        setSelectedWeek(weeklyMealSelection.week);

        const fetchData = async () => {
            setIsFetchingData(true);

            if (checkWeek(convertDateFormat(weeklyMealSelection.week))) {
                setDisableShoppingList(checkWeek(convertDateFormat(weeklyMealSelection.week)));
                setDisableEatenList(checkWeek(convertDateFormat(weeklyMealSelection.week)));
            } else {
                setDisableShoppingList(checkDay(daysOfWeek.indexOf(weeklyMealSelection.day)));
                setDisableEatenList(daysOfWeek.indexOf(weeklyMealSelection.day) !== customDayIndex);
            }

            try {
                // Using the custom fetch functions
                const [NPsWeeksResponse, MealsResponse] = await Promise.all([
                    fetchUserWeeks(decodedToken.user_id),
                    fetchDailyNP(decodedToken.user_id, weeklyMealSelection.week, weeklyMealSelection.day)
                ]);

                // console.log(MealsResponse);

                // Set the state if the response is successful
                setNPsWeeks(NPsWeeksResponse); // NPsWeeksResponse contains the data directly
                setNP(MealsResponse); // MealsResponse contains the data directly
                setRatio(MealsResponse.meal_0.ratio);
                setSelectedMealId(weeklyMealSelection.meal_id);
                handleMealClick(
                    weeklyMealSelection.week,
                    weeklyMealSelection.day,
                    weeklyMealSelection.meal_type,
                    weeklyMealSelection.meal_id
                );
            } catch (error) {
                // Handle error
                console.log(error.response?.data?.error || 'An unexpected error occurred');
            }

            setIsFetchingData(false);
        };

        fetchData();
    };

    const handleWeekChange = async (event) => {
        setSelectedWeek(convertDateFormat(event.target.value));
        const jsDayIndex = new Date().getDay();
        const customDayIndex = jsDayIndex === 0 ? 6 : jsDayIndex - 1;
        // setSelectedMealId(null);

        if (checkWeek(event.target.value)) {
            setDisableShoppingList(checkWeek(event.target.value));
            setDisableEatenList(checkWeek(event.target.value));
        } else {
            setDisableShoppingList(checkDay(currDay));
            setDisableEatenList(currDay !== customDayIndex);
        }

        try {
            const MealsResponse = await fetchDailyNP(decodedToken.user_id, convertDateFormat(event.target.value), selectedDay);
            // console.log(MealsResponse);
            setNP(MealsResponse);
            setRatio(MealsResponse.meal_0.ratio);
            setSelectedMealId(MealsResponse.meal_0.meal_id);
            handleMealClick(
                convertDateFormat(event.target.value),
                selectedDay,
                MealsResponse.meal_0.meal_type,
                MealsResponse.meal_0.meal_id
            );
            // mealId(-1);
        } catch (error) {
            // setError(error.response?.data?.error || 'An unexpected error occurred');
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }
    };

    const handleDayChange = async (event) => {
        // console.log(event.target.value);
        setSelectedDay(event.target.value); // Get the selected day's value
        const dayIndex = days.findIndex((day) => day.value === event.target.value); // Find the index of the selected day
        setCurrDay(dayIndex); // Update currDay with the index

        // setSelectedMealId(null);

        if (checkWeek(convertDateFormatReverse(selectedWeek)) === false) {
            setDisableShoppingList(checkDay(dayIndex));
            setDisableEatenList(dayIndex !== customDayIndex);
        }

        try {
            const MealsResponse = await fetchDailyNP(decodedToken.user_id, selectedWeek, event.target.value);
            // console.log(MealsResponse);
            setNP(MealsResponse);
            setRatio(MealsResponse.meal_0.ratio);
            setSelectedMealId(MealsResponse.meal_0.meal_id);
            handleMealClick(selectedWeek, event.target.value, MealsResponse.meal_0.meal_type, MealsResponse.meal_0.meal_id);
            // mealId(-1);
        } catch (error) {
            // setError(error.response?.data?.error || 'An unexpected error occurred');
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }

        // console.log(disableShoppingList);
    };

    const handleTodayButton = async () => {
        const { currday, currMondayDate, currSundayDate } = getCurrentDayAndWeekDates();

        setCurrDay(currday);
        setSelectedDay(days[currday].value);
        setSelectedWeek(currMondayDate);

        setDisableShoppingList(false);
        setDisableEatenList(false);

        // setSelectedMealId(null);

        try {
            const MealsResponse = await fetchDailyNP(decodedToken.user_id, currMondayDate, days[currday].value);
            // console.log(MealsResponse);
            setNP(MealsResponse);
            setRatio(MealsResponse.meal_0.ratio);
            setSelectedMealId(MealsResponse.meal_0.meal_id);
            handleMealClick(currMondayDate, days[currday].value, MealsResponse.meal_0.meal_type, MealsResponse.meal_0.meal_id);
            // mealId(-1);
        } catch (error) {
            // setError(error.response?.data?.error || 'An unexpected error occurred');
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }

        // console.log('selectedMealiD', selectedMealId);
    };

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
        mealId(meal_id); // Send selected meal to parent
        setSelectedMealId(meal_id);
    };

    // -------------- Eaten List Functionalities --------------------- //

    const handleEatenCheck = (selectedWeek, selectedDay, type, meal_id) => {
        if (checkEatenList(selectedWeek, selectedDay, type, meal_id)) {
            // console.log('remove');
            removeMealEatenList(selectedWeek, selectedDay, type, meal_id);
        } else {
            // console.log('add');
            addMealEatenList(selectedWeek, selectedDay, type, meal_id);
        }
    };

    const checkEatenList = (week, day, type, meal_id) => {
        // console.log(week, day, type, meal_id);
        if (eatenList?.some((item) => item.week === week && item.day === day && item.type === type && item.meal_id === meal_id)) {
            // console.log('true');
            return true;
        } else {
            // console.log('false');
            return false;
        }
    };

    const addMealEatenList = async (week, day, type, meal_id) => {
        // console.log(week, day, type, meal_id);

        const body = [
            {
                meal_id: meal_id,
                day: day,
                type: type
            }
        ];

        try {
            const addEaten = await addEatenList(decodedToken.user_id, week, body);
            setEatenList(addEaten);
            let achievements;
            try {
                achievements = await userActions(decodedToken.user_id, 'add_eaten_meal');
            } catch (error) {
                console.log(error.response?.data?.error || 'An unexpected error occurred');
            }
            addMessages(achievements?.data?.feedback);
        } catch (error) {
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }
    };

    const removeMealEatenList = async (week, day, type, meal_id) => {
        const body = [
            {
                meal_id: meal_id,
                day: day,
                type: type
            }
        ];
        let achievements;
        try {
            const removeEaten = await removeEatenList(decodedToken.user_id, week, body);
            setEatenList(removeEaten);
            try {
                achievements = await userActions(decodedToken.user_id, 'remove_eaten_meal');
            } catch (error) {
                console.log(error.response?.data?.error || 'An unexpected error occurred');
            }
            addMessages(achievements?.data?.feedback);
        } catch (error) {
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }
    };

    // -------------- Shopping List Functionalities --------------------- //

    const checkShoppingList = (week, day, type, meal_id) => {
        if (shoppingList?.some((item) => item.week === week && item.day === day && item.type === type && item.meal_id === meal_id)) {
            return true;
        } else {
            return false;
        }
    };

    const addMealShoppingList = async (week, day, type, meal_id) => {
        // console.log(week, day, type, meal_id);

        const body = [
            {
                meal_id: meal_id,
                day: day,
                type: type
            }
        ];

        try {
            const addShopping = await addShoppingList(decodedToken.user_id, week, body);
            console.log(addShopping);
            setShoppingList(addShopping);
            setMessage('Meal successfully added to the shopping list.');
            // setOpenSucces(true);
            setOpen(true);
            // Hide the message after 3 seconds
            // setTimeout(() => {
            //     setOpenSucces(false);
            // }, 3000);
        } catch (error) {
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }
    };

    const removeMealShoppingList = async (week, day, type, meal_id) => {
        const body = [
            {
                meal_id: meal_id,
                day: day,
                type: type
            }
        ];

        try {
            const removeShopping = await removeShoppingList(decodedToken.user_id, week, body);
            setShoppingList(removeShopping);
            setMessage('Meal successfully removed from the shopping list.');
            // setOpenSucces(true);
            setOpen(true);
            // Hide the message after 3 seconds
            // setTimeout(() => {
            //     setOpenSucces(false);
            // }, 3000);
        } catch (error) {
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }
    };

    // ------------------------------------------------------------- //

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

    const handlePDFclick = async () => {
        try {
            const weeklyNPs = await fetchWeeklyNPs(decodedToken.user_id, selectedWeek);
            downloadWeeklyPlan(weeklyNPs, convertDateFormat(selectedWeek));
            let achievements;
            try {
                achievements = await userActions(decodedToken.user_id, 'download_weekly_plan');
            } catch (error) {
                console.log(error.response?.data?.error || 'An unexpected error occurred');
            }
            addMessages(achievements?.data?.feedback);
        } catch (error) {
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }
        handleClose();
    };

    const handleSelection = async (selection) => {
        // console.log('Selected Option:', selection);
        // You can now handle the specific logic based on the selection:
        if (selection === 'weeklyShoppingList') {
            // Logic for creating weekly shopping list

            // Flatten all meals for the week into one array
            const body = [];

            try {
                // Using the custom fetch functions
                const MealsResponse = await fetchWeeklyNPs(decodedToken.user_id, selectedWeek);

                // console.log(MealsResponse);

                Object.keys(MealsResponse).forEach((day) => {
                    const mealsForDay = NP[day];
                    if (mealsForDay) {
                        Object.values(mealsForDay).forEach((meal) => {
                            body.push({
                                meal_id: meal.meal_id,
                                day: day,
                                type: meal.meal_type
                            });
                        });
                    }
                });

                try {
                    const addShopping = await addShoppingList(decodedToken.user_id, selectedWeek, body);
                    setShoppingList(addShopping);
                    setMessage('Weekly shopping list successfully created.');
                    setOpen(true);
                } catch (error) {
                    console.log(error.response?.data?.error || 'An unexpected error occurred');
                }
            } catch (error) {
                // Handle error
                console.log(error.response?.data?.error || 'An unexpected error occurred');
            }
        } else if (selection === 'dailyShoppingList') {
            // Update shopping list by filtering and adding new items
            const body = [
                {
                    meal_id: NP.meal_0.meal_id,
                    day: selectedDay,
                    type: NP.meal_0.meal_type
                },
                {
                    meal_id: NP.meal_1.meal_id,
                    day: selectedDay,
                    type: NP.meal_1.meal_type
                },
                {
                    meal_id: NP.meal_2.meal_id,
                    day: selectedDay,
                    type: NP.meal_2.meal_type
                },
                {
                    meal_id: NP.meal_3.meal_id,
                    day: selectedDay,
                    type: NP.meal_3.meal_type
                },
                {
                    meal_id: NP.meal_4.meal_id,
                    day: selectedDay,
                    type: NP.meal_4.meal_type
                }
            ];

            try {
                const addShopping = await addShoppingList(decodedToken.user_id, selectedWeek, body);
                setShoppingList(addShopping);
                setMessage('Meals successfully added to the shopping list.');
                setOpen(true);
                // setOpenSucces(true);
                // Hide the message after 3 seconds
                // setTimeout(() => {
                //     setOpenSucces(false);
                // }, 3000);
            } catch (error) {
                console.log(error.response?.data?.error || 'An unexpected error occurred');
            }
        }
        handleClose(); // Close the menu after the selection is made
    };

    const groupedMeals = mealOrder.map((type) => ({
        type,
        meals: Object.values(NP).filter((meal) => meal.meal_type === type)
    }));

    return (
        <>
            {isLoading || isFetchingData ? (
                <SkeletonMealPlan />
            ) : (
                <CardWrapper border={false} content={false}>
                    {/* Day Header */}

                    <Grid container justifyContent="space-between" alignItems="center">
                        {/* Left Section: Days and Calendar */}

                        <Grid item>
                            <Grid container alignItems="center">
                                <Grid item>
                                    <Box
                                        sx={{
                                            textAlign: 'left', // Align the text to the left
                                            pt: 2,
                                            pl: 2,
                                            pb: 2
                                        }}
                                    >
                                        <Avatar
                                            variant="rounded"
                                            sx={{
                                                ...theme.typography.commonAvatar,
                                                ...theme.typography.largeAvatar,
                                                backgroundColor: theme.palette.primary.light,
                                                color: theme.palette.success.dark,
                                                boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.2)',
                                                transition: 'background-color 0.3s ease, box-shadow 0.3s ease', // Add transition for background and shadow
                                                '&:hover': {
                                                    backgroundColor: theme.palette.background.default,
                                                    boxShadow: '0px 4px 15px rgba(0, 0, 0, 0.2)'
                                                }
                                            }}
                                            onClick={() => setWeekly((prevWeekly) => !prevWeekly)}
                                        >
                                            {weekly ? <CalendarMonthIcon fontSize="inherit" /> : <EventNoteIcon fontSize="inherit" />}
                                        </Avatar>
                                    </Box>
                                </Grid>
                                {/* Weeks Select Dropdown */}
                                <Grid item>
                                    <Box
                                        sx={{
                                            textAlign: 'left', // Align the text to the left
                                            pt: 2,
                                            pl: 2,
                                            pb: 2
                                        }}
                                    >
                                        <TextField
                                            id="standard-select-currency"
                                            select
                                            value={selectedWeek ? `${convertDateFormatReverse(selectedWeek)}` : ''}
                                            onChange={handleWeekChange}
                                        >
                                            {Object.values(NPsWeeks).map((week) => (
                                                <MenuItem value={week.start_date}>
                                                    <Typography variant="body1" sx={{ color: theme.palette.success.dark }}>
                                                        {`${formatDate(week.start_date)} - ${formatDate(week.end_date)}`}
                                                    </Typography>
                                                </MenuItem>
                                            ))}
                                        </TextField>
                                    </Box>
                                </Grid>

                                {/* Days Select Dropdown */}
                                <Grid item>
                                    <Box
                                        sx={{
                                            textAlign: 'left', // Align the text to the left
                                            pt: 2,
                                            pl: 2,
                                            pb: 2
                                        }}
                                    >
                                        <TextField
                                            id="standard-select-currency"
                                            select
                                            value={currDay !== undefined && currDay !== null ? days[currDay].value : ''} // Bind the value to the current day's value
                                            onChange={handleDayChange} // Update day on selection
                                        >
                                            {days.map((option) => (
                                                <MenuItem key={option.value} value={option.value}>
                                                    <Typography variant="body1" sx={{ color: theme.palette.success.dark }}>
                                                        {option.label}
                                                    </Typography>
                                                </MenuItem>
                                            ))}
                                        </TextField>
                                    </Box>
                                </Grid>

                                {/* Today Button */}
                                <Grid item>
                                    <Box
                                        sx={{
                                            textAlign: 'left', // Align the text to the left
                                            pt: 2,
                                            pl: 2,
                                            pb: 2
                                        }}
                                    >
                                        <Button
                                            id="today-button"
                                            onClick={handleTodayButton} // Handle the button click
                                            variant="contained" // You can style the button as per your design
                                            sx={{
                                                backgroundColor: theme.palette.primary.light, // Use primary color (you can define this in theme)
                                                color: theme.palette.success.dark, // Change text color
                                                '&:hover': {
                                                    backgroundColor: theme.palette.background.default
                                                },
                                                height: '47px', // Larger height
                                                width: 'auto',
                                                borderRadius: '10px'
                                            }}
                                        >
                                            Today
                                        </Button>
                                    </Box>
                                </Grid>
                            </Grid>
                        </Grid>

                        {/* Right Section: Avatar */}
                        <Grid item>
                            <Box sx={{ display: 'flex', justifyContent: 'flex-end', p: 2 }}>
                                <Avatar
                                    variant="rounded"
                                    sx={{
                                        ...theme.typography.commonAvatar,
                                        ...theme.typography.mediumAvatar,
                                        backgroundColor: theme.palette.primary.light,
                                        color: theme.palette.success.dark,
                                        boxShadow: '0px 2px 8px rgba(0, 0, 0, 0.2)',
                                        transition: 'background-color 0.3s ease, box-shadow 0.3s ease', // Add transition for background and shadow
                                        '&:hover': {
                                            backgroundColor: theme.palette.background.default,
                                            boxShadow: '0px 4px 15px rgba(0, 0, 0, 0.2)'
                                        },
                                        zIndex: 1
                                    }}
                                    aria-controls="menu-earning-card"
                                    aria-haspopup="true"
                                    onClick={handleClick}
                                >
                                    <MoreHorizIcon fontSize="inherit" />
                                </Avatar>
                                <Menu
                                    id="menu-earning-card"
                                    anchorEl={anchorEl}
                                    keepMounted
                                    open={Boolean(anchorEl)}
                                    onClose={handleClose}
                                    variant="selectedMenu"
                                    anchorOrigin={{
                                        vertical: 'bottom',
                                        horizontal: 'right'
                                    }}
                                    transformOrigin={{
                                        vertical: 'top',
                                        horizontal: 'right'
                                    }}
                                >
                                    <MenuItem onClick={handlePDFclick}>
                                        <PictureAsPdfTwoToneIcon sx={{ mr: 1.75 }} /> Download Weekly Plan
                                    </MenuItem>
                                    <MenuItem
                                        onClick={() => handleSelection('weeklyShoppingList')}
                                        disabled={!selectedWeek || checkWeek(convertDateFormatReverse(selectedWeek))}
                                    >
                                        <AddShoppingCartIcon sx={{ mr: 1.75 }} /> Create Weekly Shopping List
                                    </MenuItem>
                                    <MenuItem
                                        onClick={() => handleSelection('dailyShoppingList')}
                                        disabled={!selectedWeek || checkWeek(convertDateFormatReverse(selectedWeek)) || checkDay(currDay)}
                                    >
                                        <AddShoppingCartIcon sx={{ mr: 1.75 }} /> Create Daily Shopping List
                                    </MenuItem>
                                </Menu>
                            </Box>
                        </Grid>
                    </Grid>

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
                        {NP?.meal_0 ? (
                            <Typography color={theme.palette.error.main}>
                                {NP.meal_0.valid
                                    ? ''
                                    : 'Due to limited meal options for this user profile, the generated daily plan does not meet the nutritional and diversity requirements.'}
                            </Typography>
                        ) : null}
                        {groupedMeals.map(({ type, meals }) => (
                            <Grid
                                key={type}
                                sx={{
                                    width: '100%',
                                    maxWidth: 600
                                }}
                            >
                                {meals.map((meal) => (
                                    <Card
                                        sx={{
                                            width: '100%',
                                            maxWidth: 600,
                                            boxShadow: theme.shadows[1],
                                            // border: '1px solid',
                                            // borderColor:
                                            //     selectedMealId === meal.meal_id ? theme.palette.secondary.main : theme.palette.background.default,
                                            bgcolor:
                                                selectedMealId === meal.meal_id
                                                    ? theme.palette.secondary.light
                                                    : theme.palette.background.default,
                                            transition: 'background-color 0.3s ease'
                                        }}
                                    >
                                        <CardContent>
                                            <Typography variant="h5" color={theme.palette.success.dark} gutterBottom>
                                                {meal.meal_type}
                                            </Typography>
                                            <Box
                                                sx={{
                                                    display: 'flex', // Flexbox layout
                                                    alignItems: 'center', // Vertically align items
                                                    justifyContent: 'space-between', // Adjust spacing between items
                                                    gap: 1 // Optional: Add space between items
                                                }}
                                            >
                                                <Typography
                                                    variant="body2"
                                                    color={selectedMealId === meal.meal_id ? theme.palette.secondary.dark : 'inherit'}
                                                    sx={{
                                                        transition: 'color 0.3s ease', // Smooth transition for color change
                                                        '&:hover': {
                                                            color: theme.palette.secondary.dark, // Change color on hover
                                                            cursor: 'pointer' // Add pointer cursor for interactivity
                                                        }
                                                    }}
                                                    onClick={() => handleMealClick(selectedWeek, selectedDay, meal.meal_type, meal.meal_id)}
                                                >
                                                    {meal.meal_name}
                                                </Typography>
                                                <Grid
                                                    sx={{
                                                        display: 'flex', // Make items in the row layout
                                                        alignItems: 'center' // Vertically align checkbox and icon
                                                    }}
                                                >
                                                    <Tooltip
                                                        title={
                                                            disableShoppingList
                                                                ? ''
                                                                : checkEatenList(selectedWeek, selectedDay, meal.meal_type, meal.meal_id)
                                                                ? 'Uncheck if you did not eat this meal.'
                                                                : 'Check only if you have eaten this meal.'
                                                        }
                                                    >
                                                        <Checkbox
                                                            {...label}
                                                            // sx={{
                                                            //     color: theme.palette.success.dark,
                                                            //     '&.Mui-checked': {
                                                            //         color: theme.palette.success[300]
                                                            //     }
                                                            // }}
                                                            disabled={disableEatenList}
                                                            checked={checkEatenList(
                                                                selectedWeek,
                                                                selectedDay,
                                                                meal.meal_type,
                                                                meal.meal_id
                                                            )}
                                                            icon={<RestaurantMenuIcon />}
                                                            checkedIcon={<TaskAltIcon />}
                                                            color="success"
                                                            onClick={() => {
                                                                handleEatenCheck(selectedWeek, selectedDay, meal.meal_type, meal.meal_id);
                                                            }}
                                                        />
                                                    </Tooltip>
                                                    <Tooltip
                                                        title={
                                                            disableShoppingList
                                                                ? ''
                                                                : checkShoppingList(selectedWeek, selectedDay, meal.meal_type, meal.meal_id)
                                                                ? 'Remove from the shopping list'
                                                                : 'Add to the shopping list.'
                                                        }
                                                    >
                                                        <span>
                                                            <IconButton
                                                                disabled={disableShoppingList}
                                                                onClick={() => {
                                                                    if (
                                                                        checkShoppingList(
                                                                            selectedWeek,
                                                                            selectedDay,
                                                                            meal.meal_type,
                                                                            meal.meal_id
                                                                        )
                                                                    ) {
                                                                        removeMealShoppingList(
                                                                            selectedWeek,
                                                                            selectedDay,
                                                                            meal.meal_type,
                                                                            meal.meal_id
                                                                        );
                                                                    } else {
                                                                        addMealShoppingList(
                                                                            selectedWeek,
                                                                            selectedDay,
                                                                            meal.meal_type,
                                                                            meal.meal_id
                                                                        );
                                                                    }
                                                                }}
                                                            >
                                                                {checkShoppingList(
                                                                    selectedWeek,
                                                                    selectedDay,
                                                                    meal.meal_type,
                                                                    meal.meal_id
                                                                ) ? (
                                                                    <ShoppingCartIcon
                                                                        sx={{
                                                                            color: disableShoppingList
                                                                                ? theme.palette.text.disabled
                                                                                : theme.palette.success.dark
                                                                        }}
                                                                    />
                                                                ) : (
                                                                    <AddShoppingCartIcon
                                                                        sx={{
                                                                            color: disableShoppingList
                                                                                ? theme.palette.text.disabled
                                                                                : 'inherit'
                                                                        }}
                                                                    />
                                                                )}
                                                            </IconButton>
                                                            <Snackbar
                                                                open={open}
                                                                autoHideDuration={4000}
                                                                onClose={handleSnackbarClose}
                                                                anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
                                                            >
                                                                <Alert severity="success" sx={{ width: '100%' }}>
                                                                    {message}
                                                                </Alert>
                                                            </Snackbar>
                                                        </span>
                                                    </Tooltip>
                                                </Grid>
                                            </Box>
                                        </CardContent>
                                    </Card>
                                ))}
                            </Grid>
                        ))}
                    </Box>

                    <Box
                        sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            px: 5,
                            py: 2,
                            gap: 2
                        }}
                    >
                        <Typography
                            variant="subtitle2"
                            sx={{
                                textAlign: 'justify',
                                fontStyle: 'italic'
                            }}
                        >
                            "Please note that these menus are designed for the nutritional needs of the general population. If you are
                            pregnant, breastfeeding or need to follow a special diet, consult a health professional."
                        </Typography>
                    </Box>
                </CardWrapper>
            )}
        </>
    );
};

Meals.propTypes = {
    isLoading: PropTypes.bool
};

export default Meals;
