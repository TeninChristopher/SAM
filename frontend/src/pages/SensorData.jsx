import React, { useEffect, useState } from "react";
import "./SensorData.css";

import { onValue, ref } from "firebase/database";
// ⬇️ If SensorData.jsx is in src/components, this path is correct.
// If it's directly in src/, change to "./firebaseConfig".
import { db } from "../firebaseConfig";

const SensorData = () => {
  const [data, setData] = useState({
    soilMoisture: 35,
    soilPH: 6.5,
    temperature: 0,
    humidity: 0,
    rainfall: 0,
  });

  // 🔥 Live temperature & humidity from Firebase
  useEffect(() => {
    const sensorRef = ref(db, "sensor/latest");

    const unsubscribe = onValue(sensorRef, (snapshot) => {
      const val = snapshot.val();
      if (val) {
        setData((prev) => ({
          ...prev,
          temperature: val.temperature,
          humidity: val.humidity,
        }));
      }
    });

    return () => unsubscribe();
  }, []);

  // Simulate other sensors (optional)
  useEffect(() => {
    const interval = setInterval(() => {
      setData((prev) => ({
        ...prev,
        soilMoisture: Number((30 + Math.random() * 20).toFixed(1)),
        soilPH: Number((6 + Math.random() * 1.5).toFixed(2)),
        rainfall: Number((Math.random() * 5).toFixed(2)),
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="sensor-container">
      <h1 className="sensor-title">📊 Real-Time Sensor Data</h1>

      <div className="sensor-grid">
        {/* Soil Moisture Sensor */}
        <div className="sensor-card moisture">
          <h2>🌱 Soil Moisture Sensor</h2>
          <p>Measures the volumetric water content in soil.</p>
          <div className="reading">
            <strong>Current Moisture:</strong> {data.soilMoisture}% 
          </div>
          <p className="info">Optimal range: 25–45% for most crops</p>
        </div>

        {/* Soil pH Sensor */}
        <div className="sensor-card ph">
          <h2>🧪 Soil pH Sensor</h2>
          <p>Monitors soil acidity and alkalinity for crop suitability.</p>
          <div className="reading">
            <strong>Current pH Level:</strong> {data.soilPH}
          </div>
          <p className="info">Ideal range: 6.0–7.5</p>
        </div>

        {/* Temperature Sensor */}
        <div className="sensor-card temp">
          <h2>🌡️ Temperature Sensor</h2>
          <p>Tracks ambient temperature for crop and greenhouse monitoring.</p>
          <div className="reading">
            <strong>Current Temperature:</strong>{" "}
            {data.temperature ? data.temperature.toFixed(1) : "--"}°C
          </div>
          <p className="info">Optimal: 20–32°C for most crops</p>
        </div>

        {/* Humidity Sensor */}
        <div className="sensor-card humidity">
          <h2>💧 Humidity Sensor</h2>
          <p>Measures air moisture to help predict evapotranspiration.</p>
          <div className="reading">
            <strong>Current Humidity:</strong>{" "}
            {data.humidity ? data.humidity.toFixed(1) : "--"}%
          </div>
          <p className="info">Optimal: 60–80%</p>
        </div>

        {/* Rainfall Sensor */}
        <div className="sensor-card rain">
          <h2>🌧️ Rainfall Sensor (Tipping Bucket)</h2>
          <p>Records precipitation levels in millimeters (mm).</p>
          <div className="reading">
            <strong>Recent Rainfall:</strong> {data.rainfall} mm
          </div>
          <p className="info">Each tip = 0.2 mm of rain</p>
        </div>
      </div>
    </div>
  );
};

export default SensorData;