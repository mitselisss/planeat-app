export const checkDay = (dayIndex) => {
    const todayIndex = (new Date().getDay() + 6) % 7;

    return dayIndex < todayIndex;
};
