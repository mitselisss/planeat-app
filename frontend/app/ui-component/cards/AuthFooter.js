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

export default function Footer() {
    const theme = useTheme();

    return (
        <Box
            component="footer"
            sx={{
                backgroundColor: theme.palette.success.dark,
                p: 6
            }}
        >
            <Container maxWidth="lg">
                <Grid container spacing={5}>
                    <Grid item xs={12} sm={4}>
                        <Link to="https://planeat-project.eu/">
                            <Logo />
                        </Link>

                        <Typography sx={{ mt: '10px' }} variant="body2" color={theme.palette.primary.light}>
                            <Link
                                href="https://planeat-project.eu/"
                                sx={{ color: theme.palette.primary.light }}
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                PLANEAT
                            </Link>{' '}
                            is a Horizon Europe research project, bringing together 24 partners and running from September 2022 to 2026.
                        </Typography>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <img src={EUlogo} style={{ height: 55, width: 85 }} alt="EUlogo" />;
                        <Typography sx={{ mt: '10px' }} variant="body2" color={theme.palette.primary.light}>
                            This project has received funding from the European Union’s Horizon Europe Research and Innovation programme
                            under Grant Agreement n°{' '}
                            <Link
                                href="https://cordis.europa.eu/project/id/101061023"
                                sx={{ color: theme.palette.primary.light }}
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                101061023
                            </Link>
                            .
                        </Typography>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <Typography variant="h6" color={theme.palette.primary.light} gutterBottom>
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
                </Grid>
                <Box mt={5}>
                    <Typography variant="body2" color={theme.palette.primary.light} align="center">
                        {'Copyright © '}
                        <Link color="inherit" href="https://planeat-project.eu/" target="_blank" rel="noopener noreferrer">
                            planeat-project.eu
                        </Link>{' '}
                        {new Date().getFullYear()}
                        {'.'}
                    </Typography>
                </Box>
            </Container>
        </Box>
    );
}
