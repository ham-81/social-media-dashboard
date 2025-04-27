import { Box, Typography, useTheme, Card, CardContent } from "@mui/material";
import { tokens } from "../theme";
import Header from "../components/Header";
import EngagementTimelineChart from "../components/EngagementChart";
import UserTopPosts from "./UserTopPosts";
import { useEffect, useState } from "react";
import { useParams } from 'react-router-dom';
import TopCommentsList from "./TopCommentListUser";
import axios from 'axios';

const UserDashboard = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const { userId } = useParams();
  const [userData, setUserData] = useState({});
  const [recentPosts, setRecentPosts] = useState([]);
  const [totalEngagement, setTotalEngagement] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [userRes, postsRes] = await Promise.all([
          axios.get(`http://localhost:5001/user/${userId}`),
          axios.get(`http://localhost:5001/recent/posts/${userId}`)
        ]);
        
        setUserData(userRes.data || {});
        setRecentPosts(postsRes.data || []);
      } catch (error) {
        console.error("Data fetch failed:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [userId]);

  if (loading) {
    return <Box sx={{ p: 4, textAlign: 'center' }}>Loading dashboard...</Box>;
  }

  return (
    <Box m="20px">
      <Header 
        title="USER DASHBOARD" 
        subtitle={`Analytics for ${userData?.name || "User"}`} 
      />
      
      <Box display="grid" gridTemplateColumns="repeat(12, 1fr)" gap="20px">
        {/* Engagement Timeline */}
        <Box gridColumn="span 8" p={3} sx={{ bgcolor: colors.primary[400], borderRadius: 2 }}>
          <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
            Engagement Timeline
          </Typography>
          <Box height={400}>
            <EngagementTimelineChart 
              isDashboard={true} 
              setTotalEngagement={setTotalEngagement}
              userId={userId}
            />
          </Box>
        </Box>

        {/* User Stats */}
        <Box gridColumn="span 4" p={3} sx={{ bgcolor: colors.primary[400], borderRadius: 2 }}>
          <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
            User Statistics
          </Typography>
          <Box display="flex" flexDirection="column" gap={2}>
            <StatCard label="Total Engagement" value={totalEngagement.toLocaleString()} />
            <StatCard label="Posts Created" value={userData.post_count || 0} />
            <StatCard label="Avg Engagement/Post" value={userData.avg_engagement || 0} />
          </Box>
        </Box>

        {/* Top Posts */}
        <Box gridColumn="span 6" p={3} sx={{ bgcolor: colors.primary[400], borderRadius: 2 }}>
          <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
            Top Posts
          </Typography>
          <Box height={300}>
            <UserTopPosts userId={userId} />
          </Box>
        </Box>

        {/* Recent Activity */}
        <Box gridColumn="span 6" p={3} sx={{ bgcolor: colors.primary[400], borderRadius: 2 }}>
          <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
            Recent Activity
          </Typography>
          <Box height={300} sx={{ overflowY: 'auto' }}>
            {recentPosts.map((post, i) => (
              <Card key={i} sx={{ mb: 2, p: 2 }}>
                <Typography variant="h6">{post.content}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {post.timestamp}
                </Typography>
              </Card>
            ))}
          </Box>
        </Box>

        {/* Top Comments */}
        <Box gridColumn="span 12" p={3} sx={{ bgcolor: colors.primary[400], borderRadius: 2 }}>
          <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
            Top Comments
          </Typography>
          <TopCommentsList userId={userId} horizontal />
        </Box>
      </Box>
    </Box>
  );
};

const StatCard = ({ label, value }) => (
  <Card sx={{ p: 2, bgcolor: 'background.paper' }}>
    <Typography variant="h6" color="text.secondary">{label}</Typography>
    <Typography variant="h4" sx={{ fontWeight: 700 }}>{value}</Typography>
  </Card>
);

export default UserDashboard;
