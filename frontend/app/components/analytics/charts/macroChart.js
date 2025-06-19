import React, { useEffect, useState } from 'react';

const MacroChart = ({ analytics }) => {
    const [ApexChart, setApexChart] = useState();

    useEffect(() => {
        import('react-apexcharts').then((d) => {
            setApexChart(() => d.default.default);
        });
    }, [analytics]);

    const options = {
        chart: {
            type: 'bar',
            height: 350
        },
        plotOptions: {
            bar: {
                horizontal: false,
                columnWidth: '55%',
                borderRadius: 5,
                borderRadiusApplication: 'end'
            }
        },
        dataLabels: {
            enabled: false
        },
        stroke: {
            show: true,
            width: 2,
            colors: ['transparent']
        },
        // title: {
        //     text: 'Macronutrients' // Title of the chart
        // },
        xaxis: {
            categories: ['Mon.', 'Tue.', 'Wed.', 'Thu.', 'Fri.', 'Sat.', 'Sun.']
        },
        yaxis: {
            title: {
                text: 'Gramms'
            }
        },
        fill: {
            opacity: 1
        },
        tooltip: {
            y: {
                formatter: function (val) {
                    return val + ' g';
                }
            }
        }
    };

    const series = [
        {
            name: 'Carbohydrates',
            data: [
                Math.round(analytics?.day_1.macro.total_carbs),
                Math.round(analytics?.day_2.macro.total_carbs),
                Math.round(analytics?.day_3.macro.total_carbs),
                Math.round(analytics?.day_4.macro.total_carbs),
                Math.round(analytics?.day_5.macro.total_carbs),
                Math.round(analytics?.day_6.macro.total_carbs),
                Math.round(analytics?.day_7.macro.total_carbs)
            ]
        },
        {
            name: 'Protein',
            data: [
                Math.round(analytics?.day_1.macro.total_protein),
                Math.round(analytics?.day_2.macro.total_protein),
                Math.round(analytics?.day_3.macro.total_protein),
                Math.round(analytics?.day_4.macro.total_protein),
                Math.round(analytics?.day_5.macro.total_protein),
                Math.round(analytics?.day_6.macro.total_protein),
                Math.round(analytics?.day_7.macro.total_protein)
            ]
        },
        {
            name: 'Fat',
            data: [
                Math.round(analytics?.day_1.macro.total_fat),
                Math.round(analytics?.day_2.macro.total_fat),
                Math.round(analytics?.day_3.macro.total_fat),
                Math.round(analytics?.day_4.macro.total_fat),
                Math.round(analytics?.day_5.macro.total_fat),
                Math.round(analytics?.day_6.macro.total_fat),
                Math.round(analytics?.day_7.macro.total_fat)
            ]
        }
    ];

    return !ApexChart ? <></> : <ApexChart options={options} series={series} type="bar" />;
};

export default MacroChart;
