import React, { useEffect, useState } from 'react';
import { useTheme } from '@mui/material/styles';

const FoodGroupsPyramidChart = ({ analytics }) => {
    const [ApexChart, setApexChart] = useState();
    const theme = useTheme();

    useEffect(() => {
        import('react-apexcharts').then((d) => {
            setApexChart(() => d.default.default);
        });
    }, []);

    if (!analytics) return null;

    // Transform and sort data by weight descending to create pyramid
    const sortedData = Object.entries(analytics)
        .map(([key, value]) => ({ name: key, value: Math.round(value[1]) }))
        .filter((item) => item.value > 0) // remove 0-value items like Alcohol, Other
        .sort((a, b) => b.value - a.value); // sort descending

    const categories = sortedData.map((item) => item.name);
    const values = sortedData.map((item) => item.value);

    const colors = [
        '#F44F5E',
        '#E55A89',
        '#D863B1',
        '#CA6CD8',
        '#B57BED',
        '#8D95EB',
        '#62ACEA',
        '#4BC3E6',
        '#2DD6C1',
        '#1DDFA3',
        '#27E87A',
        '#4AF55D',
        '#A2F94A',
        '#EAF94A'
    ];

    const options = {
        chart: {
            type: 'bar',
            height: 500
            // dropShadow: {
            //     enabled: true
            // }
        },
        plotOptions: {
            bar: {
                borderRadius: 4,
                borderRadiusApplication: 'end',
                horizontal: true
            }
        },
        dataLabels: {
            enabled: false
        },
        // colors: colors,
        // dataLabels: {
        //     enabled: true,
        //     formatter: function (val, opt) {
        //         return `${categories[opt.dataPointIndex]}: ${val}g`;
        //     },
        //     dropShadow: {
        //         enabled: true
        //     },
        //     style: {
        //         fontSize: '13px'
        //     }
        // },
        // title: {
        //     text: 'Food Groups Distribution',
        //     align: 'middle',
        //     style: {
        //         fontSize: '18px'
        //     }
        // },
        xaxis: {
            categories: categories,
            title: {
                text: 'Gramms'
            }
        }
    };

    const series = [
        {
            name: 'Gramms',
            data: values,
            color: theme.palette.success[400]
        }
    ];

    return !ApexChart ? null : <ApexChart options={options} series={series} type="bar" height={options.chart.height} />;
};

export default FoodGroupsPyramidChart;
