import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Box, Typography, Card, CardContent, Stack } from '@mui/material';

const RecentPosts = ({ userId }) => {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    axios.get(`http://localhost:5001/recent/posts/${userId}`)
      .then(res => setPosts(res.data))
      .catch(err => console.error("Recent posts error:", err));
  }, [userId]);

  return (
    <Box mt={4}>
      <Typography variant="h5" gutterBottom>
        Recent Posts
      </Typography>
      
      {posts.length === 0 ? (
        <Typography>No recent posts available.</Typography>
      ) : (
        posts.map(post => (
          <Card key={post.post_id} sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="subtitle1">{post.content}</Typography>
              <Stack direction="row" justifyContent="space-between">
                <Typography variant="caption">{post.timestamp}</Typography>
                
              </Stack>
            </CardContent>
          </Card>
        ))
      )}
    </Box>
  );
};

export default RecentPosts;
