import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./Cart.module.css";

function Cart() {
  const navigate = useNavigate();
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const cartId = localStorage.getItem("cart_id");

  // Fetch cart from backend
  const fetchCart = async () => {
    if (!cartId) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/cart/${cartId}/`);
      const data = await res.json();
      setCart(data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching cart:", err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
    const handleStorage = (e) => {
      if (e.key === "cart_updated") fetchCart();
    };
    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, [cartId]);

  // Update quantity
  const updateQuantity = async (itemId, qty) => {
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/cart/${cartId}/update_quantity/`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ item_id: itemId, quantity: qty }),
        }
      );
      const data = await res.json();
      setCart(data);
    } catch (err) {
      console.error("Error updating quantity:", err);
    }
  };

  const increaseQty = (item) => {
    if (item.quantity < item.market_items.stock)
      updateQuantity(item.cart_item_id, item.quantity + 1);
  };
  const decreaseQty = (item) => {
    if (item.quantity > 1) updateQuantity(item.cart_item_id, item.quantity - 1);
  };

  // Remove item
  const removeItem = async (itemId) => {
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/cart/${cartId}/remove_item/`,
        {
          method: "DELETE",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ item_id: itemId }),
        }
      );
      const data = await res.json();
      setCart(data);
    } catch (err) {
      console.error("Error removing item:", err);
    }
  };

  const validItems =
    cart?.items.filter((item) => item.quantity <= item.market_items.stock) ||
    [];
  const invalidItems =
    cart?.items.filter((item) => item.quantity > item.market_items.stock) || [];

  const validTotalPrice = validItems.reduce(
    (sum, item) => sum + item.market_items.price * item.quantity,
    0
  );

  const purchaseAll = () => {
    if (!cart || validItems.length === 0) {
      return alert("No valid items to purchase!");
    }
    navigate("/purchase", {
      state: {
        from: "cart",
        cartData: { ...cart, items: validItems, total_price: validTotalPrice },
      },
    });
  };

  if (loading) return <div className={styles.loading}>Loading cart...</div>;
  if (!cart || cart.items.length === 0)
    return <h1 className={styles.emptyCartMessage}>🛒 Your Cart is Empty</h1>;

  return (
    <div className={styles.cartContainer}>
      <h1 className={styles.cartTitle}>Your Shopping Cart</h1>

      {/* INVALID ITEMS */}
      {invalidItems.length > 0 && (
        <div className={styles.invalidSection}>
          <h2 className={styles.invalidTitle}>
            ⚠️ Stock Alert: Items Below Have Quantity Issues
          </h2>
          <p className={styles.invalidMessage}>
            Please reduce the quantity or remove these items to proceed.
          </p>

          <div className={styles.cartItems}>
            {invalidItems.map((item) => (
              <div
                className={`${styles.cartItemCard} ${styles.invalid}`}
                key={`invalid-${item.cart_item_id}`}
              >
                <div className={styles.itemInfo}>
                  <h3 className={styles.productName}>
                    {item.market_items.product_name}
                  </h3>
                  <p className={styles.subtotal}>
                    Price: ₹{item.market_items.price} | Subtotal: ₹
                    {item.market_items.price * item.quantity}
                  </p>
                </div>

                <div className={styles.itemControls}>
                  <div className={styles.qtyControls}>
                    <button
                      onClick={() => decreaseQty(item)}
                      disabled={item.quantity <= 1}
                    >
                      –
                    </button>
                    <span className={styles.currentQty}>{item.quantity}</span>
                    <button
                      onClick={() => increaseQty(item)}
                      disabled={item.quantity >= item.market_items.stock}
                    >
                      +
                    </button>
                  </div>
                  <button
                    className={styles.removeBtn}
                    onClick={() => removeItem(item.cart_item_id)}
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* VALID ITEMS & SUMMARY */}
      <div className={styles.checkoutSummaryContainer}>
        <div className={styles.cartItems}>
          <h2 className={styles.sectionTitle}>
            Ready to Purchase ({validItems.length} items)
          </h2>
          {validItems.map((item) => (
            <div className={styles.cartItemCard} key={`valid-${item.cart_item_id}`}>
              <div className={styles.itemInfo}>
                <h3 className={styles.productName}>
                  {item.product_name || "Unnamed Product"}
                </h3>
                <p className={styles.subtotal}>
                  Price: ₹{item.market_items.price} | Subtotal: ₹
                  {item.total_price * item.quantity}
                </p>
              </div>

              <div className={styles.itemControls}>
                <div className={styles.qtyControls}>
                  <button
                    onClick={() => decreaseQty(item)}
                    disabled={item.quantity <= 1}
                  >
                    –
                  </button>
                  <span className={styles.currentQty}>{item.quantity}</span>
                  <button
                    onClick={() => increaseQty(item)}
                    disabled={item.quantity >= item.market_items.stock}
                  >
                    +
                  </button>
                </div>
                <button
                  className={`${styles.removeBtn} ${styles.secondary}`}
                  onClick={() => removeItem(item.cart_item_id)}
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className={styles.orderSummaryCard}>
          <h2 className={styles.summaryTitle}>Order Summary</h2>
          <div className={styles.summaryLine}>
            <span>Total Valid Items:</span>
            <span>{validItems.length}</span>
          </div>
          <div className={`${styles.summaryLine} ${styles.total}`}>
            <span>Total Price:</span>
            <span>₹{validTotalPrice.toFixed(2)}</span>
          </div>
          <button
            className={styles.purchaseAllBtn}
            onClick={purchaseAll}
            disabled={validItems.length === 0}
          >
            Checkout (₹{validTotalPrice.toFixed(2)})
          </button>
          {invalidItems.length > 0 && (
            <p className={styles.checkoutNote}>
              * Please resolve all stock issues above to complete your order.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default Cart;
