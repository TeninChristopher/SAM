import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import "./FarmerAddProducts.css";

const FarmerAddProducts = () => {
  const [products, setProducts] = useState([]);
  const [name, setName] = useState("");
  const [quantity, setQuantity] = useState("");
  const [reapDate, setReapDate] = useState("");

  // CSV
  const [csvPreview, setCsvPreview] = useState([]);
  const [csvErrors, setCsvErrors] = useState([]);

  const farmer_id = localStorage.getItem("farmer_id");

  // --- Fetch farmer's products ---
  useEffect(() => {
    if (!farmer_id) return;
    const fetchProducts = async () => {
      try {
        const res = await fetch(`http://localhost:8000/products/?farmer_id=${farmer_id}`);
        const data = await res.json();
        setProducts(data);
      } catch (err) {
        console.error("Error fetching products:", err);
      }
    };
    fetchProducts();
  }, [farmer_id]);

  // --- Add / update single product ---
  const handleAddProduct = async (e) => {
    e.preventDefault();
    if (!name || !quantity || !reapDate) return;

    const newProduct = {
      farmer: parseInt(farmer_id),
      name,
      quantity: parseFloat(quantity),
      reap_date: reapDate
    };

    try {
      const res = await fetch("http://localhost:8000/products/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newProduct),
      });

      let added;
      try { 
        added = await res.json();
      } catch {
        console.error("Server did not return JSON");
        return;
      }

      if (!res.ok) throw new Error(added.error || "Failed to add product");

      // Update local state and sum repeated crops for same farmer + name + reap date
      setProducts(prev => {
        const existing = prev.find(
          p => p.name.toLowerCase() === added.name.toLowerCase() && p.reap_date === added.reap_date
        );
        if (existing) {
          return prev.map(p =>
            p.name.toLowerCase() === added.name.toLowerCase() && p.reap_date === added.reap_date
              ? { ...p, quantity: added.quantity }
              : p
          );
        } else {
          return [added, ...prev];
        }
      });

      setName("");
      setQuantity("");
      setReapDate("");
    } catch (err) {
      console.error(err);
      alert(err.message);
    }
  };

  // --- CSV Upload & Preview ---
  const handleCSVUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        const rows = results.data.map((row, idx) => ({
          ...row,
          rowNumber: idx + 1,
          valid: !!row.name && !!row.quantity && !!row.reap_date
        }));
        setCsvPreview(rows);
        setCsvErrors(rows.filter(r => !r.valid));
      }
    });
  };

  // --- Upload valid CSV rows ---
  const handleUploadCSV = async () => {
    const validRows = csvPreview.filter(r => r.valid);
    let successfulUploads = 0;

    for (const row of validRows) {
      const newProduct = {
        farmer: parseInt(farmer_id),
        name: row.name,
        quantity: parseFloat(row.quantity),
        reap_date: row.reap_date
      };

      try {
        const res = await fetch("http://localhost:8000/products/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(newProduct)
        });

        let added;
        try { added = await res.json(); } catch { continue; }

        if (res.ok) {
          setProducts(prev => {
            const existing = prev.find(
              p => p.name.toLowerCase() === added.name.toLowerCase() && p.reap_date === added.reap_date
            );
            if (existing) {
              return prev.map(p =>
                p.name.toLowerCase() === added.name.toLowerCase() && p.reap_date === added.reap_date
                  ? { ...p, quantity: added.quantity }
                  : p
              );
            } else {
              return [added, ...prev];
            }
          });
          successfulUploads++;
        }
      } catch (err) {
        console.error(err);
      }
    }

    alert(`CSV uploaded successfully! ${successfulUploads} crops added/updated.`);
    setCsvPreview([]);
    setCsvErrors([]);
  };

  return (
    <div className="farmer-inventory-container">
      <h1>Manage Your Crops 🌾</h1>

      {/* Manual Add Form */}
      <form className="farmer-inventory-form" onSubmit={handleAddProduct}>
        <div className="form-row">
          <label>Crop Name:</label>
          <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g., Wheat" required />
        </div>
        <div className="form-row">
          <label>Quantity (kg):</label>
          <input type="number" value={quantity} onChange={(e) => setQuantity(e.target.value)} required />
        </div>
        <div className="form-row">
          <label>Reap Date:</label>
          <input type="date" value={reapDate} onChange={(e) => setReapDate(e.target.value)} required />
        </div>
        <button type="submit">Add / Update Crop</button>
      </form>

      <hr />

      {/* CSV Upload */}
      <div className="farmer-inventory-section">
        <h2>Bulk Upload via CSV</h2>
        <input type="file" accept=".csv" onChange={handleCSVUpload} />
        <p>CSV columns required: <strong>name, quantity, reap_date</strong></p>

        {csvPreview.length > 0 && (
          <>
            <h3>Preview ({csvPreview.filter(r => r.valid).length} valid rows)</h3>
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Crop Name</th>
                  <th>Quantity</th>
                  <th>Reap Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {csvPreview.map(row => (
                  <tr key={row.rowNumber}>
                    <td>{row.rowNumber}</td>
                    <td>{row.name || "MISSING"}</td>
                    <td>{row.quantity || "MISSING"}</td>
                    <td>{row.reap_date || "MISSING"}</td>
                    <td>{row.valid ? "✅ Valid" : "❌ Invalid"}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            {csvErrors.length === 0 && (
              <button onClick={handleUploadCSV}>Upload Valid Crops</button>
            )}
          </>
        )}
      </div>

      <hr />

      {/* Product List */}
      <div className="farmer-products-list">
        <h2>My Crops ({products.length})</h2>
        {products.length === 0 && <p>No crops added yet.</p>}
        {products.map(p => (
          <div key={`${p.name}-${p.reap_date}`} className="farmer-inventory-card">
            <strong>{p.name}</strong>
            <p>Quantity: {p.quantity} kg</p>
            <p>Reap Date: {p.reap_date}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FarmerAddProducts;
