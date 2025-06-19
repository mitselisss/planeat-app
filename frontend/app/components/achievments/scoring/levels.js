import MainCard from 'ui-component/cards/MainCard';
import { Grid, Box, Typography } from '@mui/material';
import level1 from '../../../assets/images/levels/Level1.png';
import level2 from '../../../assets/images/levels/Level2.jpg';
import level3 from '../../../assets/images/levels/Level3.jpg';
import level4 from '../../../assets/images/levels/Level4.jpg';
import level5 from '../../../assets/images/levels/Level5.jpg';

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

const Levels = ({ achievements }) => {
    const theme = useTheme();
    return (
        <Grid container spacing={2} direction="column">
            <Grid item container spacing={2} mt={2}>
                <Grid item md={12}>
                    <CardWrapper>
                        <Grid container padding={5} spacing={2} justifyContent="space-between">
                            <Grid item textAlign="center">
                                <img src={level1} width={80} height={80} alt="level" />
                                <Typography color={theme.palette.success.dark} fontWeight="bold">
                                    Beginner
                                </Typography>
                                {/* <Box mt={1}></Box>
                                <Typography variant="subtitle2">Badges: 0</Typography>
                                <Typography variant="subtitle2">Points: 0</Typography> */}
                            </Grid>
                            <Grid item textAlign="center">
                                <img
                                    src={level2}
                                    width={80}
                                    height={80}
                                    alt="leve2"
                                    style={{
                                        filter: achievements?.level < 2 ? 'grayscale(100%)' : 'none',
                                        opacity: achievements?.level < 2 ? 0.6 : 1
                                    }}
                                />
                                <Typography color={theme.palette.success.dark} fontWeight="bold">
                                    Tracker
                                </Typography>
                                <Box mt={1}></Box>
                                <Typography variant="subtitle2">Badges: 3</Typography>
                                <Typography variant="subtitle2">Points: 100</Typography>
                            </Grid>
                            <Grid item textAlign="center">
                                <img
                                    src={level3}
                                    width={80}
                                    height={80}
                                    alt="leve3"
                                    style={{
                                        filter: achievements?.level < 3 ? 'grayscale(100%)' : 'none',
                                        opacity: achievements?.level < 3 ? 0.6 : 1
                                    }}
                                />
                                <Typography color={theme.palette.success.dark} fontWeight="bold">
                                    Planner
                                </Typography>
                                <Box mt={1}></Box>
                                <Typography variant="subtitle2">Badges: 7</Typography>
                                <Typography variant="subtitle2">Points: 300</Typography>
                            </Grid>
                            <Grid item textAlign="center">
                                <img
                                    src={level4}
                                    width={80}
                                    height={80}
                                    alt="leve4"
                                    style={{
                                        filter: achievements?.level < 4 ? 'grayscale(100%)' : 'none',
                                        opacity: achievements?.level < 4 ? 0.6 : 1
                                    }}
                                />
                                <Typography color={theme.palette.success.dark} fontWeight="bold">
                                    Expert
                                </Typography>
                                <Box mt={1}></Box>
                                <Typography variant="subtitle2">Badges: 10</Typography>
                                <Typography variant="subtitle2">Points: 600</Typography>
                            </Grid>
                            <Grid item textAlign="center">
                                <img
                                    src={level5}
                                    width={80}
                                    height={80}
                                    alt="leve5"
                                    style={{
                                        filter: achievements?.level < 5 ? 'grayscale(100%)' : 'none',
                                        opacity: achievements?.level < 5 ? 0.6 : 1
                                    }}
                                />
                                <Typography color={theme.palette.success.dark} fontWeight="bold">
                                    Legend
                                </Typography>
                                <Box mt={1}></Box>
                                <Typography variant="subtitle2">Badges: 18</Typography>
                                <Typography variant="subtitle2">Points: 1000</Typography>
                            </Grid>
                        </Grid>
                    </CardWrapper>
                </Grid>
            </Grid>
        </Grid>
    );
};

export default Levels;
