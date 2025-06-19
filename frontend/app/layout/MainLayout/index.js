import { useState, useEffect } from 'react';
import { Outlet } from '@remix-run/react';
import { useDispatch, useSelector } from 'react-redux';
import { styled, useTheme } from '@mui/material/styles';
import { AppBar, Box, CssBaseline, Toolbar, useMediaQuery } from '@mui/material';
import { SET_MENU } from 'store/actions';
import { drawerWidth } from 'store/constant';
import navigation from 'menu-items';
import Breadcrumbs from 'ui-component/extended/Breadcrumbs';
import Customization from 'layout/Customization';
import Header from './Header';
import Sidebar from './Sidebar';
import { IconChevronRight } from '@tabler/icons-react';

const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' })(({ theme, open }) => ({
    ...theme.typography.mainContent,
    ...(!open && {
        borderBottomLeftRadius: 0,
        borderBottomRightRadius: 0,
        transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen
        }),
        [theme.breakpoints.up('md')]: {
            marginLeft: -(drawerWidth - 20),
            width: `calc(100% - ${drawerWidth}px)`
        },
        [theme.breakpoints.down('md')]: {
            marginLeft: '20px',
            width: `calc(100% - ${drawerWidth}px)`,
            padding: '16px'
        },
        [theme.breakpoints.down('sm')]: {
            marginLeft: '10px',
            width: `calc(100% - ${drawerWidth}px)`,
            padding: '16px',
            marginRight: '10px'
        }
    }),
    ...(open && {
        transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.easeOut,
            duration: theme.transitions.duration.enteringScreen
        }),
        marginLeft: 0,
        borderBottomLeftRadius: 0,
        borderBottomRightRadius: 0,
        width: `calc(100% - ${drawerWidth}px)`,
        [theme.breakpoints.down('md')]: {
            marginLeft: '20px'
        },
        [theme.breakpoints.down('sm')]: {
            marginLeft: '10px'
        }
    })
}));

const MainLayout = () => {
    const theme = useTheme();
    const matchDownMd = useMediaQuery(theme.breakpoints.down('md'));

    // Redux state for desktop drawer:
    const leftDrawerOpened = useSelector((state) => state.customization.opened);
    const dispatch = useDispatch();

    // New state for mobile drawer:
    const [mobileOpen, setMobileOpen] = useState(false);
    // Local state to track if component has mounted (client-only)
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    const handleDrawerToggle = () => {
        if (matchDownMd) {
            setMobileOpen((prev) => !prev);
        } else {
            dispatch({ type: SET_MENU, opened: !leftDrawerOpened });
        }
    };

    return (
        <Box sx={{ display: 'flex' }}>
            <CssBaseline />

            <AppBar
                enableColorOnDark
                position="fixed"
                color="inherit"
                elevation={0}
                sx={{
                    bgcolor: theme.palette.background.default,
                    transition: leftDrawerOpened ? theme.transitions.create('width') : 'none'
                }}
            >
                <Toolbar>
                    <Header handleLeftDrawerToggle={handleDrawerToggle} />
                </Toolbar>
            </AppBar>

            {mounted && (
                <Sidebar
                    // Use mobileOpen on mobile, leftDrawerOpened on desktop
                    drawerOpen={matchDownMd ? mobileOpen : leftDrawerOpened}
                    drawerToggle={handleDrawerToggle}
                />
            )}

            <Main theme={theme} open={leftDrawerOpened}>
                <Breadcrumbs separator={IconChevronRight} navigation={navigation} icon title rightAlign />
                <Outlet />
            </Main>
            <Customization />
        </Box>
    );
};

export default MainLayout;
