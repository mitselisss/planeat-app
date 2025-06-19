import React, { useEffect, useState } from 'react';
import { useTheme } from '@mui/material/styles';

const FoodGroupsChart = ({ analytics }) => {
    const [ApexChart, setApexChart] = useState();
    const theme = useTheme();

    useEffect(() => {
        console.log('Analytics', analytics);
        import('react-apexcharts').then((d) => {
            setApexChart(() => d.default.default);
        });
    }, [analytics]);

    const series = [
        {
            name: 'Suggested Consumption',
            data: [
                {
                    x: 'Meat',
                    y: Math.round(analytics?.Meat[1]),
                    goals: [
                        {
                            name: 'Target Consumption',
                            value: Math.round(analytics?.Meat[2]),
                            strokeHeight: Math.round(analytics?.Meat[1]) > Math.round(analytics?.Meat[2]) ? 13 : 5,
                            strokeWidth: Math.round(analytics?.Meat[1]) > Math.round(analytics?.Meat[2]) ? 0 : 20,
                            strokeLineCap: Math.round(analytics?.Meat[1]) > Math.round(analytics?.Meat[2]) ? 'round' : '',
                            strokeColor: theme.palette.secondary.dark
                        }
                    ]
                },
                {
                    x: 'Plant Protein (Legumes)',
                    y: Math.round(analytics?.Plant_protein[1]),
                    goals: [
                        {
                            name: 'Target Consumption',
                            value: Math.round(analytics?.Plant_protein[2]),
                            strokeHeight: Math.round(analytics?.Plant_protein[1]) > Math.round(analytics?.Plant_protein[2]) ? 13 : 5,
                            strokeWidth: Math.round(analytics?.Plant_protein[1]) > Math.round(analytics?.Plant_protein[2]) ? 0 : 20,
                            strokeLineCap: Math.round(analytics?.Plant_protein[1]) > Math.round(analytics?.Plant_protein[2]) ? 'round' : '',
                            strokeColor: theme.palette.secondary.dark
                        }
                    ]
                },
                {
                    x: 'Vegetables',
                    y: Math.round(analytics?.Vegetables[1]),
                    goals: [
                        {
                            name: 'Target Consumption',
                            value: Math.round(analytics?.Vegetables[2]),
                            strokeHeight: Math.round(analytics?.Vegetables[1]) > Math.round(analytics?.Vegetables[2]) ? 13 : 5,
                            strokeWidth: Math.round(analytics?.Vegetables[1]) > Math.round(analytics?.Vegetables[2]) ? 0 : 20,
                            strokeLineCap: Math.round(analytics?.Vegetables[1]) > Math.round(analytics?.Vegetables[2]) ? 'round' : '',
                            strokeColor: theme.palette.secondary.dark
                        }
                    ]
                },
                {
                    x: 'Fruit',
                    y: Math.round(analytics?.Fruit[1]),
                    goals: [
                        {
                            name: 'Target Consumption',
                            value: Math.round(analytics?.Fruit[2]),
                            strokeHeight: Math.round(analytics?.Fruit[1]) > Math.round(analytics?.Fruit[2]) ? 13 : 5,
                            strokeWidth: Math.round(analytics?.Fruit[1]) > Math.round(analytics?.Fruit[2]) ? 0 : 20,
                            strokeLineCap: Math.round(analytics?.Fruit[1]) > Math.round(analytics?.Fruit[2]) ? 'round' : '',
                            strokeColor: theme.palette.secondary.dark
                        }
                    ]
                },
                {
                    x: 'Dairy/Dairy Alternatives',
                    y: Math.round(analytics?.Dairy[1]),
                    goals: [
                        {
                            name: 'Target Consumption',
                            value: Math.round(analytics?.Dairy[2]),
                            strokeHeight: Math.round(analytics?.Dairy[1]) > Math.round(analytics?.Dairy[2]) ? 13 : 5,
                            strokeWidth: Math.round(analytics?.Dairy[1]) > Math.round(analytics?.Dairy[2]) ? 0 : 20,
                            strokeLineCap: Math.round(analytics?.Dairy[1]) > Math.round(analytics?.Dairy[2]) ? 'round' : '',
                            strokeColor: theme.palette.secondary.dark
                        }
                    ]
                },
                {
                    x: 'Nuts and Seeds',
                    y: Math.round(analytics?.Nuts_and_seeds[1]),
                    goals: [
                        {
                            name: 'Target Consumption',
                            value: Math.round(analytics?.Nuts_and_seeds[2]),
                            strokeHeight: Math.round(analytics?.Nuts_and_seeds[1]) > Math.round(analytics?.Nuts_and_seeds[2]) ? 13 : 5,
                            strokeWidth: Math.round(analytics?.Nuts_and_seeds[1]) > Math.round(analytics?.Nuts_and_seeds[2]) ? 0 : 20,
                            strokeLineCap:
                                Math.round(analytics?.Nuts_and_seeds[1]) > Math.round(analytics?.Nuts_and_seeds[2]) ? 'round' : '',
                            strokeColor: theme.palette.secondary.dark
                        }
                    ]
                },
                {
                    x: 'Fish',
                    y: Math.round(analytics?.Fish[1]),
                    goals: [
                        {
                            name: 'Target Consumption',
                            value: Math.round(analytics?.Fish[2]),
                            strokeHeight: Math.round(analytics?.Fish[1]) > Math.round(analytics?.Fish[2]) ? 13 : 5,
                            strokeWidth: Math.round(analytics?.Fish[1]) > Math.round(analytics?.Fish[2]) ? 0 : 20,
                            strokeLineCap: Math.round(analytics?.Fish[1]) > Math.round(analytics?.Fish[2]) ? 'round' : '',
                            strokeColor: theme.palette.secondary.dark
                        }
                    ]
                }
            ]
        }
    ];
    const options = {
        chart: {
            height: 350,
            type: 'bar'
        },
        plotOptions: {
            bar: {
                columnWidth: '60%'
            }
        },
        colors: [theme.palette.primary[200]],
        dataLabels: {
            enabled: false
        },
        legend: {
            show: true,
            showForSingleSeries: true,
            customLegendItems: ['Suggested Consumption', 'Target Consumption'],
            markers: {
                fillColors: [theme.palette.primary[200], theme.palette.secondary.dark]
            }
        },
        yaxis: {
            title: {
                text: 'Gramms' // This adds 'Grams' as the Y-axis label
            }
        },
        tooltip: {
            y: {
                formatter: function (val) {
                    return val + ' g';
                }
            }
        }
    };

    return !ApexChart ? <></> : <ApexChart options={options} series={series} type="bar" />;
};

export default FoodGroupsChart;

// const options = {
//     chart: {
//         width: 380,
//         type: 'pie' // Pie chart type
//     },
//     tooltip: {
//         y: {
//             formatter: function (val) {
//                 return val + ' g';
//             }
//         }
//     },
//     labels: ['Meat', 'Plant Protein (Legumes)', 'Vegetables', 'Fruit', 'Dairy/Dairy Alternatives', 'Nuts and Seeds', 'Fish'],
//     series: [
//         Math.round(analytics?.['Meat'][1]),
//         Math.round(analytics?.['Plant Protein (Legumes)'][1]),
//         Math.round(analytics?.['Vegetables'][1]),
//         Math.round(analytics?.['Fruit'][1]),
//         Math.round(analytics?.['Dairy/Dairy Alternatives'][1]),
//         Math.round(analytics?.['Nuts and Seeds'][1]),
//         Math.round(analytics?.['Fish'][1])
//     ], // Pie chart data
//     colors: [
//         'rgba(255, 99, 132, 0.6)',
//         'rgba(255, 159, 64, 0.6)',
//         'rgba(255, 205, 86, 0.6)',
//         'rgba(75, 192, 192, 0.6)',
//         'rgba(54, 162, 235, 0.6)',
//         'rgba(153, 102, 255, 0.6)',
//         'rgba(201, 203, 207, 0.6)'
//     ],
//     responsive: [
//         {
//             breakpoint: 480,
//             options: {
//                 chart: {
//                     width: 200 // Smaller width for mobile view
//                 },
//                 legend: {
//                     position: 'bottom' // Position the legend at the bottom on smaller screens
//                 }
//             }
//         }
//     ]
// };
