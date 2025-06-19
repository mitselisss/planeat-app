import { useState, useEffect } from 'react';

// material-ui
import { Grid, Box } from '@mui/material';

import { getDecodedToken } from 'utils/tokenUtils';
import { useNavigate } from '@remix-run/react';

import MainScreen from 'components/settings/mainScreen';
import SettingsPanel from 'components/settings/settingsPanel';

import LogoutAfterInactivity from 'utils/logoutAfterInactivity';

// ==============================|| MEAL PLAN PAGE ||============================== //

const Settings = () => {
    const [isLoading, setLoading] = useState(true);
    const [isFetchingData, setIsFetchingData] = useState(false);
    const decodedToken = getDecodedToken();
    const navigate = useNavigate();

    useEffect(() => {
        if (!decodedToken || Object.keys(decodedToken).length === 0) {
            navigate('/pages/login');
        }
    }, []);
    LogoutAfterInactivity();

    return (
        <Grid container spacing={2}>
            <Grid item xs={12}>
                <Grid container spacing={2}>
                    <Grid item xs={12} md={7}>
                        <MainScreen />
                    </Grid>
                    <Grid item xs={12} md={5}>
                        <SettingsPanel />
                    </Grid>
                </Grid>
            </Grid>
        </Grid>
    );
};

export default Settings;
