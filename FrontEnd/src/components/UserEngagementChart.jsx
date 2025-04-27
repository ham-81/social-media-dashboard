import { ResponsiveLine } from "@nivo/line";
import { useTheme } from "@mui/material";
import { tokens } from "../theme";
import { useEffect, useState } from "react";
import axios from "axios";

const EngagementTimelineChart = ({ isDashboard = false, setTotalEngagement, userId }) => {
  const [data, setData] = useState([]);
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  useEffect(() => {
    const url = userId 
      ? `http://localhost:5001/engagement/timeline/${userId}` // Fetch user-specific data
      : "http://localhost:5001/engagement/timeline"; // Default to all posts

    axios.get(url)
      .then((res) => {
        const timeline = res.data.timeline;
        const total = res.data.total_engagement;
        const chartData = [
          {
            id: "Engagement",
            color: "hsl(205, 70%, 50%)",
            data: timeline.map(item => ({
              x: item.date,
              y: item.engagement
            }))
          }
        ];
        setData(chartData);
        setTotalEngagement?.(total); // Set only if function provided
      })
      .catch((err) => {
        console.error("Failed to fetch engagement data", err);
      });
  }, [setTotalEngagement, userId]);

  return (
    <ResponsiveLine
      data={data}
      margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
      xScale={{ type: "point" }}
      yScale={{
        type: "linear",
        min: "auto",
        max: "auto",
        stacked: true,
        reverse: false,
      }}
      axisTop={null}
      axisRight={null}
      axisBottom={{
        orient: "bottom",
        tickSize: 5,
        tickPadding: 5,
        tickRotation: 0,
        legend: "Date",
        legendOffset: 36,
        legendPosition: "middle",
      }}
      axisLeft={{
        orient: "left",
        tickSize: 5,
        tickPadding: 5,
        tickRotation: 0,
        legend: "Engagement",
        legendOffset: -40,
        legendPosition: "middle",
      }}
      colors={{ scheme: "nivo" }}
      pointSize={10}
      pointColor={{ theme: "background" }}
      pointBorderWidth={2}
      pointBorderColor={{ from: "serieColor" }}
      pointLabelYOffset={-12}
      useMesh={true}
    />
  );
};

export default EngagementTimelineChart;
