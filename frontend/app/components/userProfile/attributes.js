import { useEffect, useState } from 'react';
import { Box, Grid, TextField, MenuItem, Typography, FormControl } from '@mui/material';

import { getDecodedToken } from 'utils/tokenUtils';
import { useTheme } from '@mui/material/styles';

import MainCard from 'ui-component/cards/MainCard';
import SkeletonTotalGrowthBarChart from 'ui-component/cards/Skeleton/TotalGrowthBarChart';

const Attributes = ({ isLoading, isFetchingData, formData, setFormData }) => {
    const [disabled, setDisabled] = useState(true);

    const theme = useTheme();
    const decodedToken = getDecodedToken();

    useEffect(() => {
        // console.log(formData);
    }, []);

    const getPALValue = (pal) => {
        switch (pal) {
            case 'sedentary':
                return 1.4;
            case 'moderately':
                return 1.6;
            case 'active':
                return 1.8;
            case 'very_active':
                return 2.0;
            default:
                return 1.0; // fallback to prevent NaN
        }
    };

    const value = getPALValue(formData.PAL);

    // const handleRoleBlur = () => {
    //     if (formData.role === '') {
    //         setFormData({ ...formData, roleStatus: 'invalid' });
    //     } else {
    //         setFormData({ ...formData, roleStatus: 'valid' });
    //     }
    // };

    // const handleRoleFocus = () => {
    //     if (formData.role !== '') {
    //         setFormData({ ...formData, roleStatus: 'valid' });
    //     }
    // };

    // const handleCountryBlur = () => {
    //     if (formData.country === '') {
    //         setFormData({ ...formData, countryStatus: 'invalid' });
    //     } else {
    //         setFormData({ ...formData, countryStatus: 'valid' });
    //     }
    // };

    // const handleCountryFocus = () => {
    //     if (formData.country !== '') {
    //         setFormData({ ...formData, countryStatus: 'valid' });
    //     }
    // };

    return (
        <>
            {isLoading || isFetchingData ? (
                <SkeletonTotalGrowthBarChart />
            ) : (
                <MainCard>
                    <Box
                        sx={{
                            display: 'flex',
                            gap: 2,
                            justifyContent: 'center',
                            mt: 2
                        }}
                    >
                        <FormControl sx={{ width: '50%' }}>
                            <TextField
                                type="number"
                                label="Age"
                                variant="outlined"
                                margin="normal"
                                value={formData.age}
                                disabled
                            ></TextField>
                        </FormControl>

                        <FormControl sx={{ width: '50%' }}>
                            <TextField
                                type="number"
                                label="Body Mass Index (BMI) - kg/m2"
                                variant="outlined"
                                margin="normal"
                                value={Math.round(formData.bmi)}
                                disabled
                            ></TextField>
                        </FormControl>
                    </Box>

                    <Box
                        sx={{
                            display: 'flex',
                            gap: 2,
                            justifyContent: 'center',
                            mt: 2
                        }}
                    >
                        <FormControl sx={{ width: '50%' }}>
                            <TextField
                                type="number"
                                label="Basal Metabolic Rate (BMR) - kcal"
                                variant="outlined"
                                margin="normal"
                                value={Math.round(formData.bmr)}
                                disabled
                            ></TextField>
                        </FormControl>

                        <FormControl sx={{ width: '50%' }}>
                            <TextField
                                type="number"
                                label="Total Daily Energy Expenditure (TDEE) - kcal"
                                variant="outlined"
                                margin="normal"
                                value={Math.round(formData.bmr * value)}
                                disabled
                            ></TextField>
                        </FormControl>
                    </Box>

                    <Box
                        sx={{
                            display: 'flex',
                            gap: 2,
                            justifyContent: 'left',
                            mt: 2
                        }}
                    >
                        <FormControl sx={{ width: '50%' }}>
                            <TextField
                                type="number"
                                label="Suggested Daily Plan Energy Aim - kcal"
                                variant="outlined"
                                margin="normal"
                                value={Math.round(formData.energy_intake)}
                                disabled
                            ></TextField>
                        </FormControl>
                    </Box>
                </MainCard>
            )}{' '}
        </>
    );
};

export default Attributes;
