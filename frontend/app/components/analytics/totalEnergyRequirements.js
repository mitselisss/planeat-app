import { useEffect, useState } from 'react';

// material-ui
import { useTheme, styled } from '@mui/material/styles';
import { Avatar, Box, TextField, MenuItem, List, ListItem, ListItemAvatar, ListItemText, Typography } from '@mui/material';

// project imports
import MainCard from 'ui-component/cards/MainCard';
import TotalIncomeCard from 'ui-component/cards/Skeleton/TotalIncomeCard';
import { getDecodedToken } from 'utils/tokenUtils';
import { getCurrentDayAndWeekDates } from 'utils/getCurrentDayAndWeekDates';

// assets
import StorefrontTwoToneIcon from '@mui/icons-material/StorefrontTwoTone';

// types
import PropTypes from 'prop-types';

import { formatDate } from 'utils/formatDate';
import { fetchUserWeeks } from 'services/api';
import { fetchNPsAnalytics } from 'services/api';

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

// ==============================|| DASHBOARD - TOTAL INCOME LIGHT CARD ||============================== //

const TotalEnergyRequirements = ({ isLoading, setSelectedWeek }) => {
    const theme = useTheme();
    const decodedToken = getDecodedToken();
    const [analytics, setAnalytics] = useState();
    const [isFetchingData, setIsFetchingData] = useState(false);

    const [NPsWeeks, setNPsWeeks] = useState({});
    const [selectedWeekLocal, setSelectedWeekLocal] = useState();

    useEffect(() => {
        const { currday, currMondayDate, currSundayDate } = getCurrentDayAndWeekDates();

        setSelectedWeekLocal(currMondayDate);
        setSelectedWeek(currMondayDate);

        const fetchData = async () => {
            setIsFetchingData(true);
            try {
                const NPsWeeksResponse = await fetchUserWeeks(decodedToken.user_id);
                setNPsWeeks(NPsWeeksResponse);
                try {
                    const NPsAnalytics = await fetchNPsAnalytics(decodedToken.user_id, currMondayDate);
                    setAnalytics(NPsAnalytics);
                } catch (error) {
                    console.log(error.response?.data?.error || 'An unexpected error occurred');
                }
            } catch (error) {
                console.log(error.response?.data?.error || 'An unexpected error occurred');
            }
            setIsFetchingData(false);
        };

        fetchData();
    }, []);

    const handleWeekChange = async (event) => {
        setSelectedWeekLocal(convertDateFormat(event.target.value));
        setSelectedWeek(convertDateFormat(event.target.value));

        setIsFetchingData(true);
        try {
            const NPsAnalytics = await fetchNPsAnalytics(decodedToken.user_id, convertDateFormat(event.target.value));
            setAnalytics(NPsAnalytics);
        } catch (error) {
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }
        setIsFetchingData(false);
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

    return (
        <>
            {isLoading || isFetchingData ? (
                <TotalIncomeCard />
            ) : (
                <CardWrapper border={false} content={false}>
                    <Box sx={{ p: 2 }}>
                        <List sx={{ py: 0 }}>
                            <ListItem alignItems="center" disableGutters sx={{ py: 0 }}>
                                <ListItemAvatar>
                                    <Avatar
                                        variant="rounded"
                                        sx={{
                                            ...theme.typography.commonAvatar,
                                            ...theme.typography.largeAvatar,
                                            backgroundColor: theme.palette.success[100],
                                            color: theme.palette.success[200]
                                        }}
                                    >
                                        <StorefrontTwoToneIcon fontSize="inherit" />
                                    </Avatar>
                                </ListItemAvatar>
                                <ListItemText
                                    sx={{
                                        py: 0,
                                        mt: 0.45,
                                        mb: 0.45
                                    }}
                                    primary={
                                        <Typography variant="h4" color={theme.palette.success.dark}>
                                            {Math.round(analytics?.user_enegy_intake)} kcal
                                        </Typography>
                                    }
                                    secondary={
                                        <Typography
                                            variant="subtitle2"
                                            sx={{
                                                color: theme.palette.grey[500],
                                                mt: 0.5
                                            }}
                                        >
                                            Daily Energy Requirements
                                        </Typography>
                                    }
                                />
                                <TextField
                                    id="standard-select-currency"
                                    select
                                    value={selectedWeekLocal ? `${convertDateFormatReverse(selectedWeekLocal)}` : ''}
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
                            </ListItem>
                        </List>
                    </Box>
                </CardWrapper>
            )}
        </>
    );
};

TotalEnergyRequirements.propTypes = {
    isLoading: PropTypes.bool
};

export default TotalEnergyRequirements;
