import React, { useEffect, useState } from 'react';
import MainCard from 'ui-component/cards/MainCard';
import { Grid, Box, Typography, Tooltip } from '@mui/material';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';

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

const Badges = ({ achievements }) => {
    // console.log(achievements?.badges);
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

    useEffect(() => {
        if (achievements?.badges) {
            const earnedStatuses = badgesList.map((badge) => achievements.badges.includes(badge));
            setEarned(earnedStatuses);
        }
    }, [achievements]);

    const theme = useTheme();
    return (
        <Grid container spacing={2} direction="column">
            <Grid item container spacing={2} mt={2}>
                <Grid item md={6}>
                    <CardWrapper>
                        <Grid>
                            <Typography color={theme.palette.success.dark} fontWeight="bold">
                                Login
                            </Typography>
                        </Grid>
                        <Box my={3} />
                        <Grid container spacing={2}>
                            <Grid item md={4}>
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
                            <Grid item md={4}>
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
                            <Grid item md={4}>
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
                                        <Typography variant="subtitle2" align="center">
                                            Committed Streaker
                                        </Typography>
                                    </Box>
                                </Tooltip>
                            </Grid>
                        </Grid>
                    </CardWrapper>
                </Grid>
                <Grid item md={6}>
                    <CardWrapper>
                        <Grid>
                            <Typography color={theme.palette.success.dark} fontWeight="bold">
                                Analytics
                            </Typography>
                        </Grid>
                        <Box my={3} />
                        <Grid container spacing={2}>
                            <Grid item md={4}>
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
                            <Grid item md={4}>
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
                            <Grid item md={4}>
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
                                        <Typography variant="subtitle2" align="center">
                                            Analytics Master
                                        </Typography>
                                    </Box>
                                </Tooltip>
                            </Grid>
                        </Grid>
                    </CardWrapper>
                </Grid>
            </Grid>

            <Grid item container spacing={2}>
                <Grid item md={6}>
                    <CardWrapper>
                        <Grid>
                            <Typography color={theme.palette.success.dark} fontWeight="bold">
                                Meal Suggestions
                            </Typography>
                        </Grid>
                        <Box my={3} />
                        <Grid container spacing={2}>
                            <Grid item md={4}>
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
                            <Grid item md={4}>
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
                            <Grid item md={4}>
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
                        </Grid>
                    </CardWrapper>
                </Grid>
                <Grid item md={6}>
                    <CardWrapper>
                        <Grid>
                            <Typography color={theme.palette.success.dark} fontWeight="bold">
                                Meals Suggestions - Advanced
                            </Typography>
                        </Grid>
                        <Box my={3} />
                        <Grid container spacing={2}>
                            <Grid item md={4}>
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
                                        <Typography variant="subtitle2" align="center">
                                            Week One Warrior
                                        </Typography>
                                    </Box>
                                </Tooltip>
                            </Grid>
                            <Grid item md={4}>
                                <Tooltip
                                    title={
                                        earned[10] ? (
                                            <Typography>
                                                You've earned this badge!{' '}
                                                <Typography fontStyle="italic">Mark 60 meals as eaten in 2 weeks</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">Mark 60 meals as eaten in 2 weeks</Typography>
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
                                        <Typography variant="subtitle2" align="center">
                                            Double Week Devotee
                                        </Typography>
                                    </Box>
                                </Tooltip>
                            </Grid>
                            <Grid item md={4}>
                                <Tooltip
                                    title={
                                        earned[11] ? (
                                            <Typography>
                                                You've earned this badge!{' '}
                                                <Typography fontStyle="italic">Mark 120 meals as eaten in 4 weeks</Typography>
                                            </Typography>
                                        ) : (
                                            <Typography fontStyle="italic">Mark 120 meals as eaten in 4 weeks</Typography>
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
                                        <Typography variant="subtitle2" align="center">
                                            Four Week Champion
                                        </Typography>
                                    </Box>
                                </Tooltip>
                            </Grid>
                        </Grid>
                    </CardWrapper>
                </Grid>
            </Grid>

            <Grid item container spacing={2}>
                <Grid item md={6}>
                    <CardWrapper>
                        <Grid>
                            <Typography color={theme.palette.success.dark} fontWeight="bold">
                                Weekly Plan
                            </Typography>
                        </Grid>
                        <Box my={3} />
                        <Grid container spacing={2}>
                            <Grid item md={4}>
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
                                        <Typography variant="subtitle2" align="center">
                                            Planner in Progress
                                        </Typography>
                                    </Box>
                                </Tooltip>
                            </Grid>
                            <Grid item md={4}>
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
                            <Grid item md={4}>
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
                        </Grid>
                    </CardWrapper>
                </Grid>
                <Grid item md={6}>
                    <CardWrapper>
                        <Grid>
                            <Typography color={theme.palette.success.dark} fontWeight="bold">
                                Shopping List
                            </Typography>
                        </Grid>
                        <Box my={3} />
                        <Grid container spacing={2}>
                            <Grid item md={4}>
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
                            <Grid item md={4}>
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
                                        <Typography variant="subtitle2" align="center">
                                            Kitchen Commander
                                        </Typography>
                                    </Box>
                                </Tooltip>
                            </Grid>
                            <Grid item md={4}>
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

export default Badges;
