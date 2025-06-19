import React, { useEffect, useState } from 'react';
import { Grid, Button, Box, TextField, MenuItem, FormControl, InputLabel, FormHelperText, Typography } from '@mui/material';
import InputAdornment from '@mui/material/InputAdornment';
import AnimateButton from 'ui-component/extended/AnimateButton';
import { getDecodedToken } from 'utils/tokenUtils';
import { useTheme } from '@mui/material/styles';
import { energyIntakeCalculator } from 'utils/energyIntakeCalculator';

const ProfileForm1 = ({ page, setPage, formData, setFormData }) => {
    const [disabled, setDisabled] = useState(true);

    const theme = useTheme();
    const decodedToken = getDecodedToken();

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

    useEffect(() => {
        // console.log(formData);
        if (formData.role === 'test') {
            setFormData({ ...formData, country: '' });
            if (
                formData.roleStatus === 'valid' &&
                formData.sexStatus === 'valid' &&
                formData.yobStatus === 'valid' &&
                formData.heightStatus === 'valid' &&
                formData.weightStatus === 'valid' &&
                formData.palStatus === 'valid'
            ) {
                setDisabled(false);
            } else {
                setDisabled(true);
            }
        } else if (formData.role === 'pilot') {
            if (
                formData.roleStatus === 'valid' &&
                formData.countryStatus === 'valid' &&
                formData.sexStatus === 'valid' &&
                formData.yobStatus === 'valid' &&
                formData.heightStatus === 'valid' &&
                formData.weightStatus === 'valid' &&
                formData.palStatus === 'valid'
            ) {
                setDisabled(false);
            } else {
                setDisabled(true);
            }
        }
    }, [
        formData.role,
        formData.roleStatus,
        formData.countryStatus,
        formData.sexStatus,
        formData.yobStatus,
        formData.heightStatus,
        formData.weightStatus,
        formData.palStatus
    ]);

    const handleRoleBlur = () => {
        if (formData.role === '') {
            setFormData({ ...formData, roleStatus: 'invalid' });
        } else {
            setFormData({ ...formData, roleStatus: 'valid' });
        }
    };

    const handleRoleFocus = () => {
        if (formData.role !== '') {
            setFormData({ ...formData, roleStatus: 'valid' });
        }
    };

    const handleCountryBlur = () => {
        if (formData.country === '') {
            setFormData({ ...formData, countryStatus: 'invalid' });
        } else {
            setFormData({ ...formData, countryStatus: 'valid' });
        }
    };

    const handleCountryFocus = () => {
        if (formData.country !== '') {
            setFormData({ ...formData, countryStatus: 'valid' });
        }
    };

    const handleSexBlur = () => {
        if (formData.sex === '') {
            setFormData({ ...formData, sexStatus: 'invalid' });
        } else {
            setFormData({ ...formData, sexStatus: 'valid' });
        }
    };

    const handleSexFocus = () => {
        if (formData.sex !== '') {
            setFormData({ ...formData, sexStatus: 'valid' });
        }
    };

    const handleYobChange = (e) => {
        const value = e.target.value;
        let status = 'typing';

        if (value >= 1904 && value <= 2024) {
            status = 'valid';
        } else if (e.target.value === '') {
            status = 'typing'; // Reset to default if empty
        } else {
            status = 'typing'; // Keep it grey while typing
        }

        setFormData({
            ...formData,
            yob: value,
            yobStatus: status
        });
    };

    const handleYobBlur = () => {
        if (formData.yob < 1904 || formData.yob > 2024) {
            setFormData({ ...formData, yobStatus: 'invalid' });
        }
    };

    const handleYobFocus = () => {
        if (formData.yob === '') {
            setFormData({ ...formData, yobStatus: 'typing' });
        }
    };

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

        // Check if the email format is valid as the user types
        if (value >= 30 && value <= 300) {
            status = 'valid';
        } else if (e.target.value === '') {
            status = 'typing'; // Reset to default if empty
        } else {
            status = 'typing'; // Keep it grey while typing
        }

        setFormData({
            ...formData,
            weight: value,
            weightStatus: status
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

    return (
        <div className="login-page">
            <TextField
                select
                fullWidth
                label="Role"
                variant="outlined"
                margin="normal"
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                onBlur={handleRoleBlur}
                onFocus={handleRoleFocus}
                error={formData.roleStatus === 'invalid'}
                helperText={formData.roleStatus === 'invalid' ? 'Role is required' : ''}
                sx={{
                    '& .MuiFormHelperText-root': {
                        color: 'red'
                    }
                }}
            >
                <MenuItem value="living_lab">Living Lab User (Research Participant)</MenuItem>
                <MenuItem value="consortium">PLANEAT Consortium Member</MenuItem>
                <MenuItem value="test">Othes Unofficial Tester</MenuItem>
            </TextField>

            {formData.role === 'pilot' && (
                <TextField
                    select
                    fullWidth
                    label="Country"
                    variant="outlined"
                    margin="normal"
                    value={formData.country}
                    onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                    onBlur={handleCountryBlur}
                    onFocus={handleCountryFocus}
                    error={formData.countryStatus === 'invalid'}
                    helperText={formData.countryStatus === 'invalid' ? 'Country is required' : ''}
                    sx={{
                        '& .MuiFormHelperText-root': {
                            color: 'red'
                        }
                    }}
                >
                    <MenuItem value="ireland">Ireland</MenuItem>
                    <MenuItem value="spain">Spain</MenuItem>
                    <MenuItem value="hungary">Hungary</MenuItem>
                </TextField>
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
                        label="Sex"
                        variant="outlined"
                        margin="normal"
                        value={formData.sex}
                        onChange={(e) => setFormData({ ...formData, sex: e.target.value })}
                        onBlur={handleSexBlur}
                        onFocus={handleSexFocus}
                        error={formData.sexStatus === 'invalid'}
                        helperText={formData.sexStatus === 'invalid' ? 'Sex is required' : ''}
                        sx={{
                            '& .MuiFormHelperText-root': {
                                color: 'red'
                            }
                        }}
                    >
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
                        onChange={handleYobChange}
                        onBlur={handleYobBlur}
                        onFocus={handleYobFocus}
                        error={formData.yobStatus === 'invalid'}
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
                                color: formData.heightStatus === 'valid' ? 'green' : formData.heightStatus === 'invalid' ? 'red' : 'grey' // Helper text color based on status
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
                                color: formData.weightStatus === 'valid' ? 'green' : formData.weightStatus === 'invalid' ? 'red' : 'grey' // Helper text color based on status
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
                onChange={(e) => setFormData({ ...formData, PAL: e.target.value })}
                onBlur={handlePalBlur}
                onFocus={handlePalFocus}
                error={formData.palStatus === 'invalid'}
                helperText={formData.palStatus === 'invalid' ? 'PAL is required' : ''}
                sx={{
                    '& .MuiFormHelperText-root': {
                        color: 'red'
                    }
                }}
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
                    mt: 2,
                    display: 'flex',
                    justifyContent: 'flex-end'
                }}
            >
                <AnimateButton>
                    <Button
                        disableElevation
                        disabled={disabled}
                        onClick={() => {
                            setPage(page + 1);
                        }}
                        fullWidth
                        size="large"
                        variant="contained"
                        color="success"
                    >
                        Next
                    </Button>
                </AnimateButton>
            </Box>
        </div>
    );
};

export default ProfileForm1;
