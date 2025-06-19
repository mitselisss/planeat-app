import { jsPDF } from 'jspdf';

export const downloadWeeklyPlan = (NP, week) => {
    const doc = new jsPDF();
    const pageHeight = doc.internal.pageSize.height;
    let y = 10;
    const lineHeight = 8;

    doc.setFont('Blinker', 'bold');
    doc.text(`Weekly Meal Plan (${week})`, 10, y);
    y += 10;

    Object.entries(NP).forEach(([dayKey, meals]) => {
        if (y + lineHeight > pageHeight) {
            doc.addPage();
            y = 10;
        }

        doc.setFontSize(14);
        doc.setFont('Blinker', 'normal');
        doc.text(`${dayKey}`, 10, y);
        y += lineHeight;

        doc.setFontSize(12);
        doc.setFont('Blinker', 'italic');

        Object.entries(meals).forEach(([mealKey, mealValue]) => {
            if (y + lineHeight > pageHeight) {
                doc.addPage();
                y = 10;
            }

            const mealName = mealValue?.meal_name || 'N/A';
            doc.text(`${mealValue.meal_type}: ${mealName}`, 15, y);
            y += lineHeight;
        });

        y += 5;
    });

    doc.save(`WeeklyPlan(${week}).pdf`);
};
