import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from '@remix-run/react';
import { motion } from 'framer-motion';
import {
    Grid,
    Button,
    Box,
    Checkbox,
    TextField,
    FormControl,
    FormHelperText,
    Typography,
    FormLabel,
    RadioGroup,
    Radio,
    FormControlLabel
} from '@mui/material';
import { Dialog, DialogActions, DialogContent, DialogTitle } from '@mui/material';
import { LoadingButton } from '@mui/lab';
import MainCard from 'ui-component/cards/MainCard';
import InputAdornment from '@mui/material/InputAdornment';
import AnimateButton from 'ui-component/extended/AnimateButton';
import { getDecodedToken } from 'utils/tokenUtils';
import { getCurrentDayAndWeekDates } from 'utils/getCurrentDayAndWeekDates';
import { updateUserProfile } from 'services/api';
import { updateCurrentWeekNPs } from 'services/api';
import { useTheme } from '@mui/material/styles';

import { energyIntakeGoalCalculator } from 'utils/energyIntakeGoalCalculator';
import SkeletonTotalGrowthBarChart from 'ui-component/cards/Skeleton/TotalGrowthBarChart';

const Goal = ({ isLoading, isFetchingData, formData, setFormData }) => {
    const navigate = useNavigate();
    const theme = useTheme();
    const decodedToken = getDecodedToken();
    const [isSubmiting, setIsSubmiting] = useState(false);
    const [openDialog, setOpenDialog] = useState(false);

    // const [goal, setGoal] = useState(''); // Increase, decrese or keep the same weight
    // const [targetGoal, setTargetGoal] = useState('normal'); // normal or fast programm

    // how many weeks need to achieve target weight goal according to each programm
    const [slowWeeks, setSlowWeeks] = useState();
    const [normalWeeks, setNormalWeeks] = useState();
    const [fastWeeks, setFastWeeks] = useState();
    const [disabled, setDisabled] = useState(true);
    const [targetWeightChange, setTragetWeightChange] = useState(false);
    const [targetGoalChange, setTargetGoalChange] = useState(false);
    const [change, setChange] = useState(false);
    const [errorMessage, setErrorMessage] = useState();
    const [successMessage, setSuccessMessage] = useState();
    const [infoMessage, setInfoMessage] = useState();
    const [checked, setChecked] = useState(formData.weight === formData.target_weight);

    useEffect(() => {
        let weeks = { goal: '', slow_weeks: null, normal_weeks: null, fast_weeks: null };
        weeks = energyIntakeGoalCalculator(formData.weight, formData.target_weight);
        setSlowWeeks(weeks.slow_weeks);
        setNormalWeeks(weeks.normal_weeks);
        setFastWeeks(weeks.fast_weeks);
    }, [formData.weight]);

    const handleChange = (e) => {
        setChecked(e.target.checked);
        if (e.target.checked) {
            setFormData({ ...formData, target_weight: formData.weight, target_weight_status: 'valid', goal: '', targetGoal: '' });
        } else {
            setFormData({ ...formData, target_weight: '', target_weight_status: '', goal: '', targetGoal: '' });
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

        setTragetWeightChange(true);
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

    const handleTargetGoalChange = (e) => {
        setTargetGoalChange(true);
        setFormData({ ...formData, targetGoal: e.target.value });
    };

    useEffect(() => {
        if (formData.target_weight_status === 'valid') {
            setDisabled(false);
        } else {
            setDisabled(true);
        }

        if (targetWeightChange || targetGoalChange) {
            setChange(true);
        } else {
            setChange(false);
        }
    }, [formData.target_weight_status, targetWeightChange, targetGoalChange]);

    const handleUpdateUserProfile = async (e) => {
        e.preventDefault();

        if (targetGoalChange && !targetWeightChange) {
            setIsSubmiting(true);
            try {
                const updateUserPro = await updateUserProfile(decodedToken.user_id, formData);
                setSuccessMessage(updateUserPro.data.message);
                setTimeout(() => {
                    window.location.reload();
                }, 2000); // Reloads after 2 seconds
            } catch (error) {
                // console.log(error.response?.data?.error || 'An error occurred');
                setErrorMessage(error.response?.data?.error || 'An error occurred');
            }
            setIsSubmiting(false);
        } else if (targetWeightChange) {
            setOpenDialog(true);
        }
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
                        <Typography variant="h3">Goal</Typography>
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
                                disabled={checked || isSubmiting}
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

                    <Box>
                        <FormControlLabel
                            control={<Checkbox size="small" checked={checked} onChange={handleChange} />}
                            label={<Typography variant="subtitle2">I prefer to maintain my weight</Typography>}
                        />
                    </Box>

                    {formData.weightStatus === 'valid' &&
                        formData.target_weight_status === 'valid' &&
                        formData.goal !== 'same' &&
                        !checked && (
                            <MainCard sx={{ mt: 2, backgroundColor: theme.palette.success[100] }}>
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
                                            onChange={handleTargetGoalChange}
                                            sx={{ display: 'flex', justifyContent: 'center', textAlign: 'center', gap: 2 }}
                                            disabled={isSubmiting}
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
                                                formData.targetGoal === 'normal'
                                                    ? normalWeeks
                                                    : formData.targetGoal === 'fast'
                                                    ? fastWeeks
                                                    : slowWeeks
                                            } weeks to achieve your target goal`}
                                        </Typography>
                                    </FormControl>
                                </Grid>
                            </MainCard>
                        )}

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

export default Goal;
