import React, { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar.jsx";
import TitleBar from "../components/TitleBar.jsx";
import MarketPrices from "./MarketPrices.jsx";
import Weather from "./Weather.jsx";
import SensorData from "./SensorData.jsx";
import FarmerDashboard from "./FarmerDashboard.jsx";
import CustomerDashboard from "./CustomerDashboard.jsx";
import SellCrop from "./SellCrop.jsx";
import FarmerAddProducts from "./FarmerAddProducts.jsx";
import Shop from "./Shop.jsx";
import Cart from "./Cart.jsx";
import "./Mainpage.css";

function Mainpage() {
  const userType = localStorage.getItem("userType") || "farmer";
  const user_id = localStorage.getItem("user_id") || "0";
  const email = localStorage.getItem("email") || "sample@gmail.com";

  const [selectedPage, setSelectedPage] = useState("Dashboard");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const [farmerData, setFarmerData] = useState(null);
  const [customerData, setCustomerData] = useState(null);

  // ============================
  // FETCH FARMER DETAILS — ONLY FOR FARMERS
  // ============================
  useEffect(() => {
    if (userType !== "farmer") return;
    if (!user_id || user_id === "0") return;

    const fetchFarmer = async () => {
      try {
        const res = await fetch(`http://localhost:8000/farmer/?user_id=${user_id}`);
        if (!res.ok) throw new Error("Farmer not found");

        const data = await res.json();
        setFarmerData(data);

        // Store farmer_id for other pages
        if (data.farmer_id) localStorage.setItem("farmer_id", data.farmer_id);
      } catch (error) {
        console.error("Error fetching farmer:", error);
      }
    };

    fetchFarmer();
  }, [userType, user_id]);

  // ============================
  // FETCH CUSTOMER DETAILS — ONLY FOR CUSTOMERS
  // ALSO RETURNS CART_ID
  // ============================
  useEffect(() => {
    if (userType !== "customer") return;
    if (!user_id || user_id === "0") return;

    const fetchCustomer = async () => {
      try {
        const res = await fetch(`http://localhost:8000/customer/?user_id=${user_id}`);
        if (!res.ok) throw new Error("Customer not found");

        const data = await res.json();
        setCustomerData(data);

        // Save cart_id for Shop.jsx
        if (data.cart_id) localStorage.setItem("cart_id", data.cart_id);

        // Save customer_id for future use
        if (data.customer_id) localStorage.setItem("customer_id", data.customer_id);
      } catch (error) {
        console.error("Customer fetch error:", error);
      }
    };

    fetchCustomer();
  }, [userType, user_id]);

  // ============================
  // PAGE SELECTOR
  // ============================
  const renderContent = () => {
    switch (selectedPage) {
      case "Dashboard":
        return userType === "farmer" ? <FarmerDashboard setSelectedPage={setSelectedPage} /> : <CustomerDashboard setSelectedPage={setSelectedPage}/>;
      case "Weather":
        return <Weather />;
      case "Market Prices":
        return <MarketPrices />;
      case "Fields":
        return <SensorData />;
      case "Sell Items":
        return <SellCrop />;
      case "Add Products":
        return <FarmerAddProducts />;
      case "Shop":
        return <Shop />;
      case "Cart":
        return <Cart />;
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
        userType={userType}
      />

      <TitleBar email={email} />

      <main className={`dashboard-main ${sidebarCollapsed ? "collapsed" : ""}`}>
        {renderContent()}
      </main>
    </div>
  );
}

export default Mainpage;