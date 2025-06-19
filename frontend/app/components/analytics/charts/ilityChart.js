import React, { useEffect, useState } from 'react';

const IlityChart = () => {
    const [ApexChart, setApexChart] = useState();

    useEffect(() => {
        import('react-apexcharts').then((d) => {
            setApexChart(() => d.default.default);
        });
    });

    const series = [90, 75, 80];

    const options = {
        chart: {
            height: 390,
            type: 'radialBar'
        },
        plotOptions: {
            radialBar: {
                offsetY: 0,
                startAngle: 0,
                endAngle: 270,
                hollow: {
                    margin: 5,
                    size: '30%',
                    background: 'transparent',
                    image: undefined
                },
                dataLabels: {
                    name: {
                        show: true
                    },
                    value: {
                        show: true
                    }
                    // total: {
                    //     show: true,
                    //     label: 'Total',
                    //     formatter: function (w) {
                    //         return w.globals.series.reduce((a, b) => a + b, 0);
                    //     }
                    // }
                }
            }
        },
        colors: ['#1ab7ea', '#0084ff', '#39539E'],
        labels: ['Sustainability', 'Affordability', 'Accessibility'],
        legend: {
            show: true,
            floating: true,
            fontSize: '16px',
            position: 'left',
            // offsetX: -8,
            // offsetY: 35,
            labels: {
                useSeriesColors: true
            },
            formatter: function (seriesName, opts) {
                return `${seriesName}: ${opts.w.globals.series[opts.seriesIndex]}%`;
            }
            // itemMargin: {
            //     horizontal: 0,
            //     vertical: 8
            // }
        },
        responsive: [
            {
                breakpoint: 480,
                options: {
                    legend: {
                        show: false
                    }
                }
            }
        ]
    };

    return !ApexChart ? <></> : <ApexChart options={options} series={series} type="radialBar" />;
};

export default IlityChart;

// const series = [
//     {
//         name: 'Sustainability',
//         data: [80, 75, 85, 80, 70, 75, 80]
//     },
//     {
//         name: 'Affordability',
//         data: [70, 85, 90, 95, 75, 75, 88]
//     },
//     {
//         name: 'Accessibility',
//         data: [70, 70, 85, 75, 90, 95, 85]
//     }
// ];

// const options = {
//     chart: {
//         type: 'bar',
//         height: 430
//     },
//     plotOptions: {
//         bar: {
//             horizontal: true,
//             dataLabels: {
//                 position: 'top'
//             }
//         }
//     },
//     dataLabels: {
//         enabled: true,
//         offsetX: -6,
//         style: {
//             fontSize: '12px',
//             colors: ['#fff']
//         },
//         formatter: function (val) {
//             return `${val}%`;
//         }
//     },
//     stroke: {
//         show: true,
//         width: 1,
//         colors: ['#fff']
//     },
//     tooltip: {
//         shared: true,
//         intersect: false,
//         y: {
//             formatter: function (val) {
//                 return val + ' %';
//             }
//         }
//     },
//     xaxis: {
//         categories: ['Mon.', 'Tue.', 'Wed.', 'Thu.', 'Fri.', 'Sat.', 'Sun.']
//     }
// };
