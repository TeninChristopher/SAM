import React, { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar.jsx";
import TitleBar from "../components/TitleBar.jsx";
import Profile from "./Profile.jsx"; // import your Profile page here
import MarketPrices from "./MarketPrices.jsx"; // import your MarketPrices page here
import Weather from "./Weather.jsx"; // import your Weather page here
import SensorData from "./SensorData.jsx"; // import your SensorData page here
import news1 from "../assets/news1.png";
import news2 from "../assets/news2.png";
import "./FarmerDashboard.css";

function FarmerDashboard() {
  const [selectedPage, setSelectedPage] = useState("Dashboard");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [currentNews, setCurrentNews] = useState(0);

  const newsData = [
    {
      img: news1,
      title: "Government announces new subsidy for organic farming",
      text: "Farmers can now avail up to 30% subsidy for switching to organic practices.",
    },
    {
      img: news2,
      title: "Monsoon rains expected next week",
      text: "IMD predicts moderate rainfall in most parts of North India.",
    },
    {
      img: "./assets/news3.jpg",
      title: "Wheat prices surge due to global shortage",
      text: "Export restrictions lifted, driving local market prices upward.",
    },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentNews((prev) => (prev + 1) % newsData.length);
    }, 4000);
    return () => clearInterval(interval);
  }, [newsData.length]);

  // 👇 Switch content dynamically based on sidebar selection
  const renderContent = () => {
    switch (selectedPage) {
      case "Dashboard":
        return (
          <div>
            <h1 className="dashboard-title">Dashboard</h1>
            <div className="news-section">
              <div className="news-image">
                <img src={newsData[currentNews].img} alt="News" />
              </div>
              <div className="news-content">
                <h3>{newsData[currentNews].title}</h3>
                <p>{newsData[currentNews].text}</p>
              </div>
            </div>

            <div className="info-box-grid">
              <div className="info-box">
                <img src="./assets/crops.jpg" alt="Top Crop" />
                <div className="info-text">
                  <h4>🌾 Best-Selling Crop</h4>
                  <p>Rice — ₹48/kg (+18%)</p>
                  <a href="#">View Market Prices →</a>
                </div>
              </div>

              <div className="info-box">
                <img src="./assets/weather.jpg" alt="Weather" />
                <div className="info-text">
                  <h4>☀️ Weather</h4>
                  <p>28°C | Clear skies</p>
                  <a href="#">View Weather →</a>
                </div>
              </div>

              <div className="info-box">
                <img src="./assets/sensor.jpg" alt="Sensor Data" />
                <div className="info-text">
                  <h4>🌡️ Sensor Data</h4>
                  <p>Soil Moisture: 72%</p>
                  <a href="#">View Sensor Data →</a>
                </div>
              </div>
            </div>
          </div>
        );

      case "Weather":
        return <Weather />; // render your weather component

      case "Market Prices":
        return <MarketPrices />; // render your MarketPrices component

      case "Profile":
        return <Profile />; // render your Profile component
      
      case "Sensor Data":
        return <SensorData />; // render your SensorData component

      default:
        return <p className="page-content">Select a page from the sidebar.</p>;
    }
  };

  return (
    <div>
      <Sidebar
        selectedPage={selectedPage}
        setSelectedPage={setSelectedPage}
        onToggle={(collapsed) => setSidebarCollapsed(collapsed)}
        userType="farmer"
      />
      <TitleBar />
      <main 
        className={`dashboard-main ${
          sidebarCollapsed ? "collapsed" : ""
        }`}
      >
        {renderContent()}
      </main>
    </div>
  );
}

export default FarmerDashboard;