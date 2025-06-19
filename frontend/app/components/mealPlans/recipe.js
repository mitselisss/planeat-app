import MainCard from 'ui-component/cards/MainCard';

// material-ui
import { Grid, Typography } from '@mui/material';
import { useTheme } from '@mui/material/styles';

const Recipe = ({ dishRecipe }) => {
    const theme = useTheme();

    return (
        <>
            {/* Main Card displaying the week range */}
            <MainCard sx={{ backgroundColor: theme.palette.success[100] }}>
                <Grid container spacing={3}>
                    {' '}
                    {/* Apply spacing to the container */}
                    <Grid item sx={{ display: 'flex', alignItems: 'center', justifyContent: 'left' }}>
                        <Typography variant="h5">Recipe</Typography>
                    </Grid>
                    <Typography variant="body2">{dishRecipe}</Typography>
                </Grid>
            </MainCard>
        </>
    );
};

export default Recipe;
