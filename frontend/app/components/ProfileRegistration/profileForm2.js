import { useEffect, useState } from 'react';
import { useNavigate } from '@remix-run/react';
import {
    Grid,
    Button,
    Box,
    TextField,
    MenuItem,
    FormControl,
    Typography,
    FormLabel,
    Checkbox,
    ListItemText,
    RadioGroup,
    Radio,
    FormControlLabel,
    FormHelperText
} from '@mui/material';
import MainCard from 'ui-component/cards/MainCard';
import InputAdornment from '@mui/material/InputAdornment';
import AnimateButton from 'ui-component/extended/AnimateButton';
import { getDecodedToken } from 'utils/tokenUtils';
import { useTheme } from '@mui/material/styles';
import axios from 'axios';
import { energyIntakeGoalCalculator } from 'utils/energyIntakeGoalCalculator';
import { createUserPro } from 'services/api';

const ProfileForm2 = ({ page, setPage, formData, setFormData }) => {
    const navigate = useNavigate();
    const theme = useTheme();
    const decodedToken = getDecodedToken();
    const [disabled, setDisabled] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [errorMessage, setErrorMessage] = useState();
    const [checked, setChecked] = useState(false);
    const label = { inputProps: { 'aria-label': 'Checkbox demo' } };

    // const [goal, setGoal] = useState(''); // Increase, decrese or keep the same weight
    // const [targetGoal, setTargetGoal] = useState('normal'); // normal or fast programm

    // how many weeks need to achieve target weight goal according to each programm
    const [slowWeeks, setSlowWeeks] = useState();
    const [normalWeeks, setNormalWeeks] = useState();
    const [fastWeeks, setFastWeeks] = useState();

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

    // useEffect(() => {
    //     console.log(formData);
    // }, [formData.sex, formData.yob, formData.height, formData.weight, formData.PAL]);

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

    const handleWeightChange = (e) => {
        const value = e.target.value;
        let status = 'typing';
        let weeks = { goal: '', slow_weeks: null, normal_weeks: null, fast_weeks: null };

        // Check if the email format is valid as the user types
        if (value >= 30 && value <= 300) {
            status = 'valid';
            weeks = energyIntakeGoalCalculator(formData.weight, value);
            setSlowWeeks(weeks.slow_weeks);
            setNormalWeeks(weeks.normal_weeks);
            setFastWeeks(weeks.fast_weeks);
        } else if (e.target.value === '') {
            status = 'typing'; // Reset to default if empty
        } else {
            status = 'typing'; // Keep it grey while typing
        }

        setFormData({
            ...formData,
            goal: weeks.goal,
            target_weight: value,
            target_weight_status: status
        });
    };

    const handleWeightBlur = () => {
        if (formData.target_weight < 30 || formData.weight > 300) {
            setFormData({ ...formData, target_weight_status: 'invalid' });
        }
    };

    const handleWeightFocus = () => {
        if (formData.target_weight === '') {
            setFormData({ ...formData, target_weight_status: 'typing' });
        }
    };

    useEffect(() => {
        if (
            formData.target_weight_status === 'valid' &&
            formData.dietaryPreferencesStatus === 'valid' &&
            formData.allergiesStatus === 'valid' &&
            formData.selectedCuisinesStatus === 'valid'
        ) {
            setDisabled(false);
        } else {
            setDisabled(true);
        }
    }, [
        formData.target_weight_status,
        formData.dietaryPreferencesStatus,
        formData.allergiesStatus,
        formData.selectedCuisinesStatus,
        formData.targetGoal
    ]);

    const handleCreateUserProfile = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);

        try {
            const response = await createUserPro(decodedToken.user_id, formData);
            // console.log("Response:", response.data);
            if (response.status === 200) {
                navigate('/meal-plan');
            }
        } catch (error) {
            // console.log(error.response?.data?.error || 'An error occurred');
            setErrorMessage(error.response?.data?.error || 'An error occurred');
        }

        setIsSubmitting(false);
    };

    const handleChange = (e) => {
        setChecked(e.target.checked);
        if (e.target.checked) {
            setFormData({ ...formData, target_weight: formData.weight, target_weight_status: 'valid', goal: '', targetGoal: '' });
        } else {
            setFormData({ ...formData, target_weight: '', target_weight_status: '', goal: '', targetGoal: '' });
        }
    };

    return (
        <div className="login-page">
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
                        label="Current Weight"
                        variant="outlined"
                        margin="normal"
                        InputProps={{
                            endAdornment: <InputAdornment position="end">kg</InputAdornment>
                        }}
                        value={formData.weight}
                        disabled
                    />
                </FormControl>

                <FormControl sx={{ width: '50%' }}>
                    <TextField
                        type="number"
                        label="Target Weight"
                        variant="outlined"
                        margin="normal"
                        disabled={checked}
                        sx={{
                            '& .MuiFormHelperText-root': {
                                color:
                                    formData.target_weight_status === 'valid'
                                        ? 'green'
                                        : formData.target_weight_status === 'invalid'
                                        ? 'red'
                                        : 'grey' // Helper text color based on status
                            }
                        }}
                        InputProps={{
                            endAdornment: <InputAdornment position="end">kg</InputAdornment>
                        }}
                        value={formData.target_weight}
                        onChange={handleWeightChange}
                        onBlur={handleWeightBlur}
                        onFocus={handleWeightFocus}
                        error={formData.target_weight_status === 'invalid'}
                        helperText={
                            formData.target_weight_status === 'invalid'
                                ? '! Weight must be between 30 and 300 kg'
                                : formData.target_weight_status === 'valid'
                                ? '✓ Weight must be between 30 and 300 kg'
                                : formData.target_weight_status === 'typing'
                                ? 'Weight must be between 30 and 300 kg'
                                : ''
                        }
                    />
                </FormControl>
            </Box>

            {formData.target_weight_status === 'valid' && formData.goal !== 'same' && !checked && (
                <MainCard sx={{ backgroundColor: theme.palette.success[100] }}>
                    <Grid
                        container
                        alignItems="center" // Vertically center
                        justifyContent="center" // Horizontally center
                        direction="column" // Align everything vertically
                        spacing={1} // Optional spacing between items
                    >
                        <FormControl>
                            <FormLabel
                                id="demo-row-radio-buttons-group-label"
                                sx={{ textAlign: 'center' }} // Center the label
                            >
                                Caloric Goal
                            </FormLabel>
                            <RadioGroup
                                row
                                aria-labelledby="demo-row-radio-buttons-group-label"
                                name="row-radio-buttons-group"
                                spacing={1}
                                value={formData.targetGoal}
                                onChange={(e) => setFormData({ ...formData, targetGoal: e.target.value })}
                                sx={{ display: 'flex', justifyContent: 'center', textAlign: 'center', gap: 2 }}
                            >
                                {/* <FormControlLabel
                                    value="slow"
                                    control={<Radio size="small" />}
                                    label={
                                        <Typography variant="subtitle2" color="textSecondary">
                                            {`250 kcal/day`}
                                        </Typography>
                                    }
                                /> */}
                                <FormControlLabel
                                    value="normal"
                                    control={<Radio size="small" />}
                                    label={
                                        <Typography variant="subtitle2" color="textSecondary">
                                            {formData.goal === 'increase' ? `+500 kcal/day` : '-500 kcal/day'}
                                        </Typography>
                                    }
                                />
                                <FormControlLabel
                                    value="fast"
                                    control={<Radio size="small" />}
                                    label={
                                        <Typography variant="subtitle2" color="textSecondary">
                                            {formData.goal === 'increase' ? `+700 kcal/day` : '-700 kcal/day'}
                                        </Typography>
                                    }
                                />
                            </RadioGroup>
                            <Typography
                                variant="subtitle2"
                                color="textSecondary"
                                sx={{ textAlign: 'center' }} // Center the week estimate text
                            >
                                {`Approximately ${
                                    formData.targetGoal === 'normal' ? normalWeeks : formData.targetGoal === 'fast' ? fastWeeks : slowWeeks
                                } weeks to achieve your target goal`}
                            </Typography>
                        </FormControl>
                    </Grid>
                </MainCard>
            )}

            <Box>
                <FormControlLabel
                    control={<Checkbox size="small" checked={checked} onChange={handleChange} />}
                    label={<Typography variant="subtitle2">I prefer to maintain my weight</Typography>}
                />
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
                        select
                        fullWidth
                        label="Dietary Preferences"
                        variant="outlined"
                        margin="normal"
                        value={formData.dietaryPreferences}
                        onChange={(e) => setFormData({ ...formData, dietaryPreferences: e.target.value })}
                        onBlur={handleDietaryPreferencesBlur}
                        onFocus={handleDietaryPreferencesFocus}
                        error={formData.dietaryPreferencesStatus === 'invalid'}
                        helperText={formData.dietaryPreferencesStatus === 'invalid' ? 'Dietary Preference is required' : ''}
                        sx={{
                            '& .MuiFormHelperText-root': {
                                color: 'red'
                            }
                        }}
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
                                    <em>{dietaryPreferencesMessages.find((item) => item.level === formData.dietaryPreferences).message}</em>
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
                        onChange={(e) => setFormData({ ...formData, allergies: e.target.value })}
                        onBlur={handleAllergiesBlur}
                        onFocus={handleAllergiesFocus}
                        error={formData.allergiesStatus === 'invalid'}
                        helperText={formData.allergiesStatus === 'invalid' ? 'Allergies is required' : ''}
                        sx={{
                            '& .MuiFormHelperText-root': {
                                color: 'red'
                            }
                        }}
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
                    onChange={(e) => {
                        setFormData({ ...formData, selectedCuisines: e.target.value });
                    }}
                    onBlur={handleCuisinesBlur}
                    onFocus={handleCuisinesFocus}
                    error={formData.selectedCuisinesStatus === 'invalid'}
                    helperText={formData.selectedCuisinesStatus === 'invalid' ? 'Cuisine(s) is required' : ''}
                    sx={{
                        '& .MuiFormHelperText-root': {
                            color: 'red'
                        }
                    }}
                >
                    {['Irish', 'Spain', 'Hungary'].map((cuisine) => (
                        <MenuItem key={cuisine} value={cuisine}>
                            <Checkbox checked={formData.selectedCuisines.indexOf(cuisine) > -1} />
                            <ListItemText primary={cuisine} />
                        </MenuItem>
                    ))}
                </TextField>
            </FormControl>

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
                    <Button
                        disableElevation
                        disabled={isSubmitting}
                        onClick={() => setPage(page - 1)}
                        fullWidth
                        size="large"
                        variant="contained"
                        color="success"
                    >
                        Previous
                    </Button>
                </AnimateButton>
                <AnimateButton>
                    <Button
                        disableElevation
                        disabled={disabled || isSubmitting}
                        fullWidth
                        size="large"
                        variant="contained"
                        color="success"
                        onClick={handleCreateUserProfile}
                    >
                        Create
                    </Button>
                </AnimateButton>
            </Box>
        </div>
    );
};

export default ProfileForm2;
