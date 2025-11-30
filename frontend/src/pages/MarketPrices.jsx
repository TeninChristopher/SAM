import React, { useState, useEffect } from "react";
import "./MarketPrices.css";

const MarketPrices = () => {
  const [cropData, setCropData] = useState([]);
  const [selectedCrop, setSelectedCrop] = useState("");
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [hidePrediction, setHidePrediction] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch("http://localhost:8000/crop-prices/");
        const data = await res.json();

        // Map API response to structured data
        const formatted = data.map((item) => ({
          crop: item.crop || "Unknown Crop",
          today: {
            date: item.year ? `${item.year}-01-01` : "N/A",
            price: item.synthetic_price ?? 0,
          },
          forecast: (item.forecast_7_days || []).map((f) => ({
            date: f.date || "N/A",
            price: f.price_estimate ?? 0,
          })),
        }));

        setCropData(formatted);
      } catch (err) {
        console.error("Failed to fetch crop prices:", err);
      }
    };

    fetchData();
  }, []);

  const handleSelectCrop = (option) => {
    if (option === "hide") {
      setHidePrediction(true);
      setSelectedCrop("");
    } else {
      setSelectedCrop(option);
      setHidePrediction(false);
    }
    setDropdownOpen(false);
  };

  // Today's prices
  const todayData = cropData
    .filter((c) => !selectedCrop || c.crop === selectedCrop)
    .map((c) => ({ crop: c.crop, date: c.today.date, price: c.today.price }))
    .sort((a, b) => b.price - a.price);

  // Prediction data for selected crop
  const predictionData = selectedCrop
    ? cropData
        .filter((c) => c.crop === selectedCrop)
        .flatMap((c) => c.forecast)
    : [];

  return (
    <div className="market-container">
      <div className="market-header">
        <h1>Market Prices</h1>
        <div className="custom-dropdown">
          <button className="dropdown-btn" onClick={() => setDropdownOpen(!dropdownOpen)}>
            {hidePrediction ? "Hide Prediction" : selectedCrop || "Select Crop"}
            <span className="arrow">{dropdownOpen ? "▲" : "▼"}</span>
          </button>
          {dropdownOpen && (
            <ul className="dropdown-list">
              <li onClick={() => handleSelectCrop("hide")}>Hide Prediction</li>
              {cropData.map((crop, index) => (
                <li key={index} onClick={() => handleSelectCrop(crop.crop)}>
                  {crop.crop}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Today's Market Price Table */}
      <h2>Today's Market Price</h2>
      <table className="market-table">
        <thead>
          <tr>
            <th>Crop</th>
            <th>Date</th>
            <th>Price (₹ / kg)</th>
          </tr>
        </thead>
        <tbody>
          {todayData.map((entry, index) => (
            <tr key={index}>
              <td>{entry.crop}</td>
              <td>{entry.date}</td>
              <td>₹ {entry.price}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Prediction Table */}
      {selectedCrop && !hidePrediction && predictionData.length > 0 && (
        <>
          <h2>7-Day Predicted Prices for {selectedCrop}</h2>
          <table className="market-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Predicted Price (₹ / kg)</th>
              </tr>
            </thead>
            <tbody>
              {predictionData.map((entry, index) => (
                <tr key={index}>
                  <td>{entry.date}</td>
                  <td>₹ {entry.price}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
};

export default MarketPrices;
