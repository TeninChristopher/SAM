import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./FarmerProfile.css";
import farmerImg from "../assets/farmer-profile.jpg";

function FarmerProfile() {
  const navigate = useNavigate();
  const farmer_id = localStorage.getItem("farmer_id");

  const [loading, setLoading] = useState(true);
  const [farmer, setFarmer] = useState({
    name: "",
    email: "",
    password: "",
  });

  // Fetch farmer profile
  useEffect(() => {
    if (!farmer_id) return;

    const fetchFarmerData = async () => {
      try {
        const res = await fetch(`http://localhost:8000/farmer/${farmer_id}/`);

        if (!res.ok) throw new Error("Farmer not found");

        const data = await res.json();
        // data now contains: { farmer_id, name, email, password }

        setFarmer({
          name: data.name,
          email: data.email,
          password: data.password,
        });

        setLoading(false);
      } catch (err) {
        console.error("Error fetching profile:", err);
      }
    };

    fetchFarmerData();
  }, [farmer_id]);

  // Update form state
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFarmer({ ...farmer, [name]: value });
  };

  const handleSave = async () => {
    try {
      const res = await fetch(`http://localhost:8000/farmer/${farmer_id}/`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(farmer),
      });

      if (!res.ok) throw new Error("Failed to update profile");

      const data = await res.json();
      setFarmer({
        name: data.name,
        email: data.email,
        password: data.password,
      });

      alert("✅ Profile updated successfully!");
    } catch (err) {
      console.error("Error updating profile:", err);
      alert("❌ Failed to update profile");
    }
  };

  const GoHome = () => navigate("/mainpage");

  if (loading) return <h2 style={{ textAlign: "center" }}>Loading...</h2>;

  return (
    <div className="sams-profile-page">
      <header className="sams-profile-header">
        <div className="sams-profile-title">Smart Agri-Market Connect (SAMS)</div>
        <div className="sams-profile-header-right">
          <button className="sams-profile-home-btn" onClick={GoHome}>🏠</button>
          <select className="sams-profile-dropdown">
            <option>Profile</option>
            <option>Settings</option>
          </select>
        </div>
      </header>

      <div className="sams-profile-card">
        <div className="sams-profile-pic-container">
          <img src={farmerImg} alt="Farmer" className="sams-profile-pic" />
        </div>

        <div className="sams-profile-details">

          <div className="sams-profile-detail">
            <strong>Name:</strong>
            <input
              type="text"
              name="name"
              value={farmer.name}
              onChange={handleChange}
            />
          </div>

          <div className="sams-profile-detail">
            <strong>Email:</strong>
            <input
              type="text"
              name="email"
              value={farmer.email}
              onChange={handleChange}
            />
          </div>

          <div className="sams-profile-detail">
            <strong>Password:</strong>
            <input
              type="password"
              name="password"
              value={farmer.password}
              onChange={handleChange}
            />
          </div>

          <div className="sams-profile-actions">
            <button onClick={handleSave} className="action-btn">
              Save Changes
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}

export default FarmerProfile;
