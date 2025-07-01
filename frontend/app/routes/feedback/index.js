import { useState, useEffect } from 'react';

// material-ui
import { Grid, Box, Typography, TextField, Button, Snackbar, Alert } from '@mui/material';

// project imports
import MainCard from 'ui-component/cards/MainCard';
import { getDecodedToken } from 'utils/tokenUtils';
import { useNavigate } from '@remix-run/react';
import LogoutAfterInactivity from 'utils/logoutAfterInactivity';
import { userActions, userFeedback } from 'services/api';

import feedbackImage from '../../assets/images/feedback/Frame-615.png';

// material-ui styling
import { useTheme, styled } from '@mui/material/styles';

// styles
const CardWrapper = styled(MainCard)(({ theme }) => ({
    overflow: 'hidden',
    position: 'relative',
    '&:after': {
        content: '""',
        position: 'absolute',
        width: 210,
        height: 210,
        background: `linear-gradient(210.04deg, ${theme.palette.success.light} -50.94%, rgba(144, 202, 249, 0) 83.49%)`,
        borderRadius: '50%',
        top: -30,
        right: -180
    },
    '&:before': {
        content: '""',
        position: 'absolute',
        width: 210,
        height: 210,
        background: `linear-gradient(140.9deg, ${theme.palette.success.light} -14.02%, rgba(144, 202, 249, 0) 70.50%)`,
        borderRadius: '50%',
        top: -160,
        right: -130
    }
}));

const FeedBackPage = () => {
    const decodedToken = getDecodedToken();
    const navigate = useNavigate();
    const theme = useTheme();

    const [feedback, setFeedback] = useState('');
    const [message, setMessage] = useState('');
    const [openSnackbar, setOpenSnackbar] = useState(false);

    useEffect(() => {
        const trackLogin = async () => {
            if (!decodedToken || Object.keys(decodedToken).length === 0) {
                navigate('/pages/login');
            } else {
                try {
                    await userActions(decodedToken.user_id, 'feedback');
                } catch (error) {
                    console.log(error.response?.data?.error || 'An unexpected error occurred');
                }
            }
        };

        trackLogin();
    }, []);

    const handleChange = (e) => {
        setFeedback(e.target.value);
    };

    const handleSend = async () => {
        try {
            const response = await userFeedback(decodedToken.user_id, feedback);
            if (response.status === 200) {
                setFeedback('');
                setMessage('Thank you for your feedback. We will try our best to improve!');
                setOpenSnackbar(true);
            }
        } catch (error) {
            console.log(error.response?.data?.error || 'An unexpected error occurred');
        }
    };

    const handleSnackbarClose = () => {
        setOpenSnackbar(false);
    };

    LogoutAfterInactivity();

    return (
        <MainCard sx={{ backgroundColor: theme.palette.success.light }}>
            <Grid container spacing={2} justifyContent="center">
                <Grid item xs={12} md={9}>
                    <Grid container spacing={2} justifyContent="center">
                        <Grid item xs={12} md={9}>
                            {/* ABOUT Section */}
                            <CardWrapper>
                                <Box display="flex" flexDirection="row" alignItems="flex-start" gap={2}>
                                    <Box>
                                        <img
                                            src={feedbackImage}
                                            alt="Feedback visual"
                                            style={{ width: '200px', height: 'auto', borderRadius: '8px' }}
                                        />
                                    </Box>
                                    <Box>
                                        <Typography variant="h4" gutterBottom color={theme.palette.error.dark}>
                                            System Usability Score
                                        </Typography>
                                        <Box
                                            sx={{
                                                borderBottom: `1px solid ${theme.palette.error.dark}`,
                                                width: '100%',
                                                mb: 2
                                            }}
                                        />
                                        <Typography>
                                            Help us improve by taking a quick survey on your experience with the app. Your responses will
                                            guide us in making the platform better for you.
                                        </Typography>
                                        <Box mb={2} />
                                        <Typography>
                                            <a
                                                href="#"
                                                style={{ color: theme.palette.success.dark, textDecoration: 'none' }}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                            >
                                                👉 Take the Survey
                                            </a>
                                        </Typography>
                                    </Box>
                                </Box>
                            </CardWrapper>

                            <Box my={2} />

                            {/* FEEDBACK Section */}
                            <CardWrapper>
                                <Box>
                                    <Typography variant="h4" gutterBottom color={theme.palette.error.dark}>
                                        Please share any suggestions for improvement.
                                    </Typography>

                                    <Box
                                        sx={{
                                            borderBottom: `1px solid ${theme.palette.error.dark}`,
                                            width: '100%',
                                            mb: 4
                                        }}
                                    />
                                    <TextField
                                        fullWidth
                                        multiline
                                        minRows={5}
                                        variant="outlined"
                                        placeholder="Write your feedback here..."
                                        value={feedback}
                                        onChange={handleChange}
                                    />
                                    <Box mt={2} display="flex" justifyContent="flex-end">
                                        <Button variant="contained" color="success" disabled={!feedback} onClick={handleSend}>
                                            Send
                                        </Button>
                                    </Box>
                                </Box>
                            </CardWrapper>
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>

            {/* Snackbar for success feedback */}
            <Snackbar
                open={openSnackbar}
                autoHideDuration={4000}
                onClose={handleSnackbarClose}
                anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
            >
                <Alert onClose={handleSnackbarClose} severity="success" sx={{ width: '100%' }}>
                    {message}
                </Alert>
            </Snackbar>
        </MainCard>
    );
};

export default FeedBackPage;
