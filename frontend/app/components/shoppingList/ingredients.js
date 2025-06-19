import React, { useEffect, useState } from 'react';
import MainCard from 'ui-component/cards/MainCard';

import { styled, useTheme } from '@mui/material/styles';

// material-ui
import { Grid, Box, Button, Typography, Snackbar, Alert } from '@mui/material';
import { List, ListItem, ListItemText, Divider } from '@mui/material';
import { getShoppingListIngredients } from 'services/api';
import { getCurrentDayAndWeekDates } from 'utils/getCurrentDayAndWeekDates';
import { getDecodedToken } from 'utils/tokenUtils';
import { userActions } from 'services/api';
import { downloadShoppingList } from 'utils/downloadShoppingList';

import PictureAsPdfTwoToneIcon from '@mui/icons-material/PictureAsPdfOutlined';

import SkeletonShoppingList from 'ui-component/cards/Skeleton/ShoppingList/ShoppingList';

// styles
const CardWrapper = styled(MainCard)(({ theme }) => ({
    overflow: 'hidden',
    position: 'relative',
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

const Ingredinets = ({ isLoading, isFetchingData, setIsFetchingData, deleteFlag, setDeleteFlag }) => {
    const theme = useTheme();
    const decodedToken = getDecodedToken();
    const [ingredients, setIngredients] = useState();
    const [open, setOpen] = React.useState(false);
    const [messageQueue, setMessageQueue] = useState([]);
    const [message, setMessage] = useState();

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
        fetchData();
    }, [deleteFlag]);

    // Function to fetch meal data
    const fetchData = async () => {
        const { currday, currMondayDate, currSundayDate } = getCurrentDayAndWeekDates();

        setIsFetchingData(true);

        try {
            const getShoppinListIngredinets = await getShoppingListIngredients(decodedToken.user_id, currMondayDate);
            // console.log(getShoppinListIngredinets);

            const grouped = getShoppinListIngredinets.reduce((acc, item) => {
                const category = item.category || 'Uncategorized'; // default if no category
                if (!acc[category]) {
                    acc[category] = [];
                }
                acc[category].push(item);
                return acc;
            }, {});

            console.log(grouped);

            setIngredients(grouped);
            setDeleteFlag(false);
        } catch (error) {
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }

        setIsFetchingData(false);
    };

    // Split categories into two halves for layout
    const splitCategories = (obj) => {
        const entries = Object.entries(obj || {});

        // Sort categories to try to distribute large categories more evenly
        const sorted = entries.sort((a, b) => b[1].length - a[1].length);

        const left = [];
        const right = [];
        let leftCount = 0;
        let rightCount = 0;

        for (const [category, items] of sorted) {
            if (leftCount <= rightCount) {
                left.push([category, items]);
                leftCount += items.length;
            } else {
                right.push([category, items]);
                rightCount += items.length;
            }
        }

        return [left, right];
    };

    const handleDownload = async () => {
        downloadShoppingList(ingredients);
        let achievements;
        try {
            achievements = await userActions(decodedToken.user_id, 'download_shopping_list');
        } catch (error) {
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }
        addMessages(achievements?.data?.feedback);
    };

    const [leftColumn, rightColumn] = splitCategories(ingredients);

    const handleSnackbarClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }
        setOpen(false);
    };

    return (
        <>
            {isLoading || isFetchingData ? (
                <SkeletonShoppingList />
            ) : (
                <CardWrapper>
                    <Grid container sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Typography variant="h3" color={theme.palette.success.dark}>
                            Shopping List
                        </Typography>
                        {ingredients && Object.keys(ingredients).length !== 0 && (
                            <Button
                                variant="outlined"
                                color="success"
                                startIcon={<PictureAsPdfTwoToneIcon />}
                                onClick={handleDownload} // <-- Your download handler function
                            >
                                Download
                            </Button>
                        )}
                    </Grid>
                    <Grid container marginTop={2}>
                        <Grid item xs={12} md={6}>
                            {leftColumn.map(([category, items], index) => (
                                <Grid
                                    sx={{
                                        // backgroundColor: theme.palette.success[100],
                                        margin: 2
                                    }}
                                    key={index}
                                >
                                    <Typography variant="body1" sx={{ fontStyle: 'italic', mb: 1 }}>
                                        {category}
                                    </Typography>
                                    <List dense>
                                        {items.map((item, i) => (
                                            <React.Fragment key={i}>
                                                <ListItem
                                                    secondaryAction={
                                                        <Typography variant="subtitle2">{Math.round(item.quantity)} g</Typography>
                                                    }
                                                >
                                                    <ListItemText primary={<Typography variant="subtitle2">{item.name}</Typography>} />
                                                </ListItem>
                                                {i < items.length - 1 && <Divider component="li" />}
                                            </React.Fragment>
                                        ))}
                                    </List>
                                </Grid>
                            ))}
                        </Grid>
                        <Grid item xs={12} md={6}>
                            {rightColumn.map(([category, items], index) => (
                                <Grid
                                    sx={{
                                        // backgroundColor: theme.palette.success[100],
                                        margin: 2
                                    }}
                                    key={index}
                                >
                                    <Typography variant="body1" sx={{ fontStyle: 'italic', mb: 1 }}>
                                        {category}
                                    </Typography>
                                    <List dense>
                                        {items.map((item, i) => (
                                            <React.Fragment key={i}>
                                                <ListItem
                                                    secondaryAction={
                                                        <Typography variant="subtitle2">{Math.round(item.quantity)} g</Typography>
                                                    }
                                                >
                                                    <ListItemText primary={<Typography variant="subtitle2">{item.name}</Typography>} />
                                                </ListItem>
                                                {i < items.length - 1 && <Divider component="li" />}
                                            </React.Fragment>
                                        ))}
                                    </List>
                                </Grid>
                            ))}
                        </Grid>
                    </Grid>
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
                </CardWrapper>
            )}
        </>
    );
};

export default Ingredinets;
