import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import wheat from "../assets/Wheat.jfif";
import styles from "./Purchase.module.css";

function Purchase() {
  const navigate = useNavigate();
  const { state } = useLocation();

  const fromPage = state?.from || "cart"; 
  const selectedItem = state?.selectedItem || null;
  const cartId = localStorage.getItem("cart_id");

  const [purchaseNow, setPurchaseNow] = useState([]);
  const [loading, setLoading] = useState(true);

  const FALLBACK_IMG = "https://via.placeholder.com/140?text=No+Image";

  // Fetch initial cart items
  const fetchInitialItems = async () => {
    if (!cartId) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/cart/${cartId}/`);
      const data = await res.json();
      if (fromPage === "cart" && data.items?.length) {
        const temp = data.items.map(it => ({
          cart_item_id: it.cart_item_id ?? it.id,
          market_id: it.market_items.id,
          qty: it.quantity,
          market_items: it.market_items,
        }));
        setPurchaseNow(temp);
      }
      setLoading(false);
    } catch (err) {
      console.error("Failed to fetch initial items:", err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInitialItems();
  }, [cartId]);

  // If coming from shop → add single item
  useEffect(() => {
    if (fromPage === "shop" && selectedItem) {
      setPurchaseNow([
        {
          cart_item_id: null,
          market_id: selectedItem.id,
          qty: selectedItem.quantity || 1,
          market_items: {
            price: selectedItem.price,
            product_name: selectedItem.product_name,
            image: wheat,
            stock: selectedItem.stock,
          },
        },
      ]);
      setLoading(false);
    }
  }, [fromPage, selectedItem]);

  const updatePurchaseQty = (item, newQty) => {
    if (newQty < 1) return;
    setPurchaseNow(prev =>
      prev.map(p => (p === item ? { ...p, qty: newQty } : p))
    );
  };

  const removeFromPurchaseNow = (item) => {
    setPurchaseNow(prev => prev.filter(p => p !== item));
  };

  const handleConfirmPurchase = async () => {
    if (purchaseNow.length === 0) {
      alert("No items selected for purchase.");
      return;
    }

    const invalidItems = purchaseNow.filter(p => p.qty > p.market_items.stock);
    if (invalidItems.length > 0) {
      let msg = "❌ Some items exceed stock:\n\n";
      invalidItems.forEach(p => {
        msg += `${p.market_items.product_name}: requested ${p.qty}, available ${p.market_items.stock}\n`;
      });
      alert(msg);
      return;
    }

    try {
      const res = await fetch(`http://127.0.0.1:8000/cart/${cartId}/purchase/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      const data = await res.json();
      if (!res.ok) {
        alert(data.error || "Purchase failed.");
        return;
      }

      alert("✅ Purchase successful!");
      setPurchaseNow([]);
      navigate("/mainpage");
    } catch (err) {
      console.error(err);
      alert("Something went wrong.");
    }
  };

  const calcTotal = () =>
    purchaseNow.reduce(
      (sum, p) => sum + (p.market_items.price || 0) * p.qty,
      0
    );

  if (loading) return <h2>Loading...</h2>;

  return (
    <div className={styles.purchasePage}>
      <div className={styles.titleBar}>Confirming Purchase</div>

      <div className={styles.layout}>
        {/* Left: Items */}
        <div className={styles.main}>
          <h2>Purchasing Now</h2>
          {purchaseNow.length === 0 && <p>No items selected.</p>}

          {purchaseNow.map((p, idx) => (
            <div className={styles.itemCard} key={idx}>
              <img
                src={wheat || FALLBACK_IMG}
                alt={p.market_items.product_name}
                className={styles.itemImage}
              />
              <div className={styles.itemInfo}>
                <h3>{p.market_items.product_name}</h3>
                <p>Price: ₹{p.market_items.price}</p>
                <p>Stock: {p.market_items.stock}</p>

                <div className={styles.qtyControls}>
                  <button onClick={() => updatePurchaseQty(p, p.qty - 1)}>-</button>
                  <span>{p.qty}</span>
                  <button onClick={() => updatePurchaseQty(p, p.qty + 1)}>+</button>
                </div>

                <div className={styles.actions}>
                  <button onClick={() => removeFromPurchaseNow(p)}>Remove</button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Right: Price summary */}
        <div className={styles.summary}>
          <h2>Price Breakdown</h2>
          <div className={styles.priceList}>
            {purchaseNow.map((p, idx) => (
              <div className={styles.priceItem} key={idx}>
                <span>{p.market_items.product_name}</span>
                <span>₹{p.qty * p.market_items.price}</span>
              </div>
            ))}
          </div>

          <h3 className={styles.total}>Total: ₹{calcTotal()}</h3>
          <button className={styles.confirmBtn} onClick={handleConfirmPurchase}>
            Confirm Purchase
          </button>
        </div>
      </div>
    </div>
  );
}

export default Purchase;