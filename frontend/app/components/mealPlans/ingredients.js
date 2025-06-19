import React, { useEffect, useState } from 'react';
import MainCard from 'ui-component/cards/MainCard';

// Material-UI components
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Tooltip, Typography, Grid } from '@mui/material';
import { useTheme } from '@mui/material/styles';

const Ingredients = ({ checked, mealInfo, dishInfo }) => {
    const theme = useTheme();
    const [displayInfo, setDisplayInfo] = useState({});

    useEffect(() => {
        setDisplayInfo(checked === 'meal' ? mealInfo : dishInfo);
        // console.log(mealInfo);
        // console.log(dishInfo);
    }, [checked, mealInfo, dishInfo]);

    const getShortName = (name) => {
        return name.split(',')[0]; // Extracts only the first word before the comma
    };

    return (
        <Grid>
            {!displayInfo.ingredient_info && (
                <MainCard
                // sx={{
                //     backgroundColor: theme.palette.success[100]
                // }}
                >
                    <Grid sx={{ display: 'flex', alignItems: 'center', justifyContent: 'left' }}>
                        <Typography variant="h5">Ingredients</Typography>
                    </Grid>
                </MainCard>
            )}

            {displayInfo.ingredient_info && (
                <TableContainer
                    component={Paper}
                    sx={{
                        // backgroundColor: theme.palette.success[100],
                        padding: 1
                    }}
                >
                    <Table size="small" aria-label="a dense table">
                        <TableHead>
                            <TableRow>
                                <TableCell>Ingredient(Quantity)</TableCell>
                                <TableCell align="right">Calories&nbsp;(kcal)</TableCell>
                                <TableCell align="right">Carbs&nbsp;(g)</TableCell>
                                <TableCell align="right">Protein&nbsp;(g)</TableCell>
                                <TableCell align="right">Fat&nbsp;(g)</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {Object.values(displayInfo.ingredient_info).map((ingredient, index) => (
                                <TableRow key={index}>
                                    <TableCell component="th" scope="row">
                                        <Tooltip title={ingredient.ingredient_name} arrow>
                                            <span>{`${getShortName(ingredient.ingredient_name)} (${Math.round(
                                                ingredient.quantity
                                            )}g)`}</span>
                                        </Tooltip>
                                    </TableCell>
                                    <TableCell align="right">{Math.round(ingredient.kcal)}</TableCell>
                                    <TableCell align="right">{Math.round(ingredient.carbs)}</TableCell>
                                    <TableCell align="right">{Math.round(ingredient.protein)}</TableCell>
                                    <TableCell align="right">{Math.round(ingredient.fat)}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            )}
        </Grid>
    );
};

export default Ingredients;

// import React, { useEffect, useState } from 'react';
// import MainCard from 'ui-component/cards/MainCard';

// // material-ui
// import { List, ListItem, ListItemText, Grid, Typography } from '@mui/material';
// import { styled, useTheme } from '@mui/material/styles';

// const Ingredients = ({ checked, mealInfo, dishInfo }) => {
//     const theme = useTheme();

//     const [displayInfo, setDisplayInfo] = useState({});

//     useEffect(() => {
//         {
//             // console.log(mealInfo);
//             checked === 'meal' ? setDisplayInfo(mealInfo) : setDisplayInfo(dishInfo);
//         }
//     });

//     return (
//         <>
//             {/* Main Card displaying the week range */}
//             <MainCard sx={{ backgroundColor: theme.palette.success[100] }}>
//                 <Grid sx={{ display: 'flex', alignItems: 'center', justifyContent: 'left' }}>
//                     <Typography variant="h5">Ingredients</Typography>
//                 </Grid>

//                 {displayInfo.ingredient_quantity && (
//                     <Grid sx={{ marginTop: 3 }}>
//                         <List sx={{ padding: 0 }}>
//                             {Object.values(displayInfo.ingredient_quantity).map((ingredient, index) => (
//                                 <ListItem key={index}>
//                                     <Typography>{`${ingredient.ingredient_name} - ${ingredient.quantity}g`}</Typography>
//                                 </ListItem>
//                             ))}
//                         </List>
//                     </Grid>
//                 )}
//             </MainCard>
//         </>
//     );
// };

// export default Ingredients;
