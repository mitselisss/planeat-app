export const energyIntakeCalculator = (sex, yob, height, weight, pal) => {
    const today = new Date();

    // convert year of bith to age
    const age = today.getFullYear() - yob;

    // calculate bmi
    const bmi = weight / ((height / 100) * 2);

    let bmr = 0;
    // calculate bmr
    if (sex === 'male') {
        if (age >= 0 && age <= 3) {
            bmr = 28.2 * weight + 8.59 * height - 371;
        } else if (age > 3 && age <= 10) {
            bmr = 15.1 * weight + 7.42 * height + 306;
        } else if (age > 10 && age <= 18) {
            bmr = 15.6 * weight + 2.66 * height + 299;
        } else if (age > 18 && age <= 30) {
            bmr = 14.4 * weight + 3.13 * height + 113;
        } else if (age > 30 && age <= 60) {
            bmr = 11.4 * weight + 5.41 * height - 137;
        } else if (age > 60) {
            bmr = 11.4 * weight + 5.41 * height - 256;
        }
    } else if (sex === 'female') {
        if (age >= 0 && age <= 3) {
            bmr = 30.4 * weight + 7.03 * height - 287;
        } else if (age > 3 && age <= 10) {
            bmr = 15.9 * weight + 2.1 * height + 349;
        } else if (age > 10 && age <= 18) {
            bmr = 9.4 * weight + 2.49 * height + 462;
        } else if (age > 18 && age <= 30) {
            bmr = 10.4 * weight + 2.57 * height + 118;
        } else if (age > 30 && age <= 60) {
            bmr = 8.18 * weight + 5.02 * height - 11.6;
        } else if (age > 60) {
            bmr = 8.52 * weight + 4.21 * height + 10.7;
        }
    }

    let energy_intake = 0;
    //calculate energy intake
    if (pal === 'sedentary') {
        energy_intake = bmr * 1.4;
    } else if (pal === 'moderately_active') {
        energy_intake = bmr * 1.6;
    } else if (pal === 'active') {
        energy_intake = bmr * 1.8;
    } else if (pal === 'very_active') {
        energy_intake = bmr * 2.0;
    }

    return {
        age: age,
        bmi: bmi.toFixed(2),
        bmr: bmr.toFixed(2),
        energy_intake: energy_intake.toFixed(2)
    };
};
