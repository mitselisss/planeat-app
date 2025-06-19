// material-ui
import { Card, CardContent, Grid } from '@mui/material';
import Skeleton from '@mui/material/Skeleton';

// ==============================|| SKELETON - EARNING CARD ||============================== //

const SkeletonDishes = () => (
    <Card>
        <CardContent>
            <Grid container direction="column">
                <Grid item xs={12} sx={{ mx: 10, my: 2 }}>
                    <Skeleton variant="text" />
                </Grid>
                <Grid item>
                    <Skeleton variant="rectangular" sx={{ m: 2 }} height={40} />
                </Grid>
                <Grid item>
                    <Skeleton variant="rectangular" sx={{ m: 2 }} height={40} />
                </Grid>
            </Grid>
        </CardContent>
    </Card>
);

export default SkeletonDishes;
