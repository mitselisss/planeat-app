import React, { useEffect, useState } from 'react';
import { useTheme } from '@mui/material/styles';

const EnergyIntakeChart = ({ analytics }) => {
    const [ApexChart, setApexChart] = useState();
    const theme = useTheme();

    useEffect(() => {
        import('react-apexcharts').then((d) => {
            setApexChart(() => d.default.default);
        });
    }, [analytics]);

    const options = {
        chart: {
            height: 350,
            type: 'line' // You can set the primary chart type here
        },
        stroke: {
            width: [0, 4] // Different stroke widths for the column and line chart
        },
        // title: {
        //     text: 'Traffic Sources' // Title of the chart
        // },
        dataLabels: {
            enabled: true,
            enabledOnSeries: [1] // Enable data labels only for the line chart
        },
        labels: ['Mon.', 'Tue.', 'Wed.', 'Thu.', 'Fri.', 'Sat.', 'Sun.'],
        yaxis: {
            title: {
                text: 'Calories' // Title for the y-axis
            },
            min: 0,
            max: Math.round(analytics?.user_enegy_intake) + 100
        }
    };

    const series = [
        {
            name: 'Suggested Daily Plan Energy',
            type: 'column', // This is a column chart
            data: [
                Math.round(analytics?.day_1.macro.total_kcal),
                Math.round(analytics?.day_2.macro.total_kcal),
                Math.round(analytics?.day_3.macro.total_kcal),
                Math.round(analytics?.day_4.macro.total_kcal),
                Math.round(analytics?.day_5.macro.total_kcal),
                Math.round(analytics?.day_6.macro.total_kcal),
                Math.round(analytics?.day_7.macro.total_kcal)
            ],
            color: theme.palette.success.light
        },
        {
            name: 'User Daily Energy Requirements',
            type: 'line', // This is a line chart
            data: [
                Math.round(analytics?.user_enegy_intake),
                Math.round(analytics?.user_enegy_intake),
                Math.round(analytics?.user_enegy_intake),
                Math.round(analytics?.user_enegy_intake),
                Math.round(analytics?.user_enegy_intake),
                Math.round(analytics?.user_enegy_intake),
                Math.round(analytics?.user_enegy_intake)
            ],
            color: theme.palette.primary.dark
        }
    ];

    return !ApexChart ? <></> : <ApexChart options={options} series={series} type="line" />;
};

export default EnergyIntakeChart;
