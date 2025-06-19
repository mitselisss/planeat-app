import React, { useState, useEffect } from 'react';
import { Grid, Typography, Collapse, Button, Box, Table, TableHead, TableRow, TableCell, TableBody } from '@mui/material';
import { useTheme, styled } from '@mui/material/styles';

import MainCard from 'ui-component/cards/MainCard';
import LevelChart from './levelChart';

import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';

import { getDecodedToken } from 'utils/tokenUtils';
import { getUserAchievments } from 'services/api';
import { getUserActionAchievments } from 'services/api';

const LevelCard = () => {
    const theme = useTheme();
    const [expanded, setExpanded] = useState(false);
    const [isFetchingData, setIsFetchingData] = useState(false);
    const [achievments, setAchievments] = useState();
    const [actionAchievments, setActionAchievments] = useState();
    const decodedToken = getDecodedToken();
    const handleToggle = () => setExpanded((prev) => !prev);

    const levels = [
        { points: 0, badges: 0 },
        { points: 100, badges: 3 },
        { points: 300, badges: 7 },
        { points: 600, badges: 10 },
        { points: 1000, badges: 18 }
    ];

    useEffect(() => {
        const fetchData = async () => {
            setIsFetchingData(true);

            try {
                const [userAchievements, userActionAchievements] = await Promise.all([
                    getUserAchievments(decodedToken.user_id),
                    getUserActionAchievments(decodedToken.user_id)
                ]);

                // console.log(userActionAchievements);

                setAchievments(userAchievements);
                setActionAchievments(userActionAchievements); // Make sure this state exists
            } catch (error) {
                console.log(error.response?.data?.error || 'An unexpected error occurred');
            }

            setIsFetchingData(false);
        };

        fetchData();
    }, []);

    return (
        <MainCard>
            {achievments && (
                <>
                    <Grid>
                        <Typography variant="h4" color={theme.palette.success.dark}>
                            NEXT LEVEL
                        </Typography>
                    </Grid>

                    <Grid>
                        <LevelChart levels={levels} achievements={achievments} />
                    </Grid>

                    <Grid>
                        <Typography variant="body2" align="center">
                            To reach the next level you need to earn the following <span style={{ fontWeight: 'bold' }}>points</span> and{' '}
                            <span style={{ fontWeight: 'bold' }}>badges</span>:
                        </Typography>
                    </Grid>

                    <Grid container mt={1}>
                        <Grid item xs={6} md={6}>
                            <Typography align="center">
                                Points:{' '}
                                <span style={{ color: theme.palette.success.dark }}>
                                    {levels[achievments.level].points - achievments.points >= 0
                                        ? levels[achievments.level].points - achievments.points
                                        : 0}
                                </span>
                            </Typography>
                        </Grid>
                        <Grid item xs={6} md={6}>
                            <Typography align="center">
                                Badges:{' '}
                                <span style={{ color: theme.palette.success.dark }}>
                                    {levels[achievments.level].badges - achievments.badges.length >= 0
                                        ? levels[achievments.level].badges - achievments.badges.length
                                        : 0}
                                </span>
                            </Typography>
                        </Grid>
                    </Grid>

                    <Box mt={5} display="flex" justifyContent="center">
                        <Button
                            variant="outlined"
                            size="small"
                            onClick={handleToggle}
                            endIcon={expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        >
                            Points history
                        </Button>
                    </Box>

                    <Collapse in={expanded} timeout="auto" unmountOnExit>
                        <Box mt={2} p={2} bgcolor={theme.palette.success[100]} borderRadius={2}>
                            {actionAchievments && actionAchievments.length > 0 ? (
                                <Box sx={{ overflowX: 'auto' }}>
                                    <Table sx={{ minWidth: 650 }}>
                                        <TableHead>
                                            <TableRow>
                                                <TableCell>
                                                    <Typography color={theme.palette.success.dark}>Action</Typography>
                                                </TableCell>
                                                <TableCell>
                                                    <Typography color={theme.palette.success.dark}>Reason</Typography>
                                                </TableCell>
                                                <TableCell>
                                                    <Typography color={theme.palette.success.dark}>Date (MM/DD/YY)</Typography>
                                                </TableCell>
                                                <TableCell>
                                                    <Typography color={theme.palette.success.dark}>Points</Typography>
                                                </TableCell>
                                            </TableRow>
                                        </TableHead>
                                        <TableBody>
                                            {actionAchievments.map((item, index) => (
                                                <TableRow key={index}>
                                                    <TableCell>{item.action}</TableCell>
                                                    <TableCell>{item.reason}</TableCell>
                                                    <TableCell>
                                                        {new Date(item.date).toLocaleDateString('en-US', {
                                                            year: '2-digit',
                                                            month: '2-digit',
                                                            day: '2-digit'
                                                        })}
                                                    </TableCell>
                                                    <TableCell>{item.points}</TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </Box>
                            ) : (
                                <Typography>No achievements yet.</Typography>
                            )}
                        </Box>
                    </Collapse>
                </>
            )}
        </MainCard>
    );
};

export default LevelCard;
