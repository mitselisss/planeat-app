import { useState, useEffect } from 'react';

// material-ui
import { Grid, Box } from '@mui/material';

import PersonalInfo from 'components/userProfile/personalInfo';
import Characteristics from 'components/userProfile/characteristics';
import Goal from 'components/userProfile/goal';

import { getDecodedToken } from 'utils/tokenUtils';
import { useNavigate } from '@remix-run/react';
import { getUserProfile } from 'services/api';

import LogoutAfterInactivity from 'utils/logoutAfterInactivity';

// ==============================|| MEAL PLAN PAGE ||============================== //

const UserProfile = () => {
    const [isLoading, setLoading] = useState(true);
    const [isFetchingData, setIsFetchingData] = useState(false);
    const decodedToken = getDecodedToken();
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        username: '',
        email: '',
        role: '',
        roleStatus: 'valid',
        country: '',
        countryStatus: '',
        sex: '',
        sexStatus: 'valid',
        yob: '',
        yobStatus: 'valid',
        height: '',
        heightStatus: 'valid',
        weight: '',
        weightStatus: 'valid',
        PAL: '',
        palStatus: 'valid',
        target_weight: '',
        target_weight_status: 'valid',
        goal: '',
        targetGoal: '',
        allergies: '',
        allergiesStatus: 'valid',
        dietaryPreferences: '',
        dietaryPreferencesStatus: 'valid',
        selectedCuisines: [''],
        selectedCuisinesStatus: 'valid'
    });

    useEffect(() => {
        if (!decodedToken || Object.keys(decodedToken).length === 0) {
            navigate('/pages/login');
        }

        const fetchData = async () => {
            setIsFetchingData(true);

            try {
                const userProfile = await getUserProfile(decodedToken.user_id);
                console.log(userProfile);

                const value =
                    userProfile.pal === '1.4'
                        ? 'sedentary'
                        : userProfile.pal === '1.6'
                        ? 'moderately'
                        : userProfile.pal === '1.8'
                        ? 'active'
                        : userProfile.pal === '2.0'
                        ? 'very_active'
                        : '';
                setFormData((formData) => ({
                    ...formData,
                    username: userProfile.username,
                    email: userProfile.email,
                    role: userProfile.role,
                    country: userProfile.pilot_country,
                    sex: userProfile.sex,
                    yob: userProfile.yob,
                    height: userProfile.height,
                    weight: userProfile.weight,
                    PAL: value,
                    target_weight: userProfile.target_weight,
                    goal: userProfile.goal,
                    targetGoal: userProfile.target_goal,
                    allergies: userProfile.allergies,
                    dietaryPreferences: userProfile.preferences,
                    selectedCuisines: userProfile.cuisine
                }));
            } catch (error) {
                console.log(error.response?.data?.error || 'An unexpected error occurred');
            }

            setIsFetchingData(false);
        };

        fetchData();

        setLoading(false);
    }, []);
    LogoutAfterInactivity();

    return (
        <Grid container spacing={2}>
            <Grid item xs={12}>
                <Grid container spacing={2}>
                    <Grid item xs={12} md={7}>
                        <PersonalInfo isLoading={isLoading} isFetchingData={isFetchingData} formData={formData} setFormData={setFormData} />
                        <Box my={2} />
                        <Characteristics
                            isLoading={isLoading}
                            isFetchingData={isFetchingData}
                            formData={formData}
                            setFormData={setFormData}
                        />
                    </Grid>
                    <Grid item xs={12} md={5}>
                        <Goal isLoading={isLoading} isFetchingData={isFetchingData} formData={formData} setFormData={setFormData} />
                    </Grid>
                </Grid>
            </Grid>
        </Grid>
    );
};

export default UserProfile;
