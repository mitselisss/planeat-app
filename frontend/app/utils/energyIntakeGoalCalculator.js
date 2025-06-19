export const energyIntakeGoalCalculator = (weight, target_weight) => {
    let goal = '';

    if (target_weight - weight > 0) {
        goal = 'increase';
    } else if (target_weight - weight < 0) {
        goal = 'decrease';
    } else {
        goal = 'same';
    }

    const slow_days = (Math.abs(weight - target_weight) * 7700) / 250;
    const slow_weeks = Math.round(slow_days / 7);

    const normal_days = (Math.abs(weight - target_weight) * 7700) / 500;
    const normal_weeks = Math.round(normal_days / 7);

    const fast_days = (Math.abs(weight - target_weight) * 7700) / 750;
    const fast_weeks = Math.round(fast_days / 7);

    return { goal, slow_weeks, normal_weeks, fast_weeks };
};
