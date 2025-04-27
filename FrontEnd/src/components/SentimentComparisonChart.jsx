import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { ResponsiveBar } from '@nivo/bar';

const SentimentComparisonChart = () => {
  const [chartData, setChartData] = useState([]);
  const [fontColor, setFontColor] = useState('#222');

  useEffect(() => {
    const updateTheme = () => {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setFontColor(isDark ? '#fff' : '#222');
    };

    updateTheme(); // Initial check
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', updateTheme);

    return () => {
      mediaQuery.removeEventListener('change', updateTheme);
    };
  }, []);

  useEffect(() => {
    axios.get("http://localhost:5001/top5/sentiment/posts")
      .then(res => {
        const formatted = res.data.map((post, idx) => ({
          post: `Post ${idx + 1}`,
          positive: post.sentiments.positive,
          neutral: post.sentiments.neutral,
          negative: post.sentiments.negative
        }));
        setChartData(formatted);
      })
      .catch(err => console.error("Sentiment fetch error:", err));
  }, []);

  return (
    <div style={{ height: '400px', width: '100%', maxWidth: '100%' }}>
      <ResponsiveBar
        data={chartData}
        keys={['positive', 'neutral', 'negative']}
        indexBy="post"
        margin={{ top: 50, right: 120, bottom: 60, left: 60 }}
        padding={0.3}
        groupMode="grouped"
        colors={{ scheme: 'set2' }}
        borderColor={{ from: 'color', modifiers: [['darker', 1.6]] }}
        axisBottom={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: 'Top 5 Posts',
          legendPosition: 'middle',
          legendOffset: 40,
        }}
        axisLeft={{
          tickSize: 5,
          tickPadding: 5,
          legend: 'Sentiment Score',
          legendPosition: 'middle',
          legendOffset: -50,
        }}
        labelSkipWidth={12}
        labelSkipHeight={12}
        labelTextColor={{ from: 'color', modifiers: [['darker', 1.6]] }}
        theme={{
          axis: {
            ticks: {
              text: {
                fill: fontColor,
                fontSize: 14,
                fontWeight: 600,
              },
            },
            legend: {
              text: {
                fill: fontColor,
                fontSize: 16,
                fontWeight: 700,
              },
            },
          },
          legends: {
            text: {
              fill: fontColor,
              fontSize: 14,
              fontWeight: 600,
            },
          },
          labels: {
            text: {
              fill: fontColor,
              fontSize: 13,
              fontWeight: 500,
            },
          },
        }}
        legends={[
          {
            dataFrom: 'keys',
            anchor: 'bottom-right',
            direction: 'column',
            justify: false,
            translateX: 120,
            translateY: 0,
            itemsSpacing: 2,
            itemWidth: 100,
            itemHeight: 20,
            itemDirection: 'left-to-right',
            symbolSize: 20,
            effects: [
              {
                on: 'hover',
                style: {
                  itemTextColor: '#000',
                },
              },
            ],
          },
        ]}
      />
    </div>
  );
};

export default SentimentComparisonChart;
