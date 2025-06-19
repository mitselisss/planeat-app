import { Card, CardContent, Grid } from '@mui/material';
import Skeleton from '@mui/material/Skeleton';

// ==============================|| SKELETON - EARNING CARD ||============================== //

const SkeletonMealPlan = () => (
    <Card>
        <CardContent>
            <Grid container direction="column">
                <Grid item>
                    <Grid container direction="row" justifyContent="space-between" alignItems="center" wrap="nowrap">
                        {/* First group of skeletons */}
                        <Grid item>
                            <Grid container spacing={2} alignItems="center" wrap="nowrap">
                                <Grid item>
                                    <Skeleton variant="rectangular" width={44} height={44} />
                                </Grid>
                                <Grid item>
                                    <Skeleton variant="rectangular" width={44} height={44} />
                                </Grid>
                            </Grid>
                        </Grid>

                        {/* Right-aligned skeleton */}
                        <Grid item>
                            <Skeleton variant="rectangular" width={34} height={34} />
                        </Grid>
                    </Grid>
                </Grid>
                <Grid item>
                    <Skeleton variant="rectangular" sx={{ m: 2 }} height={80} />
                </Grid>
                <Grid item>
                    <Skeleton variant="rectangular" sx={{ m: 2 }} height={80} />
                </Grid>
                <Grid item>
                    <Skeleton variant="rectangular" sx={{ m: 2 }} height={80} />
                </Grid>
                <Grid item>
                    <Skeleton variant="rectangular" sx={{ m: 2 }} height={80} />
                </Grid>
                <Grid item>
                    <Skeleton variant="rectangular" sx={{ m: 2 }} height={80} />
                </Grid>
            </Grid>
        </CardContent>
    </Card>
);

export default SkeletonMealPlan;
