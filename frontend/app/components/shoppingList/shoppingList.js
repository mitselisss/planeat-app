import React, { useEffect, useState } from 'react';
import MainCard from 'ui-component/cards/MainCard';

// Material-UI components
import { Grid, Typography, Box, List, ListItem, ListItemText, IconButton, Divider, Button } from '@mui/material';
import { useTheme } from '@mui/material/styles';

import { getDecodedToken } from 'utils/tokenUtils';
import { getCurrentDayAndWeekDates } from 'utils/getCurrentDayAndWeekDates';
import { getShoppingList, removeShoppingList } from 'services/api';

import SkeletonShoppingList from 'ui-component/cards/Skeleton/ShoppingList/ShoppingList';

// Icons
import DeleteIcon from '@mui/icons-material/Delete';

const ShoppingList = ({ isLoading, isFetchingData, setIsFetchingData, setDeleteFlag }) => {
    const theme = useTheme();
    const decodedToken = getDecodedToken();
    const [shoppingList, setShoppingList] = useState([]);
    const [currDay, setCurrDay] = useState();

    const dayToNumber = {
        Monday: 0,
        Tuesday: 1,
        Wednesday: 2,
        Thursday: 3,
        Friday: 4,
        Saturday: 5,
        Sunday: 6
    };

    useEffect(() => {
        fetchData();
    }, []);

    // Function to fetch meal data
    const fetchData = async () => {
        const { currday, currMondayDate, currSundayDate } = getCurrentDayAndWeekDates();
        setCurrDay(currday);

        setIsFetchingData(true);

        try {
            const getShoppinList = await getShoppingList(decodedToken.user_id, currMondayDate);
            // console.log(getShoppinList);
            setShoppingList(getShoppinList);
        } catch (error) {
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }
        setIsFetchingData(false);
    };

    // Function to delete an item
    const handleDelete = async (item) => {
        const body = [
            {
                meal_id: item.meal_id,
                day: item.day,
                type: item.type
            }
        ];

        console.log(body);

        try {
            const removeShopping = await removeShoppingList(decodedToken.user_id, item.week, body);
            setShoppingList(removeShopping);
        } catch (error) {
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }

        setDeleteFlag(true);
    };

    const handleRemoveAll = async () => {
        const body = shoppingList.map((item) => ({
            meal_id: item.meal_id,
            day: item.day,
            type: item.type
        }));

        console.log(body);

        try {
            const removeShopping = await removeShoppingList(decodedToken.user_id, shoppingList[0].week, body);
            setShoppingList(removeShopping);
        } catch (error) {
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }

        setDeleteFlag(true);
    };

    const handleClearOld = async () => {
        const body = shoppingList
            .filter((item) => dayToNumber[item.day] < currDay)
            .map((item) => ({
                meal_id: item.meal_id,
                day: item.day,
                type: item.type
            }));

        console.log(body);

        try {
            const removeShopping = await removeShoppingList(decodedToken.user_id, shoppingList[0].week, body);
            setShoppingList(removeShopping);
        } catch (error) {
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }

        setDeleteFlag(true);
    };

    const getFormattedDate = (week, day) => {
        // Parse the week (which is the Monday's date)
        const weekDate = new Date(week);

        // Mapping of weekdays to indices (0 - Monday, ..., 6 - Sunday)
        const weekdayMap = {
            Monday: 0,
            Tuesday: 1,
            Wednesday: 2,
            Thursday: 3,
            Friday: 4,
            Saturday: 5,
            Sunday: 6
        };

        // Get the current day index (0 - Monday, ..., 6 - Sunday)
        const targetDayIndex = weekdayMap[day];

        // Calculate the difference between the target day and Monday
        const dayDifference = targetDayIndex - 0; // 0 is Monday now, so no adjustment needed

        // Adjust the date of `weekDate` to match the correct day
        weekDate.setDate(weekDate.getDate() + dayDifference);

        // Format the date into "Day, DD-MM-YYYY"
        const options = { weekday: 'long', year: 'numeric', month: '2-digit', day: '2-digit' };
        return weekDate.toLocaleDateString('en-GB', options); // Use en-GB for DD/MM/YYYY format
    };

    // Group shopping list by formatted date
    const groupAndSortByFormattedDate = () => {
        const grouped = shoppingList.reduce((groups, item) => {
            const formattedDate = getFormattedDate(item.week, item.day);

            if (!groups[formattedDate]) {
                groups[formattedDate] = [];
            }

            groups[formattedDate].push(item);
            return groups;
        }, {});

        // Sort the groups by date
        const sortedGrouped = Object.keys(grouped)
            .sort((a, b) => {
                // Convert formatted date strings into Date objects
                const dateA = new Date(a.split(', ')[1]);
                const dateB = new Date(b.split(', ')[1]);

                // Sort in ascending order (change to dateB - dateA for descending order)
                return dateA - dateB;
            })
            .reduce((sortedGroups, date) => {
                sortedGroups[date] = grouped[date];
                return sortedGroups;
            }, {});

        // console.log(sortedGrouped);
        return sortedGrouped;
    };

    const groupedShoppingList = groupAndSortByFormattedDate();

    return (
        <>
            {isLoading || isFetchingData ? (
                <SkeletonShoppingList />
            ) : (
                <MainCard>
                    <Grid container spacing={2}>
                        <Grid item xs={12}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Typography variant="h3" color={theme.palette.success.dark}>
                                    Meals
                                </Typography>
                                {shoppingList?.length > 0 && (
                                    <Box sx={{ display: 'flex', gap: 2 }}>
                                        <Button
                                            variant="outlined"
                                            color="inherit"
                                            onClick={() => handleClearOld()}
                                            disabled={shoppingList.filter((item) => dayToNumber[item.day] < currDay) <= 0}
                                        >
                                            Clear Old
                                        </Button>
                                        <Button variant="outlined" color="error" onClick={() => handleRemoveAll()}>
                                            Remove All
                                        </Button>
                                    </Box>
                                )}
                            </Box>
                        </Grid>

                        <Grid item xs={12} mt={3}>
                            {Object.keys(groupedShoppingList).length > 0 ? (
                                Object.keys(groupedShoppingList).map((formattedDate) => (
                                    <div key={formattedDate}>
                                        <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                                            <Typography variant="body" sx={{ fontStyle: 'italic' }}>
                                                {formattedDate}
                                            </Typography>
                                        </Box>
                                        <List>
                                            {groupedShoppingList[formattedDate].map((item, index) => (
                                                <React.Fragment key={index}>
                                                    <ListItem
                                                        alignItems="flex-start"
                                                        secondaryAction={
                                                            <IconButton
                                                                edge="end"
                                                                sx={{
                                                                    color: dayToNumber[item.day] < currDay ? 'text.inherit' : 'error.main'
                                                                }}
                                                                onClick={() => handleDelete(item)}
                                                            >
                                                                <DeleteIcon />
                                                            </IconButton>
                                                        }
                                                    >
                                                        <ListItemText
                                                            primary={
                                                                <Typography
                                                                    variant="h5"
                                                                    sx={{
                                                                        textDecoration:
                                                                            dayToNumber[item.day] < currDay ? 'line-through' : 'none',
                                                                        color:
                                                                            dayToNumber[item.day] < currDay
                                                                                ? 'text.disabled'
                                                                                : 'text.primary'
                                                                    }}
                                                                >
                                                                    {item.meal_name}
                                                                </Typography>
                                                            }
                                                            secondary={
                                                                <>
                                                                    <Typography variant="subtitle2" color="textSecondary">
                                                                        {item.type}
                                                                    </Typography>
                                                                </>
                                                            }
                                                        />
                                                    </ListItem>
                                                    {index < groupedShoppingList[formattedDate].length - 1 && <Divider />}
                                                </React.Fragment>
                                            ))}
                                        </List>
                                    </div>
                                ))
                            ) : (
                                <Typography color={theme.palette.error.dark}>Oops! Looks like your shopping list is empty.</Typography>
                            )}
                        </Grid>
                    </Grid>
                </MainCard>
            )}
        </>
    );
};

export default ShoppingList;
