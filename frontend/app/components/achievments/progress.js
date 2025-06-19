import React from 'react';
import { Box, LinearProgress, Typography } from '@mui/material';

const LoginMilestones = ['0', '3 Logins', '10 Logins', '20 Logins'];
const progress = 10;

export default function MilestoneProgressBar() {
    return (
        <Box width="100%" px={4} py={2}>
            {/* Milestone labels */}
            <Box display="flex" justifyContent="space-between" mb={1}>
                {LoginMilestones.map((milestone, index) => (
                    <Typography key={index} variant="caption" color="textSecondary">
                        {milestone}
                    </Typography>
                ))}
            </Box>

            {/* Progress bar container */}
            <Box position="relative">
                <LinearProgress
                    variant="determinate"
                    value={progress}
                    sx={{
                        height: 10,
                        borderRadius: 5,
                        backgroundColor: '#e0e0e0',
                        '& .MuiLinearProgress-bar': {
                            borderRadius: 5,
                            backgroundColor: '#1976d2'
                        }
                    }}
                />

                {/* Milestone dots */}
                <Box
                    position="absolute"
                    top="50%"
                    left={0}
                    right={0}
                    display="flex"
                    justifyContent="space-between"
                    alignItems="center"
                    sx={{ transform: 'translateY(-50%)' }}
                >
                    {LoginMilestones.map((_, index) => (
                        <Box
                            key={index}
                            width={12}
                            height={12}
                            borderRadius="50%"
                            bgcolor={progress >= index * 25 ? '#1976d2' : '#ccc'}
                            border="2px solid white"
                            zIndex={1}
                        />
                    ))}
                </Box>
            </Box>
        </Box>
    );
}
