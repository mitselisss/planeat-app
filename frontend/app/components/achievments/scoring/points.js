import React from 'react';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography } from '@mui/material';

import { useTheme, styled } from '@mui/material/styles';

const pointsData = [
    { action: 'Login (once per day)', points: '5 pts' },
    { action: 'Bonus: 3 Logins per week', points: '+10 pts' },
    { action: 'Bonus: 7 Logins per week', points: '+20 pts' },
    { action: 'Meal Check/Uncheck (per meal)', points: '2/-2 pts' },
    { action: 'Bonus: All 5 meals in a day', points: '+10 pts' },
    { action: 'Bonus: All 35 meals in a week', points: '+30 pts' },
    { action: 'Download shopping list (once per day)', points: '5 pts' },
    { action: 'Download weekly plan (once per week)', points: '10 pts' }
];

export default function PointsTable() {
    const theme = useTheme();
    return (
        <TableContainer component={Paper} sx={{ maxWidth: 700, margin: 'auto', mt: 4 }}>
            {/* <Typography variant="h6" align="center" sx={{ p: 2 }}>
                Points System
            </Typography> */}
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>
                            <Typography color={theme.palette.success.dark} fontWeight="bold">
                                Action
                            </Typography>
                        </TableCell>
                        <TableCell align="right">
                            <Typography color={theme.palette.success.dark} fontWeight="bold">
                                Points
                            </Typography>
                        </TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {pointsData.map((item, index) => (
                        <TableRow key={index}>
                            <TableCell>{item.action}</TableCell>
                            <TableCell align="right">{item.points}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
}
