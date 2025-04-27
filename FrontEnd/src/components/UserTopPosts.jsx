import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';

const UserTopPosts = ({ userId }) => {
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    axios.get(`http://localhost:5001/top5/posts/${userId}`)
      .then((res) => {
        const formatted = res.data.map(item => ({
          name: item.content.slice(0, 20) + "...",
          engagement: item.engagement
        }));
        setChartData(formatted);
      });
  }, [userId]);

  return (
    <BarChart width={600} height={300} data={chartData}>
      <XAxis dataKey="name" />
      <YAxis />
      <Tooltip />
      <Bar dataKey="engagement" fill="#8884d8" />
    </BarChart>
  );
};
export default UserTopPosts;