import React, { useState, useEffect } from "react";
import news1 from "../assets/news1.png";
import news2 from "../assets/news2.png";
import news3 from "../assets/news3.png";
import cropsImg from "../assets/crops.jpg";
import weatherImg from "../assets/weather.jpg";
import sensorImg from "../assets/sensor.jpg";

import styles from "./FarmerDashboard.module.css";

function FarmerDashboard({ setSelectedPage }) {
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
      img: news3,
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

  return (
    <div>
      <h1 className={styles.dashboardTitle}>Dashboard</h1>

      <div className={styles.newsSection}>
        <div className={styles.newsImage}>
          <img src={newsData[currentNews].img} alt="News" />
        </div>
        <div className={styles.newsContent}>
          <h3>{newsData[currentNews].title}</h3>
          <p>{newsData[currentNews].text}</p>
        </div>
      </div>

      <div className={styles.infoBoxGrid}>
        
        {/* Best-Selling Crop */}
        <div className={styles.infoBox}>
          <img src={cropsImg} alt="Top Crop" />
          <div className={styles.infoText}>
            <h4>🌾 Best-Selling Crop</h4>
            <p>Rice — ₹48/kg (+18%)</p>
            <p onClick={() => setSelectedPage("Market Prices")}>
              View Market Prices →
            </p>
          </div>
        </div>

        {/* Weather */}
        <div className={styles.infoBox}>
          <img src={weatherImg} alt="Weather" />
          <div className={styles.infoText}>
            <h4>☀️ Weather</h4>
            <p>28°C | Clear skies</p>
            <p onClick={() => setSelectedPage("Weather")}>
              View Weather →
            </p>
          </div>
        </div>

        {/* Sensor Data */}
        <div className={styles.infoBox}>
          <img src={sensorImg} alt="Sensor Data" />
          <div className={styles.infoText}>
            <h4>🌡️ Sensor Data</h4>
            <p>Soil Moisture: 72%</p>
            <p onClick={() => setSelectedPage("Fields")}>
              View Sensor Data →
            </p>
          </div>
        </div>

      </div>
    </div>
  );
}

export default FarmerDashboard;
