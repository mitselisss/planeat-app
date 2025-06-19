import MainCard from 'ui-component/cards/MainCard';

// material-ui
import { Grid, Typography } from '@mui/material';
import { useTheme } from '@mui/material/styles';

import LinearProgress, { linearProgressClasses } from '@mui/material/LinearProgress';
import { styled } from '@mui/system';

const Sustainability = () => {
    const theme = useTheme();

    const BorderLinearProgress = styled(LinearProgress)(({ theme }) => ({
        height: 7,
        borderRadius: 5,
        [`&.${linearProgressClasses.colorPrimary}`]: {
            backgroundColor: theme.palette.mode === 'dark' ? theme.palette.grey[800] : theme.palette.grey[200]
        },
        [`& .${linearProgressClasses.bar}`]: {
            borderRadius: 5,
            backgroundColor: theme.palette.mode === 'dark' ? '#308fe8' : '#1a90ff'
        }
    }));

    return (
        <>
            {/* Main Card displaying the week range */}
            <MainCard sx={{ backgroundColor: theme.palette.success[100] }}>
                <Grid container direction={'column'} spacing={3}>
                    {' '}
                    {/* Apply spacing to the container */}
                    <Grid item sx={{ display: 'flex', alignItems: 'center', justifyContent: 'left' }}>
                        <Typography variant="h5">Sustainability</Typography>
                    </Grid>
                    <Grid item>
                        <Grid>
                            <BorderLinearProgress
                                variant="determinate"
                                value={90}
                                sx={{
                                    mb: 3,
                                    '& .MuiLinearProgress-bar': { backgroundColor: theme.palette.success[300] }
                                }}
                            />
                        </Grid>
                    </Grid>
                    <Grid item sx={{ display: 'flex', alignItems: 'center', justifyContent: 'left' }}>
                        <Typography variant="h5">Accessibility</Typography>
                    </Grid>
                    <Grid item>
                        <Grid>
                            <BorderLinearProgress
                                variant="determinate"
                                value={70}
                                sx={{
                                    mb: 3,
                                    '& .MuiLinearProgress-bar': { backgroundColor: theme.palette.success[300] }
                                }}
                            />
                        </Grid>
                    </Grid>
                    <Grid item sx={{ display: 'flex', alignItems: 'center', justifyContent: 'left' }}>
                        <Typography variant="h5">Affordability</Typography>
                    </Grid>
                    <Grid item>
                        <Grid>
                            <BorderLinearProgress
                                variant="determinate"
                                value={80}
                                sx={{
                                    mb: 3,
                                    '& .MuiLinearProgress-bar': { backgroundColor: theme.palette.success[300] }
                                }}
                            />
                        </Grid>
                    </Grid>
                </Grid>
            </MainCard>
        </>
    );
};

export default Sustainability;
