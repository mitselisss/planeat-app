import React, { useEffect, useState } from 'react';
import { useTheme, styled } from '@mui/material/styles';

const LevelChart = ({ levels, achievements }) => {
    const [ApexChart, setApexChart] = useState();
    const theme = useTheme();

    useEffect(() => {
        import('react-apexcharts').then((d) => {
            setApexChart(() => d.default.default);
        });
    }, []);

    const [state, setState] = React.useState({
        series: [
            Math.round((1 - (levels[achievements.level].points - achievements.points) / levels[achievements.level].points) * 100) <= 100
                ? Math.round((1 - (levels[achievements.level].points - achievements.points) / levels[achievements.level].points) * 100)
                : 100,
            Math.round((1 - (levels[achievements.level].badges - achievements.badges.length) / levels[achievements.level].badges) * 100) <=
            100
                ? Math.round(
                      (1 - (levels[achievements.level].badges - achievements.badges.length) / levels[achievements.level].badges) * 100
                  )
                : 100
        ],
        options: {
            chart: {
                height: 350,
                type: 'radialBar'
            },
            plotOptions: {
                radialBar: {
                    hollow: {
                        size: '70%'
                    },
                    dataLabels: {
                        name: {
                            show: true
                        },
                        value: {
                            show: true,
                            fontSize: '16px',
                            color: theme.palette.success.dark
                        },
                        total: {
                            show: true,
                            label: `Level ${achievements.level + 1}`,
                            formatter: function (w) {
                                // By default this function returns the average of all series. The below is just an example to show the use of custom formatter function
                                return '';
                            }
                        }
                    }
                }
            },
            labels: ['Points', 'Badges'],
            colors: [theme.palette.success.dark, theme.palette.success.main] //  change this to set the radial bar color
        }
    });

    return !ApexChart ? <></> : <ApexChart options={state.options} series={state.series} type="radialBar" height={350} />;
};

export default LevelChart;
