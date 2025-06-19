export const checkWeek = (weekMonday) => {
    // Convert the input weekMonday to a Date object (ignoring time)
    const [day, month, year] = weekMonday.split('-').map(Number);
    const inputDate = new Date(year, month - 1, day);
    inputDate.setHours(0, 0, 0, 0); // Reset time to 00:00:00

    // Get today's date and find the Monday of this week
    const today = new Date();
    const currentMonday = new Date(today);
    currentMonday.setDate(today.getDate() - today.getDay() + 1); // Adjust to Monday
    currentMonday.setHours(0, 0, 0, 0); // Reset time to 00:00:00

    // Compare inputDate with currentMonday (ignoring time)
    return inputDate < currentMonday;
};
