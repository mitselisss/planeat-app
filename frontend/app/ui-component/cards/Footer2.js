import * as React from 'react';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Link from '@mui/material/Link';
import Grid from '@mui/material/Grid';
import { Facebook, Instagram, Twitter, LinkedIn } from '@mui/icons-material';
import { Box, Divider } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import Logo from 'ui-component/Logo';
import EUlogo from '../../assets/images/Flag_of_Europe.svg.png';
import MainCard from './MainCard';

export default function Footer2() {
    const theme = useTheme();

    return (
        <MainCard>
            <Grid item xs={12} sm={4} textAlign="center">
                {/* <Link to="https://planeat-project.eu/">
                            <Logo />
                        </Link> */}

                <Typography sx={{ mt: '10px' }} variant="body2">
                    <span style={{ color: theme.palette.success.dark }}>PLAN’EAT</span> is a Horizon Europe research project (2022–2026)
                    bringing together 24 partners, funded by the EU under Grant Agreement No. 101061023.
                </Typography>
            </Grid>

            <Grid item xs={12} sm={4} textAlign="center" mt={5}>
                <Typography variant="body2" gutterBottom>
                    Follow Us
                </Typography>
                <Box
                    sx={{
                        display: 'flex',
                        gap: 1
                    }}
                >
                    <Box
                        sx={{
                            width: 40,
                            height: 40,
                            backgroundColor: theme.palette.primary.light,
                            borderTopLeftRadius: '12px',
                            borderBottomRightRadius: '12px',
                            display: 'flex',
                            justifyContent: 'center',
                            alignItems: 'center',
                            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)', // Optional shadow for better appearance
                            position: 'relative'
                        }}
                    >
                        <Link
                            href="https://www.facebook.com/profile.php?id=100090028100246"
                            sx={{ color: theme.palette.success.dark }}
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            <Facebook />
                        </Link>
                    </Box>

                    <Box
                        sx={{
                            width: 40,
                            height: 40,
                            backgroundColor: theme.palette.primary.light,
                            borderTopLeftRadius: '12px',
                            borderBottomRightRadius: '12px',
                            display: 'flex',
                            justifyContent: 'center',
                            alignItems: 'center',
                            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)', // Optional shadow for better appearance
                            position: 'relative'
                        }}
                    >
                        <Link
                            href="https://x.com/PlanEat_eu"
                            sx={{ color: theme.palette.success.dark }}
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            <Twitter />
                        </Link>
                    </Box>

                    <Box
                        sx={{
                            width: 40,
                            height: 40,
                            backgroundColor: theme.palette.primary.light,
                            borderTopLeftRadius: '12px',
                            borderBottomRightRadius: '12px',
                            display: 'flex',
                            justifyContent: 'center',
                            alignItems: 'center',
                            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)', // Optional shadow for better appearance
                            position: 'relative'
                        }}
                    >
                        <Link
                            href="https://www.linkedin.com/company/plan-eat-project/posts/?feedView=all"
                            sx={{ color: theme.palette.success.dark }}
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            <LinkedIn />
                        </Link>
                    </Box>
                    <Box
                        sx={{
                            width: 40,
                            height: 40,
                            backgroundColor: theme.palette.primary.light,
                            borderTopLeftRadius: '12px',
                            borderBottomRightRadius: '12px',
                            display: 'flex',
                            justifyContent: 'center',
                            alignItems: 'center',
                            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)', // Optional shadow for better appearance
                            position: 'relative'
                        }}
                    >
                        <Link
                            href="https://www.instagram.com/planeat.eu/"
                            sx={{ pl: 1, pr: 1, color: theme.palette.success.dark }}
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            <Instagram />
                        </Link>
                    </Box>
                </Box>
            </Grid>

            <Box mt={5}>
                <Typography variant="body2" align="center">
                    {'Copyright © '}
                    <Link color={theme.palette.success.dark} href="https://planeat-project.eu/" target="_blank" rel="noopener noreferrer">
                        planeat-project.eu
                    </Link>{' '}
                    {new Date().getFullYear()}
                    {'.'}
                </Typography>
            </Box>
        </MainCard>
    );
}
