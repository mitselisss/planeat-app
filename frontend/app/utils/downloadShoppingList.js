import { jsPDF } from 'jspdf';

export const downloadShoppingList = (ingredients) => {
    const doc = new jsPDF();
    const pageHeight = doc.internal.pageSize.height;
    let y = 10;
    const lineHeight = 8;

    const today = new Date();
    const formattedDate = `${String(today.getDate()).padStart(2, '0')}/${String(today.getMonth() + 1).padStart(2, '0')}/${String(
        today.getFullYear()
    ).slice(-2)}`;

    doc.setFont('Blinker', 'bold');
    doc.text(`Shopping List (${formattedDate})`, 10, y);
    y += 10;

    Object.entries(ingredients).forEach(([categoryKey, category]) => {
        if (y + lineHeight > pageHeight) {
            doc.addPage();
            y = 10;
        }

        doc.setFontSize(10);
        doc.setFont('Blinker', 'normal');
        doc.text(`${categoryKey}`, 10, y);
        y += lineHeight;

        doc.setFontSize(8);
        doc.setFont('Blinker', 'italic');

        Object.entries(category).forEach(([ingredientKey, ingredient]) => {
            if (y + lineHeight > pageHeight) {
                doc.addPage();
                y = 10;
            }

            doc.text(`${ingredient?.name}: ${ingredient?.quantity}`, 15, y);
            y += lineHeight;
        });

        y += 5;
    });

    doc.save(`Shopping List (${formattedDate})`);
};
