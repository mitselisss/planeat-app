import { useState, useEffect } from 'react';

// material-ui
import { Grid, Box, Typography } from '@mui/material';

// project imports
import MainCard from 'ui-component/cards/MainCard';
import { getDecodedToken } from 'utils/tokenUtils';
import { useNavigate } from '@remix-run/react';
import LogoutAfterInactivity from 'utils/logoutAfterInactivity';
import { userActions } from 'services/api';

import image1 from '../../assets/images/about/Group-649.png';
import image2 from '../../assets/images/about/Group-613-1.jpg';
import image3 from '../../assets/images/about/HAPPY-PEOPLE-1.png';
import image4 from '../../assets/images/about/image-25-1.png';

// material-ui
import { useTheme, styled } from '@mui/material/styles';
import theme from 'themes';

// ==============================|| SAMPLE PAGE ||============================== //

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

const SamplePage = () => {
    const decodedToken = getDecodedToken();
    const navigate = useNavigate();
    const theme = useTheme();

    useEffect(() => {
        const trackLogin = async () => {
            if (!decodedToken || Object.keys(decodedToken).length === 0) {
                navigate('/pages/login');
            } else {
                try {
                    await userActions(decodedToken.user_id, 'about');
                } catch (error) {
                    console.log(error.response?.data?.error || 'An unexpected error occurred');
                }
            }
        };

        trackLogin();
    }, []);

    LogoutAfterInactivity();

    return (
        <MainCard sx={{ backgroundColor: theme.palette.success.light }}>
            <Grid container spacing={2}>
                <Grid item xs={12}>
                    <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                            <CardWrapper>
                                <Box display="flex" flexDirection="row" alignItems="flex-start" gap={2}>
                                    <Box>
                                        <img
                                            src={image1}
                                            alt="About section visual"
                                            style={{ width: '200px', height: 'auto', borderRadius: '8px' }}
                                        />
                                    </Box>

                                    <Box>
                                        <Typography variant="h4" gutterBottom color={theme.palette.error.dark}>
                                            ABOUT
                                        </Typography>
                                        <Box
                                            sx={{
                                                borderBottom: `1px solid ${theme.palette.error.dark}`,
                                                width: '100%',
                                                mb: 2 // Adds margin below the line
                                            }}
                                        />
                                        <Typography>
                                            PLAN’EAT is a Horizon Europe research project, funded by the European Commission, which aims at
                                            transforming food systems and food environments towards healthy and sustainable dietary
                                            behaviour. The project started in September 2022 and will last for 4 years.
                                        </Typography>
                                    </Box>
                                </Box>
                            </CardWrapper>
                            <Box my={2} />
                            <CardWrapper>
                                <Box display="flex" flexDirection="row" alignItems="flex-start" gap={2}>
                                    <Box>
                                        <Typography variant="h4" gutterBottom color={theme.palette.error.dark}>
                                            OBJECTIVES
                                        </Typography>

                                        <Box
                                            sx={{
                                                borderBottom: `1px solid ${theme.palette.error.dark}`,
                                                width: '100%',
                                                mb: 2 // Adds margin below the line
                                            }}
                                        />

                                        <Typography>
                                            THE MAIN OBJECTIVES OF PLAN’EAT ARE: to understand the underlying factors and drivers
                                            influencing dietary behaviour, to measure, compare and ‘monetize’ the environmental, social and
                                            health impacts of 3 dominant European dietary patterns through True Cost Accounting (TCA), and
                                            to co-design effective recommendations, tools and interventions that allow food system actors to
                                            steer a transition towards healthier and more sustainable dietary behaviour.
                                        </Typography>
                                    </Box>

                                    <Box>
                                        <img
                                            src={image2}
                                            alt="About section visual"
                                            style={{ width: '200px', height: 'auto', borderRadius: '8px' }}
                                        />
                                    </Box>
                                </Box>
                            </CardWrapper>
                            <Box my={2} />
                            <CardWrapper>
                                <Box display="flex" flexDirection="row" alignItems="flex-start" gap={2}>
                                    <Box>
                                        <img
                                            src={image3}
                                            alt="About section visual"
                                            style={{ width: '200px', height: 'auto', borderRadius: '8px' }}
                                        />
                                    </Box>

                                    <Box>
                                        <Typography variant="h4" gutterBottom color={theme.palette.error.dark}>
                                            PROJECT APPROACH
                                        </Typography>
                                        <Box
                                            sx={{
                                                borderBottom: `1px solid ${theme.palette.error.dark}`,
                                                width: '100%',
                                                mb: 2 // Adds margin below the line
                                            }}
                                        />
                                        <Typography>
                                            PLAN’EAT will implement a systemic and co-creation approach at macro (food system), meso (food
                                            environment) and micro (individual) levels. Various socio-cultural and geographic contexts will
                                            be considered by implementing 9 Living Labs (LLs), 5 pan-European food value chain Consultation
                                            and Working Groups (CWGs) and 1 Policy Lab.
                                        </Typography>
                                    </Box>
                                </Box>
                            </CardWrapper>
                        </Grid>
                        <Grid item xs={12} md={6}>
                            {/* <TotalEnergyRequirements
                                        isLoading={isLoading}
                                        setSelectedWeek={(selectedWeek) => {
                                            setWeek(selectedWeek);
                                        }}
                                    /> */}

                            <CardWrapper>
                                <Box display="flex" flexDirection="column" gap={2}>
                                    <Box>
                                        <Typography variant="h4" gutterBottom color={theme.palette.error.dark}>
                                            METHODOLOGY
                                        </Typography>
                                        <Box
                                            sx={{
                                                borderBottom: `1px solid ${theme.palette.error.dark}`,
                                                width: '100%',
                                                mb: 2 // Adds margin below the line
                                            }}
                                        />
                                        <Typography>
                                            The dietary patterns of 11 European countries will be mapped and assessed in terms of
                                            environmental, socio-economic and health impacts. Impacts will then be translated into true
                                            costs for 3 dominant dietary patterns. The micro-meso-macro factors influencing dietary
                                            behaviours with the highest potential for change will be analysed. The knowledge and scientific
                                            evidence obtained will feed into the co-design and test of more than 10 effective solutions
                                            adjusted to different contexts and end-users.
                                        </Typography>
                                    </Box>
                                    <Box my={1} />
                                    <Box Box display="flex" justifyContent="center">
                                        <img
                                            src={image4}
                                            alt="About section visual"
                                            style={{ width: '450px', height: 'auto', borderRadius: '8px' }}
                                        />
                                    </Box>
                                </Box>
                            </CardWrapper>
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
        </MainCard>
    );
};

export default SamplePage;
