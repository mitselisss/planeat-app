import { useNavigate } from '@remix-run/react';
import { useState, useRef, useEffect } from 'react';
import { useSelector } from 'react-redux';

// material-ui
import { useTheme } from '@mui/material/styles';
import {
    Avatar,
    Box,
    Card,
    CardContent,
    Chip,
    ClickAwayListener,
    Divider,
    Grid,
    InputAdornment,
    List,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    OutlinedInput,
    Paper,
    Popper,
    Stack,
    Switch,
    Typography
} from '@mui/material';

// third-party
import PerfectScrollbar from 'react-perfect-scrollbar';

// project imports
import MainCard from 'ui-component/cards/MainCard';
import Transitions from 'ui-component/extended/Transitions';
import UpgradePlanCard from './UpgradePlanCard';
import { getDecodedToken } from 'utils/tokenUtils';
import { getUserProfile } from 'services/api';

// import { Dialog, DialogActions, DialogContent, DialogTitle, Button } from '@mui/material';

// assets
import { IconLogout, IconSearch, IconSettings, IconUser } from '../../../../../node_modules/@tabler/icons-react';
import User2 from 'assets/images/users/user-circle-icon-lg.png';

// ==============================|| PROFILE MENU ||============================== //

const ProfileSection = () => {
    const theme = useTheme();
    const customization = useSelector((state) => state.customization);
    const navigate = useNavigate();
    const decodedToken = getDecodedToken();

    const [username, setUsername] = useState();
    const [sdm, setSdm] = useState(true);
    const [value, setValue] = useState('');
    const [notification, setNotification] = useState(false);
    const [selectedIndex, setSelectedIndex] = useState(-1);
    const [open, setOpen] = useState(false);
    // const [openDialog, setOpenDialog] = useState(false);
    /**
     * anchorRef is used on different componets and specifying one type leads to other components throwing an error
     * */
    const anchorRef = useRef(null);

    const handleLogout = async () => {
        localStorage.removeItem('token');
        localStorage.removeItem('expireTime');

        navigate('/pages/login');

        // const shoppingList = JSON.parse(localStorage.getItem('shoppingList'));
        // // console.log('kajsndj', shoppingList.length);
        // if (shoppingList && shoppingList.length >= 1) {
        //     // Open the dialog if the shopping list has unsaved changes
        //     setOpenDialog(true);
        // } else {
        //     // Direct logout if shopping list is empty or no unsaved changes
        //     localStorage.removeItem('token');
        //     localStorage.removeItem('expireTime');

        //     navigate('/pages/login');
        // }
    };

    // const handleDialogClose = (confirm) => {
    //     // console.log(confirm);
    //     if (confirm) {
    //         // If user confirms, logout
    //         localStorage.removeItem('token');
    //         localStorage.removeItem('expireTime');
    //         localStorage.removeItem('shoppingList');
    //         navigate('/pages/login');
    //     }
    //     // Close the dialog regardless of confirmation
    //     setOpenDialog(false);
    // };

    const handleClose = (event) => {
        if (anchorRef.current && anchorRef.current.contains(event.target)) {
            return;
        }
        setOpen(false);
    };

    const handleListItemClick = (event, index, route = '') => {
        setSelectedIndex(index);
        handleClose(event);

        if (route && route === 'userprofile') {
            navigate('/userProfile');
        }
        if (route && route === 'settings') {
            navigate('/settings');
        }
    };
    const handleToggle = () => {
        setOpen((prevOpen) => !prevOpen);
    };

    const prevOpen = useRef(open);
    useEffect(() => {
        if (prevOpen.current === true && open === false) {
            anchorRef.current.focus();
        }

        prevOpen.current = open;
    }, [open]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const userProfile = await getUserProfile(decodedToken.user_id);
                setUsername(userProfile.username);
            } catch (error) {
                console.log(error.response?.data?.error || 'An unexpected error occurred');
            }
        };

        fetchData();
    }, []);

    return (
        <>
            <Chip
                sx={{
                    height: '48px',
                    alignItems: 'center',
                    borderRadius: '27px',
                    transition: 'all .2s ease-in-out',
                    borderColor: theme.palette.primary.light,
                    backgroundColor: theme.palette.primary.light,
                    '&[aria-controls="menu-list-grow"], &:hover': {
                        borderColor: theme.palette.primary.main,
                        background: `${theme.palette.primary.main}!important`,
                        color: theme.palette.primary.light,
                        '& svg': {
                            stroke: theme.palette.primary.light
                        }
                    },
                    '& .MuiChip-label': {
                        lineHeight: 0
                    }
                }}
                icon={
                    <Avatar
                        src={User2}
                        sx={{
                            ...theme.typography.mediumAvatar,
                            margin: '8px 0 8px 8px !important',
                            cursor: 'pointer'
                        }}
                        ref={anchorRef}
                        aria-controls={open ? 'menu-list-grow' : undefined}
                        aria-haspopup="true"
                        color="inherit"
                    />
                }
                label={<IconSettings stroke={1.5} size="1.5rem" color={theme.palette.primary.main} />}
                variant="outlined"
                ref={anchorRef}
                aria-controls={open ? 'menu-list-grow' : undefined}
                aria-haspopup="true"
                onClick={handleToggle}
                color="primary"
            />
            <Popper
                placement="bottom-end"
                open={open}
                anchorEl={anchorRef.current}
                role={undefined}
                transition
                disablePortal
                popperOptions={{
                    modifiers: [
                        {
                            name: 'offset',
                            options: {
                                offset: [0, 14]
                            }
                        }
                    ]
                }}
            >
                {({ TransitionProps }) => (
                    <Transitions in={open} {...TransitionProps}>
                        <Paper>
                            <ClickAwayListener onClickAway={handleClose}>
                                <MainCard border={false} elevation={16} content={false} boxShadow shadow={theme.shadows[16]}>
                                    <Box sx={{ p: 2 }}>
                                        <Stack>
                                            <Stack direction="row" spacing={0.5} alignItems="center">
                                                <Typography variant="h4">Hello,</Typography>
                                                {decodedToken?.user_id && (
                                                    <Typography component="span" variant="h4" sx={{ fontWeight: 400 }}>
                                                        {username}
                                                    </Typography>
                                                )}
                                            </Stack>
                                            {/* <Typography variant="subtitle2">Project Admin</Typography> */}
                                        </Stack>
                                        {/* <OutlinedInput
                                            sx={{ width: '100%', pr: 1, pl: 2, my: 2 }}
                                            id="input-search-profile"
                                            value={value}
                                            onChange={(e) => setValue(e.target.value)}
                                            placeholder="Search profile options"
                                            startAdornment={
                                                <InputAdornment position="start">
                                                    <IconSearch stroke={1.5} size="1rem" color={theme.palette.grey[500]} />
                                                </InputAdornment>
                                            }
                                            aria-describedby="search-helper-text"
                                            inputProps={{
                                                'aria-label': 'weight'
                                            }}
                                        /> */}
                                        <Divider />
                                    </Box>
                                    <PerfectScrollbar
                                        style={{
                                            height: '100%',
                                            maxHeight: 'calc(100vh - 250px)',
                                            overflowX: 'hidden'
                                        }}
                                    >
                                        <Box sx={{ p: 2 }}>
                                            {/* <UpgradePlanCard />
                                            <Divider />
                                            <Card
                                                sx={{
                                                    bgcolor: theme.palette.primary.light,
                                                    my: 2
                                                }}
                                            >
                                                <CardContent>
                                                    <Grid container spacing={3} direction="column">
                                                        <Grid item>
                                                            <Grid item container alignItems="center" justifyContent="space-between">
                                                                <Grid item>
                                                                    <Typography variant="subtitle1">Start DND Mode</Typography>
                                                                </Grid>
                                                                <Grid item>
                                                                    <Switch
                                                                        color="primary"
                                                                        checked={sdm}
                                                                        onChange={(e) => setSdm(e.target.checked)}
                                                                        name="sdm"
                                                                        size="small"
                                                                    />
                                                                </Grid>
                                                            </Grid>
                                                        </Grid>
                                                        <Grid item>
                                                            <Grid item container alignItems="center" justifyContent="space-between">
                                                                <Grid item>
                                                                    <Typography variant="subtitle1">Allow Notifications</Typography>
                                                                </Grid>
                                                                <Grid item>
                                                                    <Switch
                                                                        checked={notification}
                                                                        onChange={(e) => setNotification(e.target.checked)}
                                                                        name="sdm"
                                                                        size="small"
                                                                    />
                                                                </Grid>
                                                            </Grid>
                                                        </Grid>
                                                    </Grid>
                                                </CardContent>
                                            </Card>
                                            <Divider /> */}
                                            <List
                                                component="nav"
                                                sx={{
                                                    width: '100%',
                                                    maxWidth: 350,
                                                    minWidth: 300,
                                                    backgroundColor: theme.palette.background.paper,
                                                    borderRadius: '10px',
                                                    [theme.breakpoints.down('md')]: {
                                                        minWidth: '100%'
                                                    },
                                                    '& .MuiListItemButton-root': {
                                                        mt: 0.5
                                                    }
                                                }}
                                            >
                                                <ListItemButton
                                                    sx={{
                                                        borderRadius: `${customization.borderRadius}px`
                                                    }}
                                                    selected={selectedIndex === 0}
                                                    onClick={(event) => handleListItemClick(event, 0, 'userprofile')}
                                                >
                                                    <ListItemIcon>
                                                        <IconUser stroke={1.5} size="1.3rem" />
                                                    </ListItemIcon>
                                                    <ListItemText primary={<Typography variant="body2">User Profile</Typography>} />
                                                </ListItemButton>
                                                <ListItemButton
                                                    sx={{
                                                        borderRadius: `${customization.borderRadius}px`
                                                    }}
                                                    selected={selectedIndex === 1}
                                                    onClick={(event) => handleListItemClick(event, 1, 'settings')}
                                                >
                                                    <ListItemIcon>
                                                        <IconSettings stroke={1.5} size="1.3rem" />
                                                    </ListItemIcon>
                                                    <ListItemText primary={<Typography variant="body2">Settings</Typography>} />
                                                </ListItemButton>
                                                {/* <ListItemButton
                                                    sx={{
                                                        borderRadius: `${customization.borderRadius}px`
                                                    }}
                                                    selected={selectedIndex === 1}
                                                    onClick={(event) => handleListItemClick(event, 1, '#')}
                                                >
                                                    <ListItemIcon>
                                                        <IconUser stroke={1.5} size="1.3rem" />
                                                    </ListItemIcon>
                                                    <ListItemText
                                                        primary={
                                                            <Grid container spacing={1} justifyContent="space-between">
                                                                <Grid item>
                                                                    <Typography variant="body2">Social Profile</Typography>
                                                                </Grid>
                                                                <Grid item>
                                                                    <Chip
                                                                        label="02"
                                                                        size="small"
                                                                        sx={{
                                                                            bgcolor: theme.palette.warning.dark,
                                                                            color: theme.palette.background.default
                                                                        }}
                                                                    />
                                                                </Grid>
                                                            </Grid>
                                                        }
                                                    />
                                                </ListItemButton> */}
                                                <ListItemButton
                                                    sx={{
                                                        borderRadius: `${customization.borderRadius}px`
                                                    }}
                                                    selected={selectedIndex === 4}
                                                    onClick={handleLogout}
                                                >
                                                    <ListItemIcon>
                                                        <IconLogout stroke={1.5} size="1.3rem" />
                                                    </ListItemIcon>
                                                    <ListItemText primary={<Typography variant="body2">Logout</Typography>} />
                                                </ListItemButton>
                                            </List>
                                        </Box>
                                    </PerfectScrollbar>
                                </MainCard>
                            </ClickAwayListener>
                        </Paper>
                    </Transitions>
                )}
            </Popper>

            {/* <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
                <DialogTitle>
                    <Typography variant="h3">Confirm Logout</Typography>
                </DialogTitle>
                <Box></Box>
                <DialogContent>
                    <Typography>There are unsaved changes in your shopping list that will be lost.</Typography>
                    <Typography mt={3}>Are you sure you want to log out?</Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => handleDialogClose(false)} color="primary">
                        Cancel
                    </Button>
                    <Button onClick={() => handleDialogClose(true)} color="primary">
                        Logout
                    </Button>
                </DialogActions>
            </Dialog> */}
        </>
    );
};

export default ProfileSection;
