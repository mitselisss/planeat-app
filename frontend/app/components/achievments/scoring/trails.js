import React, { useEffect, useState } from 'react';
import MainCard from 'ui-component/cards/MainCard';
import { Grid, Box, Typography, Tooltip, List, ListItem, ListItemText } from '@mui/material';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import HikingIcon from '@mui/icons-material/Hiking';
import ExploreIcon from '@mui/icons-material/Explore';
import MilitaryTechIcon from '@mui/icons-material/MilitaryTech';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

// material-ui
import { useTheme, styled } from '@mui/material/styles';

// styles
const CardWrapper = styled(MainCard)(({ theme }) => ({
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

const Trails = ({ achievements }) => {
    const theme = useTheme();
    const trailsList = ['planeat_hiker', 'planeat_explorer', 'planeat_ranger'];
    const badgesList = [
        'login/getting_started',
        'login/habit_builder',
        'login/committed_streaker',
        'analytics/data_glancer',
        'analytics/insight_seeker',
        'analytics/analytics_master',
        'meal_suggestions/first_bite',
        'meal_suggestions/routine_rookie',
        'meal_suggestions/healthy_habit',
        'meal_suggestions_advanced/week_one_warrior',
        'meal_suggestions_advanced/double_week_devotee',
        'meal_suggestions_advanced/four_week_champion',
        'download_weekly_plan/planner_in_progress',
        'download_weekly_plan/strategic_eater',
        'download_weekly_plan/plan_mastermind',
        'download_shopping_list/list_soldier',
        'download_shopping_list/kitchen_commander',
        'download_shopping_list/grocery_general'
    ];
    const [earned, setEarned] = useState(Array(badgesList.length).fill(false));
    const [earnedTrails, setEarnedTrails] = useState(Array(trailsList.length).fill(false));

    useEffect(() => {
        if (achievements?.badges) {
            const earnedStatuses = badgesList.map((badge) => achievements.badges.includes(badge));
            setEarned(earnedStatuses);
        }
        if (achievements?.trails) {
            const trailStatuses = trailsList.map((trail) => achievements.trails.includes(trail));
            setEarnedTrails(trailStatuses);
        }
    }, [achievements]);

    return (
        <Grid container spacing={2} direction="column">
            <Grid item container spacing={2} mt={2}>
                <Grid item md={12}>
                    <CardWrapper>
                        {earnedTrails[0] && (
                            <CheckCircleIcon
                                style={{
                                    color: '#4caf50',
                                    position: 'absolute',
                                    top: 0,
                                    right: 0,
                                    fontSize: 40,
                                    backgroundColor: 'white',
                                    borderRadius: '50%',
                                    padding: 4
                                }}
                            />
                        )}
                        <Grid container spacing={2} alignItems="center">
                            <Grid item>
                                <HikingIcon style={{ fontSize: 40, color: '#cd7f32' }} /> {/* Bronze */}
                            </Grid>
                            <Grid item xs>
                                <Typography fontWeight="bold" color={theme.palette.success.dark}>
                                    PLANEAT Hiker
                                </Typography>
                                <Typography variant="subtitle2" fontStyle="italic">
                                    Start your journey in the planEat world by getting a taste of healthy habits and smart planning.
                                </Typography>
                            </Grid>
                        </Grid>
                        <Box my={4} />
                        <Grid container spacing={2} justifyContent="space-between">
                            <Grid item>
                                <Tooltip
                                    title={
                                        earned[0] ? (
                                            <Typography>
                                                You've earned this badge!{' '}
                                                <Typography fontStyle="italic">Log in on 3 seperate days.</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">Log in on 3 seperate days to earn this badge</Typography>
                                        )
                                    }
                                >
                                    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center">
                                        <EmojiEventsIcon style={{ fontSize: 60, color: '#cd7f32' }} /> {/* Bronze */}
                                        {earned[0] && (
                                            <VerifiedUserIcon
                                                style={{
                                                    color: '#4caf50',
                                                    position: 'absolute',
                                                    fontSize: 25,
                                                    backgroundColor: 'white',
                                                    borderRadius: '50%'
                                                }}
                                            />
                                        )}
                                        <Typography variant="subtitle2" align="center">
                                            Getting Started
                                        </Typography>
                                    </Box>
                                </Tooltip>
                            </Grid>
                            <Grid item>
                                <Tooltip
                                    title={
                                        earned[3] ? (
                                            <Typography>
                                                You've earned this badge!{' '}
                                                <Typography fontStyle="italic">Visit the Analytics page on 3 separate days</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">
                                                Visit the Analytics page on 3 separate days to earn this badge
                                            </Typography>
                                        )
                                    }
                                >
                                    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center">
                                        <EmojiEventsIcon style={{ fontSize: 60, color: '#cd7f32' }} /> {/* Bronze */}
                                        {earned[3] && (
                                            <VerifiedUserIcon
                                                style={{
                                                    color: '#4caf50',
                                                    position: 'absolute',
                                                    fontSize: 25,
                                                    backgroundColor: 'white',
                                                    borderRadius: '50%'
                                                }}
                                            />
                                        )}
                                        <Typography variant="subtitle2" align="center">
                                            Data Glancer
                                        </Typography>
                                    </Box>
                                </Tooltip>
                            </Grid>
                            <Grid item>
                                <Tooltip
                                    title={
                                        earned[6] ? (
                                            <Typography>
                                                You've earned this badge!{' '}
                                                <Typography fontStyle="italic">Mark 1 proposed meal as eaten</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">Mark 1 proposed meal as eaten</Typography>
                                        )
                                    }
                                >
                                    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center">
                                        <EmojiEventsIcon style={{ fontSize: 60, color: '#cd7f32' }} /> {/* Bronze */}
                                        {earned[6] && (
                                            <VerifiedUserIcon
                                                style={{
                                                    color: '#4caf50',
                                                    position: 'absolute',
                                                    fontSize: 25,
                                                    backgroundColor: 'white',
                                                    borderRadius: '50%'
                                                }}
                                            />
                                        )}
                                        <Typography variant="subtitle2" align="center">
                                            First Bite
                                        </Typography>
                                    </Box>
                                </Tooltip>
                            </Grid>
                            <Grid item>
                                <Tooltip
                                    title={
                                        earned[9] ? (
                                            <Typography>
                                                You've earned this badge!{' '}
                                                <Typography fontStyle="italic">Mark 30 meals as eaten in 1 week</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">Mark 30 meals as eaten in 1 week</Typography>
                                        )
                                    }
                                >
                                    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center">
                                        <EmojiEventsIcon style={{ fontSize: 60, color: '#cd7f32' }} /> {/* Bronze */}
                                        {earned[9] && (
                                            <VerifiedUserIcon
                                                style={{
                                                    color: '#4caf50',
                                                    position: 'absolute',
                                                    fontSize: 25,
                                                    backgroundColor: 'white',
                                                    borderRadius: '50%'
                                                }}
                                            />
                                        )}
                                        <Box textAlign="center">
                                            <Typography variant="subtitle2">Week One</Typography>
                                            <Typography variant="subtitle2">Warrior</Typography>
                                        </Box>
                                    </Box>
                                </Tooltip>
                            </Grid>
                            <Grid item>
                                <Tooltip
                                    title={
                                        earned[12] ? (
                                            <Typography>
                                                You've earned this badge! <Typography fontStyle="italic">Download weekly plan</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">Download weekly plan</Typography>
                                        )
                                    }
                                >
                                    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center">
                                        <EmojiEventsIcon style={{ fontSize: 60, color: '#cd7f32' }} /> {/* Bronze */}
                                        {earned[12] && (
                                            <VerifiedUserIcon
                                                style={{
                                                    color: '#4caf50',
                                                    position: 'absolute',
                                                    fontSize: 25,
                                                    backgroundColor: 'white',
                                                    borderRadius: '50%'
                                                }}
                                            />
                                        )}
                                        <Box textAlign="center">
                                            <Typography variant="subtitle2">Planner in</Typography>
                                            <Typography variant="subtitle2">Progress</Typography>
                                        </Box>
                                    </Box>
                                </Tooltip>
                            </Grid>
                            <Grid item>
                                <Tooltip
                                    title={
                                        earned[15] ? (
                                            <Typography>
                                                You've earned this badge!{' '}
                                                <Typography fontStyle="italic">Download the shopping list on 3 seperate days</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">Download the shopping list on 3 seperate days</Typography>
                                        )
                                    }
                                >
                                    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center">
                                        <EmojiEventsIcon style={{ fontSize: 60, color: '#cd7f32' }} /> {/* Bronze */}
                                        {earned[15] && (
                                            <VerifiedUserIcon
                                                style={{
                                                    color: '#4caf50',
                                                    position: 'absolute',
                                                    fontSize: 25,
                                                    backgroundColor: 'white',
                                                    borderRadius: '50%'
                                                }}
                                            />
                                        )}
                                        <Typography variant="subtitle2" align="center">
                                            List Soldier
                                        </Typography>
                                    </Box>
                                </Tooltip>
                            </Grid>
                        </Grid>
                    </CardWrapper>
                </Grid>
            </Grid>

            <Grid item container spacing={2}>
                <Grid item md={12}>
                    <CardWrapper>
                        {earnedTrails[1] && (
                            <CheckCircleIcon
                                style={{
                                    color: '#4caf50',
                                    position: 'absolute',
                                    top: 0,
                                    right: 0,
                                    fontSize: 40,
                                    backgroundColor: 'white',
                                    borderRadius: '50%',
                                    padding: 4
                                }}
                            />
                        )}
                        <Grid container spacing={2} alignItems="center">
                            <Grid item>
                                <ExploreIcon style={{ fontSize: 40, color: '#c0c0c0' }} /> {/* Bronze */}
                            </Grid>
                            <Grid item xs>
                                <Typography fontWeight="bold" color={theme.palette.success.dark}>
                                    PLANEAT Explorer
                                </Typography>
                                <Typography variant="subtitle2" fontStyle="italic">
                                    You’re building momentum in the planEat lifestyle — balanced meals, steady habits, and thoughtful prep.
                                    Stay consistent and level up your planning game.
                                </Typography>
                            </Grid>
                        </Grid>
                        <Box my={4} />
                        <Grid container spacing={2} justifyContent="space-between">
                            <Grid item>
                                <Tooltip
                                    title={
                                        earned[1] ? (
                                            <Typography>
                                                You've earned this badge!{' '}
                                                <Typography fontStyle="italic">Log in on 10 seperate days.</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">Log in on 10 seperate days to earn this badge</Typography>
                                        )
                                    }
                                >
                                    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center">
                                        <EmojiEventsIcon style={{ fontSize: 60, color: '#c0c0c0' }} /> {/* Silver */}
                                        {earned[1] && (
                                            <VerifiedUserIcon
                                                style={{
                                                    color: '#4caf50',
                                                    position: 'absolute',
                                                    fontSize: 25,
                                                    backgroundColor: 'white',
                                                    borderRadius: '50%'
                                                }}
                                            />
                                        )}
                                        <Typography variant="subtitle2" align="center">
                                            Habit Builder
                                        </Typography>
                                    </Box>
                                </Tooltip>
                            </Grid>
                            <Grid item>
                                <Tooltip
                                    title={
                                        earned[4] ? (
                                            <Typography>
                                                You've earned this badge!{' '}
                                                <Typography fontStyle="italic">Visit the Analytics page on 10 separate days</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">
                                                Visit the Analytics page on 10 separate days to earn this badge
                                            </Typography>
                                        )
                                    }
                                >
                                    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center">
                                        <EmojiEventsIcon style={{ fontSize: 60, color: '#c0c0c0' }} /> {/* Silver */}
                                        {earned[4] && (
                                            <VerifiedUserIcon
                                                style={{
                                                    color: '#4caf50',
                                                    position: 'absolute',
                                                    fontSize: 25,
                                                    backgroundColor: 'white',
                                                    borderRadius: '50%'
                                                }}
                                            />
                                        )}
                                        <Typography variant="subtitle2" align="center">
                                            Insight Seeker
                                        </Typography>
                                    </Box>
                                </Tooltip>
                            </Grid>
                            <Grid item>
                                <Tooltip
                                    title={
                                        earned[7] ? (
                                            <Typography>
                                                You've earned this badge!{' '}
                                                <Typography fontStyle="italic">Mark 30 proposed meals as eaten</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">Mark 30 proposed meals as eaten</Typography>
                                        )
                                    }
                                >
                                    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center">
                                        <EmojiEventsIcon style={{ fontSize: 60, color: '#c0c0c0' }} /> {/* Silver */}
                                        {earned[7] && (
                                            <VerifiedUserIcon
                                                style={{
                                                    color: '#4caf50',
                                                    position: 'absolute',
                                                    fontSize: 25,
                                                    backgroundColor: 'white',
                                                    borderRadius: '50%'
                                                }}
                                            />
                                        )}
                                        <Typography variant="subtitle2" align="center">
                                            Routine Rookie
                                        </Typography>
                                    </Box>
                                </Tooltip>
                            </Grid>
                            <Grid item>
                                <Tooltip
                                    title={
                                        earned[10] ? (
                                            <Typography>
                                                You've earned this badge!{' '}
                                                <Typography fontStyle="italic">Mark 60 meals as eaten in 1 week</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">Mark 60 meals as eaten in 1 week</Typography>
                                        )
                                    }
                                >
                                    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center">
                                        <EmojiEventsIcon style={{ fontSize: 60, color: '#c0c0c0' }} /> {/* Silver */}
                                        {earned[10] && (
                                            <VerifiedUserIcon
                                                style={{
                                                    color: '#4caf50',
                                                    position: 'absolute',
                                                    fontSize: 25,
                                                    backgroundColor: 'white',
                                                    borderRadius: '50%'
                                                }}
                                            />
                                        )}
                                        <Box textAlign="center">
                                            <Typography variant="subtitle2">Double Week</Typography>
                                            <Typography variant="subtitle2">Devotee</Typography>
                                        </Box>
                                    </Box>
                                </Tooltip>
                            </Grid>
                            <Grid item>
                                <Tooltip
                                    title={
                                        earned[13] ? (
                                            <Typography>
                                                You've earned this badge!{' '}
                                                <Typography fontStyle="italic">Download weekly plan on 2 seperate weeks</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">Download weekly plan on 2 seperate weeks</Typography>
                                        )
                                    }
                                >
                                    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center">
                                        <EmojiEventsIcon style={{ fontSize: 60, color: '#c0c0c0' }} /> {/* Silver */}
                                        {earned[13] && (
                                            <VerifiedUserIcon
                                                style={{
                                                    color: '#4caf50',
                                                    position: 'absolute',
                                                    fontSize: 25,
                                                    backgroundColor: 'white',
                                                    borderRadius: '50%'
                                                }}
                                            />
                                        )}
                                        <Typography variant="subtitle2" align="center">
                                            Strategic Eater
                                        </Typography>
                                    </Box>
                                </Tooltip>
                            </Grid>
                            <Grid item>
                                <Tooltip
                                    title={
                                        earned[16] ? (
                                            <Typography>
                                                You've earned this badge!{' '}
                                                <Typography fontStyle="italic">Download the shopping list on 6 seperate days</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">Download the shopping list on 6 seperate days</Typography>
                                        )
                                    }
                                >
                                    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center">
                                        <EmojiEventsIcon style={{ fontSize: 60, color: '#c0c0c0' }} /> {/* Silver */}
                                        {earned[16] && (
                                            <VerifiedUserIcon
                                                style={{
                                                    color: '#4caf50',
                                                    position: 'absolute',
                                                    fontSize: 25,
                                                    backgroundColor: 'white',
                                                    borderRadius: '50%'
                                                }}
                                            />
                                        )}
                                        <Box textAlign="center">
                                            <Typography variant="subtitle2">Kitchen</Typography>
                                            <Typography variant="subtitle2">Commander</Typography>
                                        </Box>
                                    </Box>
                                </Tooltip>
                            </Grid>
                        </Grid>
                    </CardWrapper>
                </Grid>
            </Grid>

            <Grid item container spacing={2}>
                <Grid item md={12}>
                    <CardWrapper>
                        {earnedTrails[2] && (
                            <CheckCircleIcon
                                style={{
                                    color: '#4caf50',
                                    position: 'absolute',
                                    top: 0,
                                    right: 0,
                                    fontSize: 40,
                                    backgroundColor: 'white',
                                    borderRadius: '50%',
                                    padding: 4
                                }}
                            />
                        )}
                        <Grid container spacing={2} alignItems="center">
                            <Grid item>
                                <MilitaryTechIcon style={{ fontSize: 40, color: '#ffd700' }} /> {/* Bronze */}
                            </Grid>
                            <Grid item xs>
                                <Typography fontWeight="bold" color={theme.palette.success.dark}>
                                    PLANEAT Ranger
                                </Typography>
                                <Typography variant="subtitle2" fontStyle="italic">
                                    Become a ranger in the planEat world — consistent, strategic, and fully in control of your food journey.
                                </Typography>
                            </Grid>
                        </Grid>
                        <Box my={3} />
                        <Grid container spacing={2} justifyContent="space-between">
                            <Grid item>
                                <Tooltip
                                    title={
                                        earned[2] ? (
                                            <Typography>
                                                You've earned this badge!{' '}
                                                <Typography fontStyle="italic">Log in on 30 seperate days.</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">Log in on 30 seperate days to earn this badge</Typography>
                                        )
                                    }
                                >
                                    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center">
                                        <EmojiEventsIcon style={{ fontSize: 60, color: '#ffd700' }} /> {/* Gold */}
                                        {earned[2] && (
                                            <VerifiedUserIcon
                                                style={{
                                                    color: '#4caf50',
                                                    position: 'absolute',
                                                    fontSize: 25,
                                                    backgroundColor: 'white',
                                                    borderRadius: '50%'
                                                }}
                                            />
                                        )}
                                        <Box textAlign="center">
                                            <Typography variant="subtitle2">Committed</Typography>
                                            <Typography variant="subtitle2">Streaker</Typography>
                                        </Box>
                                    </Box>
                                </Tooltip>
                            </Grid>
                            <Grid item>
                                <Tooltip
                                    title={
                                        earned[5] ? (
                                            <Typography>
                                                You've earned this badge!{' '}
                                                <Typography fontStyle="italic">Visit the Analytics page on 30 separate days</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">
                                                Visit the Analytics page on 30 separate days to earn this badge
                                            </Typography>
                                        )
                                    }
                                >
                                    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center">
                                        <EmojiEventsIcon style={{ fontSize: 60, color: '#ffd700' }} /> {/* Gold */}
                                        {earned[5] && (
                                            <VerifiedUserIcon
                                                style={{
                                                    color: '#4caf50',
                                                    position: 'absolute',
                                                    fontSize: 25,
                                                    backgroundColor: 'white',
                                                    borderRadius: '50%'
                                                }}
                                            />
                                        )}
                                        <Box textAlign="center">
                                            <Typography variant="subtitle2">Analytics</Typography>
                                            <Typography variant="subtitle2">Master</Typography>
                                        </Box>
                                    </Box>
                                </Tooltip>
                            </Grid>
                            <Grid item>
                                <Tooltip
                                    title={
                                        earned[8] ? (
                                            <Typography>
                                                You've earned this badge!{' '}
                                                <Typography fontStyle="italic">Mark 90 proposed meals as eaten</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">Mark 90 proposed meals as eaten</Typography>
                                        )
                                    }
                                >
                                    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center">
                                        <EmojiEventsIcon style={{ fontSize: 60, color: '#ffd700' }} /> {/* Gold */}
                                        {earned[8] && (
                                            <VerifiedUserIcon
                                                style={{
                                                    color: '#4caf50',
                                                    position: 'absolute',
                                                    fontSize: 25,
                                                    backgroundColor: 'white',
                                                    borderRadius: '50%'
                                                }}
                                            />
                                        )}
                                        <Typography variant="subtitle2" align="center">
                                            Healthy Habit
                                        </Typography>
                                    </Box>
                                </Tooltip>
                            </Grid>
                            <Grid item>
                                <Tooltip
                                    title={
                                        earned[11] ? (
                                            <Typography>
                                                You've earned this badge!{' '}
                                                <Typography fontStyle="italic">Mark 120 meals as eaten in 1 week</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">Mark 120 meals as eaten in 1 week</Typography>
                                        )
                                    }
                                >
                                    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center">
                                        <EmojiEventsIcon style={{ fontSize: 60, color: '#ffd700' }} /> {/* Gold */}
                                        {earned[11] && (
                                            <VerifiedUserIcon
                                                style={{
                                                    color: '#4caf50',
                                                    position: 'absolute',
                                                    fontSize: 25,
                                                    backgroundColor: 'white',
                                                    borderRadius: '50%'
                                                }}
                                            />
                                        )}
                                        <Box textAlign="center">
                                            <Typography variant="subtitle2">Four Week</Typography>
                                            <Typography variant="subtitle2">Champion</Typography>
                                        </Box>
                                    </Box>
                                </Tooltip>
                            </Grid>
                            <Grid item>
                                <Tooltip
                                    title={
                                        earned[14] ? (
                                            <Typography>
                                                You've earned this badge!{' '}
                                                <Typography fontStyle="italic">Download weekly plan on 4 seperate weeks</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">Download weekly plan on 4 seperate weeks</Typography>
                                        )
                                    }
                                >
                                    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center">
                                        <EmojiEventsIcon style={{ fontSize: 60, color: '#ffd700' }} /> {/* Gold */}
                                        {earned[14] && (
                                            <VerifiedUserIcon
                                                style={{
                                                    color: '#4caf50',
                                                    position: 'absolute',
                                                    fontSize: 25,
                                                    backgroundColor: 'white',
                                                    borderRadius: '50%'
                                                }}
                                            />
                                        )}
                                        <Typography variant="subtitle2" align="center">
                                            Plan Mastermind
                                        </Typography>
                                    </Box>
                                </Tooltip>
                            </Grid>
                            <Grid item>
                                <Tooltip
                                    title={
                                        earned[17] ? (
                                            <Typography>
                                                You've earned this badge!{' '}
                                                <Typography fontStyle="italic">Download the shopping list on 12 seperate days</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">Download the shopping list on 12 seperate days</Typography>
                                        )
                                    }
                                >
                                    <Box display="flex" flexDirection="column" justifyContent="center" alignItems="center">
                                        <EmojiEventsIcon style={{ fontSize: 60, color: '#ffd700' }} /> {/* Gold */}
                                        {earned[17] && (
                                            <VerifiedUserIcon
                                                style={{
                                                    color: '#4caf50',
                                                    position: 'absolute',
                                                    fontSize: 25,
                                                    backgroundColor: 'white',
                                                    borderRadius: '50%'
                                                }}
                                            />
                                        )}
                                        <Typography variant="subtitle2" align="center">
                                            Grocery General
                                        </Typography>
                                    </Box>
                                </Tooltip>
                            </Grid>
                        </Grid>
                    </CardWrapper>
                </Grid>
            </Grid>
        </Grid>
    );
};

export default Trails;
