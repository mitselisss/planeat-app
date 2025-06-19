import { useEffect, useState } from 'react';
import { Grid, Typography, ListItemText } from '@mui/material';

import { useTheme } from '@mui/material/styles';
import MainCard from 'ui-component/cards/MainCard';
import { getUserAchievments } from 'services/api';
import { getDecodedToken } from 'utils/tokenUtils';

import SkeletonShoppingList from 'ui-component/cards/Skeleton/ShoppingList/ShoppingList';

import level1 from '../../assets/images/levels/Level1.png';
import level2 from '../../assets/images/levels/Level2.jpg';
import level3 from '../../assets/images/levels/Level3.jpg';
import level4 from '../../assets/images/levels/Level4.jpg';
import level5 from '../../assets/images/levels/Level5.jpg';

const CurrentState = () => {
    const theme = useTheme();
    const decodedToken = getDecodedToken();
    const [achievments, setAchievments] = useState();
    const [isFetchingData, setIsFetchingData] = useState(false);

    const levels = {
        1: level1,
        2: level2,
        3: level3,
        4: level4,
        5: level5
    };

    useEffect(() => {
        const fetchData = async () => {
            setIsFetchingData(true);

            try {
                const userAchievments = await getUserAchievments(decodedToken.user_id);
                setAchievments(userAchievments);
                // console.log(userAchievments);
            } catch (error) {
                console.log(error.response?.data?.error || 'An unexpected error occurred');
            }

            setIsFetchingData(false);
        };

        fetchData();
    }, []);

    return (
        <>
            {isFetchingData ? (
                <SkeletonShoppingList />
            ) : (
                <MainCard>
                    {achievments && (
                        <Grid container spacing={2} alignItems="center">
                            {/* Left: Image */}
                            <Grid item xs={3} md={3} textAlign="center">
                                <img src={levels[achievments.level]} width={90} height={90} alt="level" />
                                {/* <Typography>Beginner</Typography> */}
                            </Grid>

                            {/* Center: Points and Badges */}
                            <Grid item xs={9} md={9}>
                                <Grid container justifyContent="center" spacing={2}>
                                    <Grid item xs={4} md={4}>
                                        <ListItemText
                                            primary={
                                                <Typography variant="subtitle2" align="center" fontSize="1.1rem">
                                                    Points
                                                </Typography>
                                            }
                                            secondary={
                                                <Typography mt={1} variant="h2" color={theme.palette.success.dark} align="center">
                                                    {achievments.points}
                                                </Typography>
                                            }
                                        />
                                    </Grid>
                                    <Grid item xs={4} md={4}>
                                        <ListItemText
                                            primary={
                                                <Typography variant="subtitle2" align="center" fontSize="1.1rem">
                                                    Badges
                                                </Typography>
                                            }
                                            secondary={
                                                <Typography mt={1} variant="h2" color={theme.palette.success.dark} align="center">
                                                    {achievments.badges.length}
                                                </Typography>
                                            }
                                        />
                                    </Grid>
                                    <Grid item xs={4} md={4}>
                                        <ListItemText
                                            primary={
                                                <Typography variant="subtitle2" align="center" fontSize="1.1rem">
                                                    Trails
                                                </Typography>
                                            }
                                            secondary={
                                                <Typography mt={1} variant="h2" color={theme.palette.success.dark} align="center">
                                                    {achievments.trails.length}
                                                </Typography>
                                            }
                                        />
                                    </Grid>
                                </Grid>
                            </Grid>
                        </Grid>
                    )}
                </MainCard>
            )}
        </>
    );
};

export default CurrentState;
