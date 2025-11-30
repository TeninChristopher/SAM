import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./TitleBar.css";

function TitleBar({ email }) {
  const [showProfile, setShowProfile] = useState(false);
  //const [userProfile, setuserProfile] = useState()
  const navigate = useNavigate();
  const goprofile = () => {
    navigate("/farmerprofile");
  }

  return (
    <div className="farmer-1">
      <div className="farmer-1-title">Smart Agri-Market Connect (SAMS)</div>

      <div className="profile-bar" onClick={() => setShowProfile(!showProfile)}>
        <div className="profile-circle">
          👤
        </div>
        <div className="profile-user">Farmer John</div>
      </div>

      {showProfile && (
        <div className="profile-card">
          <p><b>{email}</b></p>
          <hr />
          <p onClick={goprofile}>Profile</p>
          <p>Items for Sale</p>
        </div>
      )}
    </div>
  );
}

export default TitleBar;