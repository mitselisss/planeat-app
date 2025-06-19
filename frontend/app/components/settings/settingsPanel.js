import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';

import { Grid, Typography, Slider, FormControl, RadioGroup, FormControlLabel, Radio } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import PerfectScrollbar from 'react-perfect-scrollbar';

import SubCard from 'ui-component/cards/SubCard';
import { SET_BORDER_RADIUS, SET_FONT_FAMILY } from 'store/actions';
import { gridSpacing } from 'store/constant';
import MainCard from 'ui-component/cards/MainCard';

function valueText(value) {
    return `${value}px`;
}

const SettingsPanel = () => {
    const theme = useTheme();
    const dispatch = useDispatch();
    const customization = useSelector((state) => state.customization);

    // Font family setup
    let initialFont;
    switch (customization.fontFamily) {
        case `'Inter', sans-serif`:
            initialFont = 'Inter';
            break;
        case `'Poppins', sans-serif`:
            initialFont = 'Poppins';
            break;
        default:
            initialFont = 'Roboto';
            break;
    }

    const [fontFamily, setFontFamily] = useState(initialFont);
    useEffect(() => {
        const fontMap = {
            Inter: `'Inter', sans-serif`,
            Poppins: `'Poppins', sans-serif`,
            Roboto: `'Roboto', sans-serif`
        };
        dispatch({ type: SET_FONT_FAMILY, fontFamily: fontMap[fontFamily] });
    }, [fontFamily, dispatch]);

    // Border radius setup
    const [borderRadius, setBorderRadius] = useState(customization.borderRadius);
    useEffect(() => {
        dispatch({ type: SET_BORDER_RADIUS, borderRadius });
    }, [borderRadius, dispatch]);

    const handleBorderRadius = (event, newValue) => setBorderRadius(newValue);

    return (
        <MainCard>
            <Grid container direction="column" spacing={3}>
                <Grid item>
                    <Typography variant="h3" color={theme.palette.success.dark}>
                        Interface Style
                    </Typography>
                    <Typography variant="subtitle2">
                        Personalize the look and feel of the app by choosing your preferred font and corner style of UI elements.
                    </Typography>
                </Grid>
                <Grid item>
                    <PerfectScrollbar component="div">
                        <Grid container spacing={gridSpacing} sx={{ p: 3 }}>
                            <Grid item xs={12}>
                                <SubCard title="Font Style">
                                    <FormControl>
                                        <RadioGroup
                                            value={fontFamily}
                                            onChange={(e) => setFontFamily(e.target.value)}
                                            name="font-family-options"
                                        >
                                            {['Roboto', 'Poppins', 'Inter'].map((font) => (
                                                <FormControlLabel
                                                    key={font}
                                                    value={font}
                                                    control={<Radio />}
                                                    label={font}
                                                    sx={{
                                                        '& .MuiSvgIcon-root': { fontSize: 28 },
                                                        '& .MuiFormControlLabel-label': {
                                                            color: theme.palette.grey[900]
                                                        }
                                                    }}
                                                />
                                            ))}
                                        </RadioGroup>
                                    </FormControl>
                                </SubCard>
                            </Grid>

                            <Grid item xs={12}>
                                <SubCard title="Corner Style">
                                    <Grid container spacing={2} alignItems="center" sx={{ mt: 2.5 }}>
                                        <Grid item>
                                            <Typography variant="h6" color="secondary">
                                                4px
                                            </Typography>
                                        </Grid>
                                        <Grid item xs>
                                            <Slider
                                                size="small"
                                                value={borderRadius}
                                                onChange={handleBorderRadius}
                                                getAriaValueText={valueText}
                                                valueLabelDisplay="on"
                                                step={2}
                                                min={4}
                                                max={24}
                                                color="secondary"
                                            />
                                        </Grid>
                                        <Grid item>
                                            <Typography variant="h6" color="secondary">
                                                24px
                                            </Typography>
                                        </Grid>
                                    </Grid>
                                </SubCard>
                            </Grid>
                        </Grid>
                    </PerfectScrollbar>
                </Grid>
            </Grid>
        </MainCard>
    );
};

export default SettingsPanel;
