import { Box } from "@mui/material";
import Header from "../../components/Header";
import TopCommentsList from "../../components/TopCommentList";

const Pie = () => {
  return (
    <Box m="20px">
      <Header title="Sentiment Comparison" subtitle="Bar Graph" />
      <Box height="75vh">
        <TopCommentsList />
      </Box>
    </Box>
  );
};

export default Pie;
