export const formatDate = (dateString) => {
    // Parse the date from the "DD-MM-YYYY" format
    const [day, month, year] = dateString.split('-');
    const date = new Date(`${year}-${month}-${day}`);

    // Define an array of month names
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    // Define an array of weekday names
    const weekdayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    // Get the weekday name (e.g., "Mon")
    const weekday = weekdayNames[date.getDay()];

    // Format the date as "Mon. 13 Jan. 2025"
    return `${weekday}. ${parseInt(day)} ${monthNames[parseInt(month) - 1]}. ${year}`;
};
