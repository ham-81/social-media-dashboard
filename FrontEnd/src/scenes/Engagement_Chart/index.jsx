import { Box } from "@mui/material";
import Header from "../../components/Header";
import LineChart from "../../components/LineChart";
import EngagementTimelineChart from "../../components/EngagementChart";

const Line = () => {
  return (
    <Box m="20px">
      <Header title="Engagement Chart" subtitle="Simple Line Chart" />
      <Box height="75vh">
        <EngagementTimelineChart />
      </Box>
    </Box>
  );
};

export default Line;
