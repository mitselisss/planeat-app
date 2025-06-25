import React, { useState, useEffect } from 'react';

// material-ui
import { Avatar, Box, Grid, Menu, MenuItem, TextField, Typography, Alert, Snackbar } from '@mui/material';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
import { styled, useTheme } from '@mui/material/styles';
// import { IconShoppingBagPlus } from '@tabler/icons-react';

// project imports
import MainCard from 'ui-component/cards/MainCard';
import { getDecodedToken } from 'utils/tokenUtils';
import { formatDate } from 'utils/formatDate';
import { fetchWeeklyNPs, fetchUserWeeks, fetchWeeklyNP, createNPs, addShoppingList } from 'services/api';
import { getCurrentDayAndWeekDates } from 'utils/getCurrentDayAndWeekDates';
import { downloadWeeklyPlan } from 'utils/downloadWeeklyPlan';
import { checkWeek } from 'utils/checkWeek';
import { userActions } from 'services/api';

import MoreHorizIcon from '@mui/icons-material/MoreHoriz';
import SkeletonMealPlan from 'ui-component/cards/Skeleton/MealPlan/MealPlan';
import EventNoteIcon from '@mui/icons-material/EventNote';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import PictureAsPdfTwoToneIcon from '@mui/icons-material/PictureAsPdfOutlined';
import AddShoppingCartIcon from '@mui/icons-material/AddShoppingCart';

// types
import PropTypes from 'prop-types';

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

const MealsWeekly = ({
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
    const [messageQueue, setMessageQueue] = useState([]);

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

    const handleWeekChange = async (event) => {
        setSelectedWeek(convertDateFormat(event.target.value));

        try {
            const MealsResponse = await fetchWeeklyNPs(decodedToken.user_id, convertDateFormat(event.target.value));
            // console.log(MealsResponse);
            setNP(MealsResponse);
            // setRatio(MealsResponse.meal_0.ratio);
            // mealId(-1);
        } catch (error) {
            // setError(error.response?.data?.error || 'An unexpected error occurred');
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }
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

    const handlePDFclick = async () => {
        downloadWeeklyPlan(NP, convertDateFormat(selectedWeek));
        let achievements;
        try {
            achievements = await userActions(decodedToken.user_id, 'download_weekly_plan');
        } catch (error) {
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }
        addMessages(achievements?.data?.feedback);

        handleClose();
    };

    const handleWeeklyShoppingList = async () => {
        // Logic for creating weekly shopping list

        // Flatten all meals for the week into one array
        const body = [];

        Object.keys(NP).forEach((day) => {
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
            // setShoppingList(addShopping);
            setMessage('Weekly shopping list successfully created.');
            setOpen(true);
        } catch (error) {
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }

        handleClose();
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
                                        onClick={handleWeeklyShoppingList}
                                        disabled={!selectedWeek || checkWeek(convertDateFormatReverse(selectedWeek))}
                                    >
                                        <AddShoppingCartIcon sx={{ mr: 1.75 }} /> Create Weekly Shopping List
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
                            gap: 2,
                            width: '100%'
                        }}
                    >
                        <Paper sx={{ p: 2, width: '100%' }}>
                            <Typography variant="h5" sx={{ mb: 2 }}>
                                Weekly Meal Plan
                            </Typography>

                            {/* Responsive Scrollable Table */}
                            <Box sx={{ overflowX: 'auto' }}>
                                <TableContainer>
                                    <Table sx={{ minWidth: 700 }}>
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
                                                                        handleMealClick(selectedWeek, day, meal?.meal_type, meal?.meal_id)
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
                            </Box>

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
                    <Box
                        sx={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            p: 2,
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

MealsWeekly.propTypes = {
    isLoading: PropTypes.bool
};

export default MealsWeekly;
