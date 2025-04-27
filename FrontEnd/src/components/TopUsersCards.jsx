import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./TopUsersCards.css";

const TopUsersCards = () => {
  const [users, setUsers] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    axios.get("http://localhost:5001/top5/users")
      .then((res) => {
        console.log("API Response:", res.data); // Debug log
        setUsers(res.data);
      })
      .catch((err) => console.error("Failed to fetch top users", err));
  }, []);

  return (
    <div className="top-users-container">
      {users.map((user) => (
        <div
          className="user-card"
          key={user.user_id}
          onClick={() => {
            console.log("Navigating to:", user.user_id);
            navigate(`/dashboard/${user.user_id}`);
          }}
          role="button"
          tabIndex={0}
        >
          <h3>{user.name}</h3>
          <div className="user-details">
            <div>🔥 Total Engagement: {user.total_engagement}</div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default TopUsersCards;
