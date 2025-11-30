// src/App.jsx
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Homepage from "./pages/Homepage.jsx";
import Register from "./pages/Register.jsx";
import FarmerDashboard from "./pages/FarmerDashboard.jsx";
import Weather from "./pages/Weather.jsx";
import MarketPrices from "./pages/MarketPrices.jsx";
import CustomerDashboard from "./pages/CustomerDashboard.jsx";
import Mainpage from "./pages/Mainpage.jsx";
import FarmerProfile from "./pages/FarmerProfile.jsx";
import Purchase from "./pages/Purchase.jsx";


function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Homepage />} />
        <Route path="/register" element={<Register />} />
        <Route path="/mainpage" element={<Mainpage />} />
        <Route path="/farmer" element={<FarmerDashboard />} />
        <Route path="/weather" element={<Weather />} />
        <Route path="/marketprices" element={<MarketPrices />} />
        <Route path="/customer" element={<CustomerDashboard />} />
        <Route path="/farmerprofile" element={<FarmerProfile />}/>
        <Route path="/purchase" element={<Purchase />}/>
      </Routes>
    </Router>
  );
}

export default App;