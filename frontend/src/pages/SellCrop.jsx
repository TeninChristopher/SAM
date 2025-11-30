import React, { useState, useEffect, useMemo } from "react";
import "./SellCrop.css";

const SellCrop = () => {
  // Retrieve farmer_id early
  const farmer_id = useMemo(() => localStorage.getItem("farmer_id"), []);

  const [crop, setCrop] = useState("");
  const [reapDate, setReapDate] = useState("");
  const [weight, setWeight] = useState("");
  const [stock, setStock] = useState("");
  const [discount, setDiscount] = useState(0);

  const [products, setProducts] = useState([]);
  const [availableReapDates, setAvailableReapDates] = useState([]);
  const [maxWeight, setMaxWeight] = useState(0);

  const [pricePerStock, setPricePerStock] = useState(0);
  const [cropsInMarket, setCropsInMarket] = useState([]);

  // NEW: Crop prices from backend
  const [cropPrices, setCropPrices] = useState([]);

  // -----------------------------
  // Fetch crop prices from backend
  // -----------------------------
  useEffect(() => {
    fetch("http://localhost:8000/crop-prices/")
      .then((res) => res.json())
      .then((data) => setCropPrices(data))
      .catch((err) => console.error("Failed to fetch crop prices:", err));
  }, []);

  // Convert backend crop prices into a lookup map
  const marketPriceMap = useMemo(() => {
    const map = {};
    cropPrices.forEach((item) => {
      map[item.crop] = item.synthetic_price; // backend price
    });
    return map;
  }, [cropPrices]);

  // -------------------------------------------------
  // Fetch farmer products
  // -------------------------------------------------
  const refreshProducts = () => {
    if (!farmer_id) return;
    fetch(`http://localhost:8000/products/?farmer_id=${farmer_id}`)
      .then((res) => res.json())
      .then((data) => setProducts(data))
      .catch((err) => console.error("Failed to refresh products:", err));
  };

  useEffect(() => {
    if (!farmer_id) return;
    refreshProducts();
  }, [farmer_id]);

  // -------------------------------------------------
  // Fetch farmer market listings
  // -------------------------------------------------
  useEffect(() => {
    if (!farmer_id) return;
    fetch(`http://localhost:8000/market/?farmer_id=${farmer_id}`)
      .then((res) => res.json())
      .then((data) => setCropsInMarket(data))
      .catch((err) =>
        console.error("Failed to fetch market listings:", err)
      );
  }, [farmer_id]);

  // -------------------------------------------------
  // Update available reap dates when crop changes
  // -------------------------------------------------
  useEffect(() => {
    if (!crop) {
      setAvailableReapDates([]);
      setReapDate("");
      return;
    }
    const dates = products
      .filter((p) => p.name === crop)
      .map((p) => p.reap_date);

    setAvailableReapDates(dates);
    setReapDate("");
  }, [crop, products]);

  // -------------------------------------------------
  // Update max weight based on crop + date
  // -------------------------------------------------
  useEffect(() => {
    if (!crop || !reapDate) {
      setMaxWeight(0);
      return;
    }
    const prod = products.find(
      (p) => p.name === crop && p.reap_date === reapDate
    );
    setMaxWeight(prod ? prod.quantity : 0);
  }, [crop, reapDate, products]);

  // -------------------------------------------------
  // Price calculation using REAL crop-prices backend
  // -------------------------------------------------
  useEffect(() => {
    const w = Number(weight);
    const s = Number(stock);
    const d = Number(discount);

    if (w > 0 && s > 0) {
      const basePrice = marketPriceMap[crop] || 10;

      const priceForOneStock = w * basePrice * (1 - d / 100);
      setPricePerStock(priceForOneStock.toFixed(2));
    } else {
      setPricePerStock(0);
    }
  }, [weight, stock, discount, crop, marketPriceMap]);

  // -------------------------------------------------
  // POST — Add crop to market
  // -------------------------------------------------
  const handleAddToMarket = async () => {
    if (!crop || !reapDate || !weight || !stock)
      return alert("Please fill all fields.");

    const totalWeight = Number(weight) * Number(stock);

    if (totalWeight > maxWeight) {
      return alert(
        `Total weight (${totalWeight} kg) exceeds available (${maxWeight} kg).`
      );
    }

    const selectedProduct = products.find(
      (p) => p.name === crop && p.reap_date === reapDate
    );

    if (!selectedProduct)
      return alert("Product not found in your inventory.");

    const payload = {
      farmer: farmer_id,
      product: selectedProduct.id,
      product_name: crop,
      weight: Number(weight),
      stock: Number(stock),
      discount: Number(discount),
      price: Number(pricePerStock),
    };

    try {
      const res = await fetch("http://localhost:8000/market/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const error = await res.json();
        alert(error.error || error.message || "Error adding crop");
        return;
      }

      const added = await res.json();
      setCropsInMarket([added, ...cropsInMarket]);
      refreshProducts();

      // Reset
      setCrop("");
      setReapDate("");
      setWeight("");
      setStock("");
      setDiscount(0);
      setPricePerStock(0);

      alert("Crop added to market successfully!");
    } catch (err) {
      console.error(err);
      alert("Error adding crop.");
    }
  };

  // -------------------------------------------------
  // DELETE — Remove from market
  // -------------------------------------------------
  const handleDeleteMarketItem = async (id) => {
    if (!window.confirm("Delete this item?")) return;

    try {
      const res = await fetch(`http://localhost:8000/market/${id}/`, {
        method: "DELETE",
      });

      if (!res.ok) return alert("Delete failed.");

      setCropsInMarket(cropsInMarket.filter((i) => i.id !== id));
      refreshProducts();
      alert("Item deleted successfully.");
    } catch (err) {
      console.error(err);
      alert("Error deleting item.");
    }
  };

  // -----------------------------------------------------------
  // UI Rendering
  // -----------------------------------------------------------
  return (
    <div className="sell-crop-page">
      <h1>Sell Your Crop</h1>

      <div className="sell-crop-form">
        {/* Crop */}
        <label>
          Crop:
          <select value={crop} onChange={(e) => setCrop(e.target.value)}>
            <option value="">Select Crop</option>
            {Array.from(new Set(products.map((p) => p.name))).map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        </label>

        {/* Reap Date */}
        <label>
          Reap Date:
          <select
            value={reapDate}
            onChange={(e) => setReapDate(e.target.value)}
            disabled={!crop}
          >
            <option value="">Select Date</option>
            {availableReapDates.map((d) => (
              <option key={d}>{d}</option>
            ))}
          </select>
        </label>

        {/* Weight */}
        <label>
          Weight per Stock (kg):
          <input
            type="number"
            min="1"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
            disabled={!reapDate}
          />
          {reapDate && (
            <small style={{ color: "#475569" }}>
              Available: {maxWeight} kg total
            </small>
          )}
        </label>

        {/* Stock */}
        <label>
          Stock:
          <input
            type="number"
            min="1"
            value={stock}
            onChange={(e) => setStock(e.target.value)}
            disabled={!reapDate}
          />
        </label>

        {/* Discount + price preview */}
        {reapDate && (
          <>
            <label>
              Discount (%):
              <input
                type="number"
                min="0"
                max="100"
                value={discount}
                onChange={(e) => setDiscount(e.target.value)}
              />
            </label>

            {Number(weight) > 0 && Number(stock) > 0 && (
              <p>
                <strong>Price per stock:</strong> ₹{pricePerStock}
              </p>
            )}
          </>
        )}

        <button
          onClick={handleAddToMarket}
          disabled={!crop || !reapDate || !weight || !stock}
        >
          Add to Market
        </button>
      </div>

      <hr />

      {/* Market Listings */}
      <div className="market-list-section">
        <h2>My Market Listings</h2>

        {cropsInMarket.length === 0 && (
          <p style={{ textAlign: "center", color: "#64748b" }}>
            No crops listed yet.
          </p>
        )}

        <div className="market-list">
          {cropsInMarket.map((item) => (
            <div key={item.id} className="crop-card">
              <h3>{item.product_name}</h3>
              <p><strong>Weight:</strong> {item.weight} kg</p>
              <p><strong>Stock:</strong> {item.stock}</p>
              <p><strong>Discount:</strong> {item.discount}%</p>
              <p><strong>Price per Stock:</strong> ₹{item.price}</p>
              <p>
                <small>
                  Date: {new Date(item.date_added).toLocaleDateString()}
                </small>
              </p>

              <button
                className="delete-btn"
                onClick={() => handleDeleteMarketItem(item.id)}
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SellCrop;