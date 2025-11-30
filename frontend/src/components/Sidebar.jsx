import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./Sidebar.css";

function Sidebar({ selectedPage, setSelectedPage, onToggle, userType }) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const navigate = useNavigate();
  const Logout = () => {
    navigate("/register");
  }

  useEffect(() => {
    if (onToggle) onToggle(isCollapsed);
  }, [isCollapsed, onToggle]);

  // --- Farmer Menu ---
  const farmerMenu = [
    "Dashboard",
    "Market Prices",
    "Weather",
    "Fields",
    "Sell Items",
    "Add Products",
  ];

  // --- Customer Menu ---
  const customerMenu = [
    "Dashboard",
    "Shop",
    "Cart",
  ];

  // 🟢 Select menu based on userType
  const menuItems = userType === "customer" ? customerMenu : farmerMenu;

  return (
    <aside className={`sidebar ${isCollapsed ? "collapsed" : ""}`}>
      {/* Collapse Toggle */}
      <div
        className="sidebar-toggle"
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        {isCollapsed ? ">" : "<"}
      </div>

      {/* Menu List */}
      <ul className="sidebar-menu">
        {menuItems.map((item, index) => (
          <li
            key={index}
            className={`sidebar-item ${
              item === selectedPage ? "active-item" : ""
            }`}
            onClick={() => setSelectedPage(item)}
          >
            {isCollapsed ? item.charAt(0) : item}
          </li>
        ))}
      </ul>

      {/* Logout Button */}
      <div className="logout" onClick={Logout}>
        {isCollapsed ? "⎋" : "Logout"}
      </div>
    </aside>
  );
}

export default Sidebar;