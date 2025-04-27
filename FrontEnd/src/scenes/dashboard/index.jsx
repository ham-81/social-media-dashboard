import { Box, Button, IconButton, Typography, useTheme } from "@mui/material";
import { tokens } from "../../theme";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import Header from "../../components/Header";
import EngagementTimelineChart from "../../components/EngagementChart";
import Top5Posts from "../../components/Top5Posts";
import axios from "axios";
import { useEffect, useState } from "react";
import SentimentComparisonChart from "../../components/SentimentComparisonChart";
import { Link } from 'react-router-dom';


const Dashboard = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [topUsers, setTopUsers] = useState([]);
  const [recentPosts, setRecentPosts] = useState([]);
  const [totalEngagement, setTotalEngagement] = useState(0);
  

useEffect(() => {
  axios.get("http://localhost:5001/top5/users")
    .then((res) => setTopUsers(res.data))
    .catch((err) => console.error("Failed to load top users", err));
  axios.get("http://localhost:5001/recent/posts")
    .then(res => setRecentPosts(res.data))
    .catch(err => console.error("Failed to load recent posts", err));
}, []);

  return (
    <Box m="20px">
      {/* HEADER */}
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Header title="DASHBOARD" subtitle="Welcome to your dashboard" />

        <Box>
          <Button
            sx={{
              backgroundColor: colors.blueAccent[700],
              color: colors.grey[100],
              fontSize: "14px",
              fontWeight: "bold",
              padding: "10px 20px",
            }}
          >
            <DownloadOutlinedIcon sx={{ mr: "10px" }} />
            Download Reports
          </Button>
        </Box>
      </Box>

      {/* GRID & CHARTS */}
      <Box
        display="grid"
        gridTemplateColumns="repeat(12, 1fr)"
        gridAutoRows="140px"
        gap="20px"
      >
        {/* ROW 1 */}
        {topUsers.map((user, index) => (
  <Box
    key={user.user_id}
    gridColumn="span 3"
    backgroundColor={colors.primary[400]}
    display="flex"
    flexDirection="column"
    alignItems="center"
    justifyContent="center"
    p={2}
    sx={{
      borderRadius: "12px",
      transition: "all 0.3s ease",
      cursor: "pointer",
      "&:hover .details": {
        maxHeight: "100px",
        opacity: 1,
      },
    }}
  >
    <Typography variant="h5" color={colors.grey[100]}>
      {user.name}
    </Typography>
    <Typography variant="subtitle2" color={colors.greenAccent[500]}>
      Total Engagement: {user.total_engagement}
    </Typography>
    <Box
      className="details"
      sx={{
        mt: 1,
        maxHeight: 0,
        overflow: "hidden",
        opacity: 0,
        transition: "all 0.3s ease",
        width: "100%",
      }}
    >
      <Typography variant="body2" color={colors.grey[200]}>
        👍 Likes: {user.likes}
      </Typography>
      <Typography variant="body2" color={colors.grey[200]}>
        🔁 Shares: {user.shares}
      </Typography>
      <Typography variant="body2" color={colors.grey[200]}>
        💬 Comments: {user.comments}
      </Typography>
    </Box>
  </Box>
))}
  <Box></Box>
        {/* ROW 2 */}
        <Box
  gridColumn="span 8"
  gridRow="span 2"
  backgroundColor={colors.primary[400]}
>
  <Box
    mt="25px"
    p="0 30px"
    display="flex"
    justifyContent="space-between"
    alignItems="center"
  >
    <Box>
      <Typography
        variant="h5"
        fontWeight="600"
        color={colors.grey[100]}
      >
        Engagement (3 Months)
      </Typography>
      <Typography
        variant="h3"
        fontWeight="bold"
        color={colors.greenAccent[500]}
      >
        {totalEngagement.toLocaleString()}
      </Typography>
    </Box>
    <Box>
      <IconButton>
        <DownloadOutlinedIcon
          sx={{ fontSize: "26px", color: colors.greenAccent[500] }}
        />
      </IconButton>
    </Box>
  </Box>

  {/* Adjust height and margin so chart doesn't clip */}
  <Box height="250px" m="-40px 0 0 0">
    <EngagementTimelineChart isDashboard={true} setTotalEngagement={setTotalEngagement} />
  </Box>
</Box>

        <Box></Box>
        <Box
          gridColumn="span 4"
          gridRow="span 2"
          backgroundColor={colors.primary[400]}
          overflow="auto"
        >
          
          <Box
  display="flex"
  justifyContent="space-between"
  alignItems="center"
  borderBottom={`4px solid ${colors.primary[500]}`}
  colors={colors.grey[100]}
  p="15px"
>
  <Typography color={colors.grey[100]} variant="h5" fontWeight="600">
    Recent Posts
  </Typography>
</Box>

{recentPosts.map((post, i) => (
  <Box
    key={`${post.post_id}-${i}`}
    display="flex"
    justifyContent="space-between"
    alignItems="center"
    borderBottom={`4px solid ${colors.primary[500]}`}
    p="15px"
  >
    <Box width="60%">
      <Typography
        color={colors.greenAccent[500]}
        variant="h5"
        fontWeight="600"
        noWrap
      >
        {post.username}
      </Typography>
      <Typography color={colors.grey[100]} noWrap>
        {post.content}
      </Typography>
    </Box>
    <Box color={colors.grey[100]}>{post.timestamp}</Box>
  </Box>
          ))}
        </Box>
        <Box
          gridColumn="span 4"
          gridRow="span 2"
          backgroundColor={colors.primary[400]}
        >
          <Typography
            variant="h5"
            fontWeight="600"
            sx={{ padding: "30px 30px 0 30px" }}
          >
            Top 5 Posts Engagement
          </Typography>
          <Box height="250px" mt="-20px">
            <Top5Posts isDashboard={true} />
          </Box>
        </Box>
          
        {/* ROW 3 */}
        <Box
  gridColumn="span 9"
  gridRow="span 3"
  backgroundColor={colors.primary[400]}
>
  <Typography variant="h6" color={colors.grey[100]} fontWeight="999" sx={{ p: '15px' }}>
    Continuation
  </Typography>

  {/* Navigation Button to Top Comments List (Now routing to /pie) */}
  <Box display="flex" justifyContent="center" alignItems="center" p="20px">
    <Link to="/pie" style={{ textDecoration: 'none' }}>
      <Button
        sx={{
          backgroundColor: colors.greenAccent[500],
          color: colors.grey[100],
          fontSize: "16px",
          fontWeight: "bold",
          padding: "10px 20px",
          "&:hover": {
            backgroundColor: colors.greenAccent[700],
          },
        }}
      >
        View Top Comments List
      </Button>
    </Link>
  </Box>
</Box>


        
        
      </Box>
    </Box>
  );
};

export default Dashboard;
