import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  CardHeader,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Chip
} from '@mui/material';
import { useParams } from 'react-router-dom';
import { format } from 'date-fns';

const TopCommentsList = () => {
  const { userId } = useParams();
  const [postsWithComments, setPostsWithComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    axios.get(`http://localhost:5001/top5/comments/sentiment`)
      .then(res => {
        // Flatten the nested comments structure
        const allComments = res.data.flatMap(post => 
          post.top_comments.map(comment => ({
            ...comment,
            post_content: post.post_content
          }))
        );
        
        setPostsWithComments(allComments);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching comments:", err);
        setError(err.message);
        setLoading(false);
      });
  }, [userId]);

  const getSentimentColor = (label) => {
    switch(label.toLowerCase()) {
      case 'positive': return 'success';
      case 'negative': return 'error';
      default: return 'info';
    }
  };

  if (loading) {
    return <Box p={3}>Loading comments...</Box>;
  }

  if (error) {
    return <Box p={3} color="error.main">{error}</Box>;
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Top Comments Analysis
      </Typography>

      <List sx={{ width: '100%' }}>
        {postsWithComments.map((comment, index) => (
          <Card key={comment.comment_id} sx={{ mb: 2, boxShadow: 3 }}>
            <CardHeader
              avatar={
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  {String.fromCharCode(65 + index)} {/* A, B, C, etc */}
                </Avatar>
              }
              title={
                <Box display="flex" alignItems="center" gap={1}>
                  <Chip 
                    label={comment.sentiment_label}
                    color={getSentimentColor(comment.sentiment_label)}
                    size="small"
                  />
                  <Typography variant="caption" color="text.secondary">
                    {format(new Date(comment.timestamp), 'MMM dd, yyyy HH:mm')}
                  </Typography>
                </Box>
              }
              subheader={
                <Typography variant="body2" color="text.secondary">
                  On Post: "{comment.post_content}"
                </Typography>
              }
            />
            <CardContent>
              <Typography variant="body1" paragraph>
                "{comment.text}"
              </Typography>
              
              <Box display="flex" gap={1} mt={1}>
                <Chip 
                  label={`Compound: ${comment.sentiment_score.compound.toFixed(2)}`}
                  variant="outlined"
                />
                <Chip 
                  label={`Positive: ${comment.sentiment_score.pos.toFixed(2)}`}
                  color="success"
                  variant="outlined"
                />
                <Chip 
                  label={`Neutral: ${comment.sentiment_score.neu.toFixed(2)}`}
                  color="info"
                  variant="outlined"
                />
                <Chip 
                  label={`Negative: ${comment.sentiment_score.neg.toFixed(2)}`}
                  color="error"
                  variant="outlined"
                />
              </Box>
            </CardContent>
          </Card>
        ))}
      </List>

      {postsWithComments.length === 0 && (
        <Typography variant="body1" color="text.secondary">
          No comments found for analysis
        </Typography>
      )}
    </Box>
  );
};

export default TopCommentsList;
