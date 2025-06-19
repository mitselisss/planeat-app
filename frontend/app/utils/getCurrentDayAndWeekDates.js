export const getCurrentDayAndWeekDates = () => {
    const today = new Date();

    // Get the current day of the week (0: Sunday, 1: Monday, ..., 6: Saturday)
    const currentDay = (today.getDay() + 6) % 7;
    // (today.getDay() + 6) % 7 remaps:
    // Sunday (0) -> 6, Monday (1) -> 0, Tuesday (2) -> 1, ..., Saturday (6) -> 5

    // Calculate the current week's Monday date
    const monday = new Date(today);
    monday.setDate(today.getDate() - currentDay); // Go back 'currentDay' days to get Monday

    // Calculate the current week's Sunday date
    const sunday = new Date(monday);
    sunday.setDate(monday.getDate() + 6); // Sunday is 6 days after Monday

    // Format dates (optional, but can be useful for UI)
    const formatDate = (date) => {
        const year = date.getFullYear();
        const month = `0${date.getMonth() + 1}`.slice(-2); // +1 to adjust for zero-indexed months
        const day = `0${date.getDate()}`.slice(-2);
        return `${year}-${month}-${day}`;
    };

    return {
        currday: currentDay, // Numeric value of the current day (0 to 6)
        currMondayDate: formatDate(monday), // Monday of this week in YYYY-MM-DD format
        currSundayDate: formatDate(sunday) // Sunday of this week in YYYY-MM-DD format
    };
};
