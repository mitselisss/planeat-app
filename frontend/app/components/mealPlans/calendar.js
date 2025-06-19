import React, { useEffect, useState } from 'react';
import { TextField } from '@mui/material';
import dayjs from 'dayjs'; // Assuming you're using dayjs for date manipulation
import { LocalizationProvider, DatePicker } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';

const CalendarComponent = () => {
    const [monday, setMonday] = useState('');
    const [sunday, setSunday] = useState('');
    const [selectedDate, setSelectedDate] = useState(dayjs()); // Default to today's date
    const [showCalendar, setShowCalendar] = useState(false);

    useEffect(() => {
        // Calculate the week range when the selectedDate changes
        calculateWeekRange(selectedDate);
    }, [selectedDate]);

    const calculateWeekRange = (date) => {
        if (!date) return;

        const dayOfWeek = date.day(); // dayjs .day() returns 0 for Sunday, 1 for Monday, ..., 6 for Saturday
        const diffToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek; // If it's Sunday (0), go back 6 days to get to Monday
        const startOfWeek = date.add(diffToMonday, 'day');
        setMonday(startOfWeek.format('ddd MMM DD YYYY'));

        const endOfWeek = startOfWeek.add(6, 'day');
        setSunday(endOfWeek.format('ddd MMM DD YYYY'));
    };

    const handleDateChange = (newDate) => {
        setSelectedDate(newDate); // Update selected date
        setShowCalendar(false); // Hide the calendar
    };

    return (
        <LocalizationProvider dateAdapter={AdapterDayjs}>
            <DatePicker
                value={selectedDate}
                onChange={handleDateChange} // Update the selected date
                renderInput={(params) => <TextField {...params} style={{ display: 'none' }} />} // Hide the default input
            />
        </LocalizationProvider>
    );
};

export default CalendarComponent;
