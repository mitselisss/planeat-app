import { useEffect, useState } from 'react';
import { Box, Grid, TextField, MenuItem, Typography, FormControl } from '@mui/material';

import { getDecodedToken } from 'utils/tokenUtils';
import { useTheme } from '@mui/material/styles';

import MainCard from 'ui-component/cards/MainCard';
import SkeletonTotalGrowthBarChart from 'ui-component/cards/Skeleton/TotalGrowthBarChart';

const PersonalInfo = ({ isLoading, isFetchingData, formData, setFormData }) => {
    const [disabled, setDisabled] = useState(true);

    const theme = useTheme();
    const decodedToken = getDecodedToken();

    useEffect(() => {
        // console.log(formData);
    }, []);

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
                    <Grid item>
                        <Typography variant="h3">Personal Information</Typography>
                    </Grid>
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
                                type="text"
                                label="Username"
                                variant="outlined"
                                margin="normal"
                                value={formData.username}
                                disabled
                            ></TextField>
                        </FormControl>

                        <FormControl sx={{ width: '50%' }}>
                            <TextField type="email" label="Email" variant="outlined" margin="normal" value={formData.email} disabled />
                        </FormControl>
                    </Box>
                    <TextField fullWidth select label="Role" variant="outlined" margin="normal" value={formData.role} disabled>
                        <MenuItem value="living_lab">Living Lab User (Research Participant)</MenuItem>
                        <MenuItem value="consortium">PLANEAT Consortium Member</MenuItem>
                        <MenuItem value="test">Othes Unofficial Tester</MenuItem>
                    </TextField>

                    {formData.role === 'pilot' && (
                        <TextField fullWidth label="Country" variant="outlined" margin="normal" value={formData.country} disabled>
                            <MenuItem value="ireland">Ireland</MenuItem>
                            <MenuItem value="spain">Spain</MenuItem>
                            <MenuItem value="hungary">Hungary</MenuItem>
                        </TextField>
                    )}
                </MainCard>
            )}{' '}
        </>
    );
};

export default PersonalInfo;
