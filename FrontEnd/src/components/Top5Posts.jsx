import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid, ResponsiveContainer,
} from 'recharts';

  
const Top5Posts = () => {
  const [chartData, setChartData] = useState([]);
  const [error, setError] = useState("");
  useEffect(() => {
    axios.get('http://localhost:5001/top5/read')
      .then((res) => {
        console.log("Data received:", res.data);  // DEBUG POINT

        const formatted = res.data.map((item) => ({
          name: item.content.slice(0, 20) + "...",  // Short label
          likes: parseInt(item.likes),
          shares: parseInt(item.shares),
        }));

        console.log("Formatted chart data:", formatted);  // DEBUG POINT

        setChartData(formatted);
      })
      .catch((err) => {
        console.error("Error fetching data:", err);
        setError("Failed to fetch data from backend.");
      });
  }, []);

  return (
    <div style={{ width: '90%', margin: 'auto', marginTop: '50px' }}>
      

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {chartData.length === 0 ? (
        <p>Loading or No Data to Display</p>
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="likes" fill="#8884d8" />
            <Bar dataKey="shares" fill="#82ca9d" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default Top5Posts;
