import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from '@remix-run/react';
import { motion } from 'framer-motion';
import { Grid, Button, Box, Checkbox, TextField, MenuItem, FormControl, ListItemText, FormHelperText, Typography } from '@mui/material';
import { Dialog, DialogActions, DialogContent, DialogTitle } from '@mui/material';
import { LoadingButton } from '@mui/lab';
import InputAdornment from '@mui/material/InputAdornment';
import AnimateButton from 'ui-component/extended/AnimateButton';
import { getDecodedToken } from 'utils/tokenUtils';
import { useTheme } from '@mui/material/styles';
import SkeletonTotalGrowthBarChart from 'ui-component/cards/Skeleton/TotalGrowthBarChart';

import MainCard from 'ui-component/cards/MainCard';
import { getCurrentDayAndWeekDates } from 'utils/getCurrentDayAndWeekDates';
import { updateUserProfile } from 'services/api';
import { updateCurrentWeekNPs } from 'services/api';
import { energyIntakeGoalCalculator } from 'utils/energyIntakeGoalCalculator';

const Characteristics = ({ isLoading, isFetchingData, formData, setFormData }) => {
    const [disabled, setDisabled] = useState(true);

    const navigate = useNavigate();
    const theme = useTheme();
    const decodedToken = getDecodedToken();
    const [isSubmiting, setIsSubmiting] = useState(false);

    const [heightChange, setHeightChange] = useState(false);
    const [weightChange, setWeightChange] = useState(false);
    const [palChange, setPalChange] = useState(false);
    const [dietaryPreferencesChange, setDietaryPreferencesChange] = useState(false);
    const [allergiesChange, setAllergiesChange] = useState(false);
    const [selectedCuisinesChange, setselectedCuisinesChange] = useState(false);
    const [change, setChange] = useState(false);
    const [errorMessage, setErrorMessage] = useState();
    const [successMessage, setSuccessMessage] = useState();
    const [infoMessage, setInfoMessage] = useState();
    const [openDialog, setOpenDialog] = useState(false);

    const palMessages = [
        {
            level: 'sedentary',
            message: `"Exclusively sedentary activity, generally seated at work. With little or no strenuous leisure activities"`
        },
        {
            level: 'moderately',
            message: `"Predominantly standing or walking work, with little strenuous leisure activity"`
        },
        {
            level: 'active',
            message: `"Predominantly standing or walking work with significant amounts of strenuous leisure activity"`
        },
        {
            level: 'very_active',
            message: `"Heavy occupational work or significant strenuous leisure activities"`
        }
    ];

    const dietaryPreferencesMessages = [
        {
            level: 'omnivore',
            message: ``
        },
        {
            level: 'pescatarian',
            message: `"Eats fish and seafood but avoids other meats; include dairy and eggs."`
        },
        {
            level: 'vegetarian',
            message: `"Avoids all meat and fish but consume dairy and eggs."`
        },
        {
            level: 'vegan',
            message: `"Avoids all animal products, including meat, dairy, eggs, and even honey."`
        }
    ];

    useEffect(() => {
        // console.log(formData);

        if (
            formData.heightStatus === 'valid' &&
            formData.weightStatus === 'valid' &&
            formData.palStatus === 'valid' &&
            formData.dietaryPreferencesStatus === 'valid' &&
            formData.allergiesStatus === 'valid' &&
            formData.selectedCuisinesStatus === 'valid'
        ) {
            setDisabled(false);
        } else {
            setDisabled(true);
        }

        if (heightChange || weightChange || palChange || dietaryPreferencesChange || allergiesChange || selectedCuisinesChange) {
            setChange(true);
        } else {
            setChange(false);
        }
    }, [
        formData.heightStatus,
        formData.weightStatus,
        formData.palStatus,
        formData.dietaryPreferencesStatus,
        formData.allergiesStatus,
        formData.selectedCuisinesStatus,
        heightChange,
        weightChange,
        palChange,
        dietaryPreferencesChange,
        allergiesChange,
        selectedCuisinesChange
    ]);

    const handleHeightChange = (e) => {
        const value = e.target.value;
        let status = 'typing';

        if (value >= 50 && value <= 250) {
            status = 'valid';
        } else if (e.target.value === '') {
            status = 'typing'; // Reset to default if empty
        } else {
            status = 'typing'; // Keep it grey while typing
        }

        setHeightChange(true);
        setFormData({
            ...formData,
            height: value,
            heightStatus: status
        });
    };

    const handleHeightBlur = (e) => {
        if (formData.height < 50 || formData.height > 250) {
            setFormData({ ...formData, heightStatus: 'invalid' });
        }
    };

    const handleHeightFocus = () => {
        if (formData.height === '') {
            setFormData({ ...formData, heightStatus: 'typing' });
        }
    };

    const handleWeightChange = (e) => {
        const value = e.target.value;
        let status = 'typing';
        let weeks = { goal: '', slow_weeks: null, normal_weeks: null, fast_weeks: null };

        // Check if the email format is valid as the user types
        if (value >= 30 && value <= 300) {
            status = 'valid';
            weeks = energyIntakeGoalCalculator(value, formData.target_weight);
        } else if (e.target.value === '') {
            status = 'typing'; // Reset to default if empty
        } else {
            status = 'typing'; // Keep it grey while typing
        }

        setWeightChange(true);
        setFormData({
            ...formData,
            weight: value,
            weightStatus: status,
            goal: weeks.goal
        });
    };

    const handleWeightBlur = () => {
        if (formData.weight < 30 || formData.weight > 300) {
            setFormData({ ...formData, weightStatus: 'invalid' });
        }
    };

    const handleWeightFocus = () => {
        if (formData.weight === '') {
            setFormData({ ...formData, weightStatus: 'typing' });
        }
    };

    const handlePalChange = (e) => {
        setPalChange(true);
        setFormData({ ...formData, PAL: e.target.value });
    };

    const handlePalBlur = () => {
        if (formData.PAL === '') {
            setFormData({ ...formData, palStatus: 'invalid' });
        } else {
            setFormData({ ...formData, palStatus: 'valid' });
        }
    };

    const handlePalFocus = () => {
        if (formData.PAL !== '') {
            setFormData({ ...formData, palStatus: 'valid' });
        }
    };

    const handleDietaryPreferencesChange = (e) => {
        setDietaryPreferencesChange(true);
        setFormData({ ...formData, dietaryPreferences: e.target.value });
    };

    const handleDietaryPreferencesBlur = () => {
        if (formData.dietaryPreferences === '') {
            setFormData({ ...formData, dietaryPreferencesStatus: 'invalid' });
        } else {
            setFormData({ ...formData, dietaryPreferencesStatus: 'valid' });
        }
    };

    const handleDietaryPreferencesFocus = () => {
        if (formData.dietaryPreferences !== '') {
            setFormData({ ...formData, dietaryPreferencesStatus: 'valid' });
        }
    };

    const handleAllergiesChange = (e) => {
        setAllergiesChange(true);
        setFormData({ ...formData, allergies: e.target.value });
    };

    const handleAllergiesBlur = () => {
        if (formData.allergies === '') {
            setFormData({ ...formData, allergiesStatus: 'invalid' });
        } else {
            setFormData({ ...formData, allergiesStatus: 'valid' });
        }
    };

    const handleAllergiesFocus = () => {
        if (formData.allergies !== '') {
            setFormData({ ...formData, allergiesStatus: 'valid' });
        }
    };

    const handleSelectedCuisinesChange = (e) => {
        setAllergiesChange(true);
        setFormData({ ...formData, selectedCuisines: e.target.value });
    };

    const handleCuisinesBlur = () => {
        if (formData.selectedCuisines.length === 0) {
            setFormData({ ...formData, selectedCuisinesStatus: 'invalid' });
        } else {
            setFormData({ ...formData, selectedCuisinesStatus: 'valid' });
        }
    };

    const handleCuisinesFocus = () => {
        if (formData.selectedCuisines.length !== 0) {
            setFormData({ ...formData, selectedCuisinesStatus: 'valid' });
        } else {
            setFormData({ ...formData, selectedCuisinesStatus: 'invalid' });
        }
    };

    const handleUpdateUserProfile = () => {
        setOpenDialog(true);
    };

    const handleDialogClose = async (confirm) => {
        if (confirm) {
            // If user confirms, update
            setOpenDialog(false);
            setIsSubmiting(true);

            const { currday, currMondayDate, currSundayDate } = getCurrentDayAndWeekDates();

            try {
                const updateUserPro = await updateUserProfile(decodedToken.user_id, formData);
                setSuccessMessage(updateUserPro.data.message);
                setInfoMessage('Please wait while we are updating your weekly NP');
                try {
                    const updateNPs = await updateCurrentWeekNPs(decodedToken.user_id, currMondayDate, currSundayDate);
                    setSuccessMessage(updateNPs.data.message);
                    setInfoMessage('');
                    setTimeout(() => {
                        navigate('/meal-plan');
                    }, 2000); // Reloads after 2 seconds
                } catch (error) {
                    // console.log(error.response?.data?.error || 'An error occurred');
                    setErrorMessage(error.response?.data?.error || 'An error occurred');
                }
            } catch (error) {
                // console.log(error.response?.data?.error || 'An error occurred');
                setErrorMessage(error.response?.data?.error || 'An error occurred');
            }
            setIsSubmiting(false);
        }
        // Close the dialog regardless of confirmation
        setOpenDialog(false);
    };

    const WavyText = ({ text }) => {
        return (
            <span>
                {text.split(' ').map((word, index) => (
                    <motion.span
                        key={index}
                        style={{ display: 'inline-block', marginRight: '5px' }}
                        animate={{ y: [0, -5, 0] }}
                        transition={{
                            duration: 0.6,
                            repeat: Infinity,
                            repeatDelay: 0.5,
                            delay: index * 0.1
                        }}
                    >
                        {word}
                    </motion.span>
                ))}
            </span>
        );
    };

    return (
        <>
            {isLoading || isFetchingData ? (
                <SkeletonTotalGrowthBarChart />
            ) : (
                <MainCard>
                    <Grid item>
                        <Typography variant="h3">Physical Characteristics</Typography>
                    </Grid>
                    <Box my={2} />

                    <Box
                        sx={{
                            display: 'flex',
                            gap: 2,
                            justifyContent: 'center'
                        }}
                    >
                        <FormControl sx={{ width: '50%' }}>
                            <TextField select disabled label="Sex" variant="outlined" margin="normal" value={formData.sex}>
                                <MenuItem value="male">Male</MenuItem>
                                <MenuItem value="female">Female</MenuItem>
                            </TextField>
                        </FormControl>

                        <FormControl sx={{ width: '50%' }}>
                            <TextField
                                type="number"
                                label="Year of Birth"
                                variant="outlined"
                                margin="normal"
                                value={formData.yob}
                                disabled
                            />
                            <FormHelperText
                                sx={{
                                    color: formData.yobStatus === 'valid' ? 'green' : formData.yobStatus === 'invalid' ? 'red' : 'grey',
                                    fontSize: '0.75rem' // Optional: Adjust font size for helper text
                                }}
                            >
                                {formData.yobStatus === 'invalid'
                                    ? '! Year of birth must be between 1904 and 2024'
                                    : formData.yobStatus === 'valid'
                                    ? '✓ Year of birth must be between 1904 and 2024'
                                    : formData.yobStatus === 'typing'
                                    ? 'Year of birth must be between 1904 and 2024'
                                    : ''}
                            </FormHelperText>
                        </FormControl>
                    </Box>
                    <Box
                        sx={{
                            display: 'flex',
                            gap: 2,
                            justifyContent: 'center'
                        }}
                    >
                        <FormControl sx={{ width: '50%' }}>
                            <TextField
                                type="number"
                                label="Height"
                                variant="outlined"
                                margin="normal"
                                sx={{
                                    '& .MuiFormHelperText-root': {
                                        color:
                                            formData.heightStatus === 'valid'
                                                ? 'green'
                                                : formData.heightStatus === 'invalid'
                                                ? 'red'
                                                : 'grey' // Helper text color based on status
                                    }
                                }}
                                InputProps={{
                                    endAdornment: <InputAdornment position="end">cm</InputAdornment>
                                }}
                                value={formData.height}
                                onChange={handleHeightChange}
                                onBlur={handleHeightBlur}
                                onFocus={handleHeightFocus}
                                error={formData.heightStatus === 'invalid'}
                                helperText={
                                    formData.heightStatus === 'invalid'
                                        ? '! Height must be between 50 and 250 cm'
                                        : formData.heightStatus === 'valid'
                                        ? '✓ Height must be between 50 and 250 cm'
                                        : formData.heightStatus === 'typing'
                                        ? 'Height must be between 50 and 250 cm'
                                        : ''
                                }
                                disabled={isSubmiting}
                            />
                        </FormControl>

                        <FormControl sx={{ width: '50%' }}>
                            <TextField
                                type="number"
                                label="Weight"
                                variant="outlined"
                                margin="normal"
                                sx={{
                                    '& .MuiFormHelperText-root': {
                                        color:
                                            formData.weightStatus === 'valid'
                                                ? 'green'
                                                : formData.weightStatus === 'invalid'
                                                ? 'red'
                                                : 'grey' // Helper text color based on status
                                    }
                                }}
                                InputProps={{
                                    endAdornment: <InputAdornment position="end">kg</InputAdornment>
                                }}
                                value={formData.weight}
                                onChange={handleWeightChange}
                                onBlur={handleWeightBlur}
                                onFocus={handleWeightFocus}
                                error={formData.weightStatus === 'invalid'}
                                helperText={
                                    formData.weightStatus === 'invalid'
                                        ? '! Weight must be between 30 and 300 kg'
                                        : formData.weightStatus === 'valid'
                                        ? '✓ Weight must be between 30 and 300 kg'
                                        : formData.weightStatus === 'typing'
                                        ? 'Weight must be between 30 and 300 kg'
                                        : ''
                                }
                                disabled={isSubmiting}
                            />
                        </FormControl>
                    </Box>

                    <TextField
                        select
                        fullWidth
                        label="Physical Activity Level (PAL)"
                        variant="outlined"
                        margin="normal"
                        value={formData.PAL}
                        onChange={handlePalChange}
                        onBlur={handlePalBlur}
                        onFocus={handlePalFocus}
                        error={formData.palStatus === 'invalid'}
                        helperText={formData.palStatus === 'invalid' ? 'PAL is required' : ''}
                        sx={{
                            '& .MuiFormHelperText-root': {
                                color: 'red'
                            }
                        }}
                        disabled={isSubmiting}
                    >
                        <MenuItem value="sedentary">Low Active/Sedentary Lifestyle (1.4)</MenuItem>
                        <MenuItem value="moderately">Moderately Active Lifestyle (1.6)</MenuItem>
                        <MenuItem value="active">Active Lifestyle (1.8)</MenuItem>
                        <MenuItem value="very_active">Very Active Lifestyle (2.0)</MenuItem>
                    </TextField>
                    {formData.PAL && (
                        <Grid item xs={12}>
                            <Grid item container direction="column" alignItems="center" xs={12}>
                                <Typography variant="body" sx={{ my: 1, px: 1 }}>
                                    <em>{palMessages.find((item) => item.level === formData.PAL).message}</em>
                                </Typography>
                            </Grid>
                        </Grid>
                    )}

                    <Box
                        sx={{
                            display: 'flex',
                            gap: 2,
                            justifyContent: 'center'
                        }}
                    >
                        <FormControl sx={{ width: '50%' }}>
                            <TextField
                                select
                                fullWidth
                                label="Dietary Preferences"
                                variant="outlined"
                                margin="normal"
                                value={formData.dietaryPreferences}
                                onChange={handleDietaryPreferencesChange}
                                onBlur={handleDietaryPreferencesBlur}
                                onFocus={handleDietaryPreferencesFocus}
                                error={formData.dietaryPreferencesStatus === 'invalid'}
                                helperText={formData.dietaryPreferencesStatus === 'invalid' ? 'Dietary Preference is required' : ''}
                                sx={{
                                    '& .MuiFormHelperText-root': {
                                        color: 'red'
                                    }
                                }}
                                disabled={isSubmiting}
                            >
                                <MenuItem value="omnivore">None</MenuItem>
                                <MenuItem value="pescatarian">Pescatarian</MenuItem>
                                <MenuItem value="vegetarian">Vegetarian</MenuItem>
                                <MenuItem value="vegan">Vegan</MenuItem>
                            </TextField>
                            {formData.dietaryPreferences && (
                                <Grid item xs={12}>
                                    <Grid item container direction="column" alignItems="center" xs={12}>
                                        <Typography variant="body" sx={{ my: 1, px: 1 }}>
                                            <em>
                                                {
                                                    dietaryPreferencesMessages.find((item) => item.level === formData.dietaryPreferences)
                                                        .message
                                                }
                                            </em>
                                        </Typography>
                                    </Grid>
                                </Grid>
                            )}
                        </FormControl>

                        <FormControl sx={{ width: '50%' }}>
                            <TextField
                                select
                                fullWidth
                                label="Allergies"
                                variant="outlined"
                                margin="normal"
                                value={formData.allergies}
                                onChange={handleAllergiesChange}
                                onBlur={handleAllergiesBlur}
                                onFocus={handleAllergiesFocus}
                                error={formData.allergiesStatus === 'invalid'}
                                helperText={formData.allergiesStatus === 'invalid' ? 'Allergies is required' : ''}
                                sx={{
                                    '& .MuiFormHelperText-root': {
                                        color: 'red'
                                    }
                                }}
                                disabled={isSubmiting}
                            >
                                <MenuItem value="no_allergy">None</MenuItem>
                                <MenuItem value="milk_allergy">Dairy</MenuItem>
                                <MenuItem value="nuts_allergy">Nuts</MenuItem>
                            </TextField>
                        </FormControl>
                    </Box>

                    <FormControl FormControl sx={{ width: '100%' }}>
                        <TextField
                            select
                            fullWidth
                            label="Cuisine(s) for meal suggestions"
                            variant="outlined"
                            margin="normal"
                            SelectProps={{
                                multiple: true, // ✅ Allows multiple selection
                                renderValue: (selected) => selected.join(', ') // ✅ Shows selected values as text
                            }}
                            value={formData.selectedCuisines}
                            onChange={handleSelectedCuisinesChange}
                            onBlur={handleCuisinesBlur}
                            onFocus={handleCuisinesFocus}
                            error={formData.selectedCuisinesStatus === 'invalid'}
                            helperText={formData.selectedCuisinesStatus === 'invalid' ? 'Cuisine(s) is required' : ''}
                            sx={{
                                '& .MuiFormHelperText-root': {
                                    color: 'red'
                                }
                            }}
                            disabled={isSubmiting}
                        >
                            {['Irish', 'Spain', 'Hungary'].map((cuisine) => (
                                <MenuItem key={cuisine} value={cuisine}>
                                    <Checkbox checked={formData.selectedCuisines.indexOf(cuisine) > -1} />
                                    <ListItemText primary={cuisine} />
                                </MenuItem>
                            ))}
                        </TextField>
                    </FormControl>

                    {successMessage && (
                        <Box sx={{ mt: 3 }}>
                            <FormHelperText sx={{ color: 'green' }}>✓ {successMessage}</FormHelperText>
                            <FormHelperText>{infoMessage && <WavyText text={infoMessage} />}</FormHelperText>
                        </Box>
                    )}
                    {errorMessage && (
                        <Box sx={{ mt: 3 }}>
                            <FormHelperText error>{errorMessage}</FormHelperText>
                        </Box>
                    )}
                    <Box
                        sx={{
                            mt: 2,
                            display: 'flex',
                            justifyContent: 'space-between'
                        }}
                    >
                        <AnimateButton>
                            {/* <Button disableElevation onClick={(e) => setPage(page - 1)} fullWidth size="large" variant="contained" color="success">
                                    Previous
                                </Button> */}
                        </AnimateButton>
                        <AnimateButton>
                            <LoadingButton
                                disableElevation
                                disabled={disabled || !change}
                                fullWidth
                                size="large"
                                variant="contained"
                                color="success"
                                onClick={handleUpdateUserProfile}
                                loading={isSubmiting}
                            >
                                Update
                            </LoadingButton>
                        </AnimateButton>
                    </Box>
                </MainCard>
            )}{' '}
            <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
                <DialogTitle>
                    <Typography variant="h3">Confirm Update</Typography>
                </DialogTitle>
                <Box></Box>
                <DialogContent>
                    <Typography>
                        If you update your profile, daily meal plans will be re-generated for the current week. Any changes in your shopping
                        list will be lost.
                    </Typography>
                    <Typography mt={3}>Are you sure you want to proceed?</Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => handleDialogClose(false)} color="primary">
                        No
                    </Button>
                    <Button onClick={() => handleDialogClose(true)} color="primary">
                        Yes
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
};

export default Characteristics;
