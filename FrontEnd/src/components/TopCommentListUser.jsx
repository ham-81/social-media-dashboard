import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Box, Card, CardContent, Typography, CardActions, Button } from '@mui/material';
import { useParams } from 'react-router-dom';

const TopCommentsList = () => {
  const { userId } = useParams();
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!userId) return;

    axios.get(`http://localhost:5001/top5/comments/user/${userId}`)
      .then(res => {
        console.log("User comments response:", res.data);
        setComments(res.data.comments || []);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching user comments:", err);
        setError(err.message);
        setLoading(false);
      });
  }, [userId]);

  if (loading) {
    return <div>Loading comments for user {userId}...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div style={{ padding: '20px', backgroundColor: '#2c3e50', minHeight: '100vh' }}>
      <Typography variant="h4" color="white" gutterBottom>
        Top Comments for User {userId}
      </Typography>
      
      {comments.length === 0 ? (
        <p style={{ color: 'white' }}>No comments found for this user's posts.</p>
      ) : (
        comments.map((comment, index) => (
          <Card key={index} sx={{ 
            marginBottom: 2, 
            boxShadow: 3, 
            '&:hover': { boxShadow: 6 }, 
            backgroundColor: '#34495e'
          }}>
            <CardContent>
              <Typography variant="h6" color="primary">
                <strong>Comment {index + 1}</strong>
              </Typography>
              <Typography variant="body1" color="textSecondary" paragraph>
                {comment.comment_text}
              </Typography>
              
              <Box sx={{ 
                backgroundColor: '#2c3e50',
                padding: '10px',
                borderRadius: '8px',
                marginBottom: '10px'
              }}>
                <Typography variant="subtitle2" color="text.primary">
                  On Post: {comment.post_content}
                </Typography>
                <CardActions>
                  <Button size="small" variant="contained" color="primary">
                    Posted at: {comment.timestamp}
                  </Button>
                </CardActions>
              </Box>
            </CardContent>
          </Card>
        ))
      )}
    </div>
  );
};

export default TopCommentsList;
