// material-ui
import { Card, CardContent, Grid } from '@mui/material';
import Skeleton from '@mui/material/Skeleton';

// ==============================|| SKELETON - EARNING CARD ||============================== //

const SkeletonShoppingList = () => (
    <Card>
        <CardContent>
            <Grid container direction="column">
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

export default SkeletonShoppingList;
