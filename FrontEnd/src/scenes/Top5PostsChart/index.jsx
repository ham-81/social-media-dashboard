import { Box } from "@mui/material";
import Header from "../../components/Header";
import Top5Posts from "../../components/Top5Posts";

const Bar = () => {
  return (
    <Box m="20px">
      <Header title="Top 5 Posts Engagement" subtitle="Simple Bar Graph" />
      <Box height="75vh">
        <Top5Posts />
      </Box>
    </Box>
  );
};

export default Bar;
