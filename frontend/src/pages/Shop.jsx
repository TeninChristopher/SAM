import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import wheat from "../assets/Wheat.jfif";
import rice from "../assets/Rice.jfif";
import corn from "../assets/Corn.jfif";
import sugarcane from "../assets/Sugarcane.jfif";
import deefault from "../assets/default.jfif";
import styles from "./Shop.module.css";

function Shop() {
  const [items, setItems] = useState([]);
  const [filteredItems, setFilteredItems] = useState([]);
  const [farmers, setFarmers] = useState({});
  const [customer, setCustomer] = useState(null);
  const [cartId, setCartId] = useState(null);
  const [recommendedItems, setRecommendedItems] = useState([]);
  const [search, setSearch] = useState("");
  const [cropType, setCropType] = useState("All");
  const [sortType, setSortType] = useState("Newest");
  const [priceRange, setPriceRange] = useState([0, 10000]);
  const navigate = useNavigate();

  const cropImages = {
    Wheat: wheat,
    Rice: rice,
    Corn: corn,
    Sugarcane: sugarcane,
    Default: deefault,
  };

  useEffect(() => {
    const userType = localStorage.getItem("userType");
    const userId = localStorage.getItem("user_id");
    if (userType !== "customer" || !userId) return;
    fetch(`http://127.0.0.1:8000/customer/?user_id=${userId}`)
      .then((res) => res.json())
      .then((data) => {
        setCustomer(data);
        if (data.cart_id) setCartId(data.cart_id);
        if (data.customer_id) localStorage.setItem("customer_id", data.customer_id);
      })
      .catch(console.log);
  }, []);

  const fetchMarketItems = () => {
    fetch("http://127.0.0.1:8000/market/")
      .then((res) => res.json())
      .then((data) => {
        const updated = data.map((item) => ({ ...item, qty: 1 }));
        updated.sort((a, b) => new Date(b.date_added) - new Date(a.date_added));
        setItems(updated);
        setFilteredItems(updated);
        updated.forEach((item) => item.stock <= 0 && deleteMarketItem(item.id));
      })
      .catch(console.log);
  };

  useEffect(() => fetchMarketItems(), []);

  const deleteMarketItem = async (itemId) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/market/${itemId}/`, { method: "DELETE" });
      if (res.ok) {
        setItems((prev) => prev.filter((i) => i.id !== itemId));
        setFilteredItems((prev) => prev.filter((i) => i.id !== itemId));
      }
    } catch (err) { console.log(err); }
  };

  useEffect(() => {
    const customerId = localStorage.getItem("customer_id");
    if (!customerId) return;
    fetch(`http://127.0.0.1:8000/recommendations/${customerId}/`)
      .then((res) => res.json())
      .then((data) => data.success && setRecommendedItems(data.data))
      .catch(console.log);
  }, [customer]);

  const fetchFarmerName = async (farmerId) => {
    if (!customer || farmers[farmerId]) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/farmer/${farmerId}/`);
      const data = await res.json();
      setFarmers((prev) => ({
        ...prev,
        [farmerId]: data.user?.name || data.name || "Unknown Farmer",
      }));
    } catch (err) { console.log(err); }
  };

  useEffect(() => {
    if (!customer) return;
    items.forEach((item) => fetchFarmerName(item.farmer));
  }, [items, customer]);

  useEffect(() => {
    let updated = [...items];
    if (search) updated = updated.filter((i) => i.product_name.toLowerCase().includes(search.toLowerCase()));
    if (cropType !== "All") updated = updated.filter((i) => i.product_name === cropType);
    updated = updated.filter((i) => i.price >= priceRange[0] && i.price <= priceRange[1]);
    if (sortType === "Cheapest") updated.sort((a,b)=>a.price-b.price);
    else if(sortType==="Highest") updated.sort((a,b)=>b.price-a.price);
    else updated.sort((a,b)=>new Date(b.date_added)-new Date(a.date_added));
    setFilteredItems(updated);
  }, [search, cropType, sortType, priceRange, items]);

  const increaseQty = (id) => setFilteredItems(prev => prev.map(i => i.id===id && i.qty<i.stock ? {...i, qty:i.qty+1} : i));
  const decreaseQty = (id) => setFilteredItems(prev => prev.map(i => i.id===id && i.qty>1 ? {...i, qty:i.qty-1} : i));

  const addToCart = async (item) => {
    if (!cartId) return alert("Cart not ready.");
    try {
      const res = await fetch(`http://127.0.0.1:8000/cart/${cartId}/add_item/`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({market_item_id:item.id, quantity:item.qty}),
      });
      const data = await res.json();
      if(res.ok){
        alert(`${item.product_name} added to cart!`);
        item.stock -= item.qty;
        if(item.stock<=0) deleteMarketItem(item.id);
        setItems([...items]);
      } else alert(data.error||"Failed to add to cart");
    } catch(err){ console.log(err); alert("Server error."); }
  };

  const buyNow = (item) => navigate("/purchase", { state: { from: "shop", selectedItem: {...item, image: cropImages[item.product_name]||cropImages.Default} } });

  return (
    <div className={styles.shopContainer}>
      <div className={styles.filterSidebar}>
        <h2>Filters</h2>
        <input type="text" placeholder="Search crop..." value={search} onChange={(e)=>setSearch(e.target.value)} className={styles.searchBar}/>
        <label>Crop Type</label>
        <select value={cropType} onChange={(e)=>setCropType(e.target.value)}>
          <option value="All">All</option>
          {Array.from(new Set(items.map(i=>i.product_name))).map(crop=><option key={crop} value={crop}>{crop}</option>)}
        </select>
        <label>Max Price</label>
        <input type="range" min="0" max="10000" value={priceRange[1]} onChange={e=>setPriceRange([0, Number(e.target.value)])}/>
        <span>₹0 - ₹{priceRange[1]}</span>
        <label>Sort By</label>
        <select value={sortType} onChange={e=>setSortType(e.target.value)}>
          <option value="Newest">Newest</option>
          <option value="Cheapest">Cheapest</option>
          <option value="Highest">Highest</option>
        </select>
      </div>

      <div className={styles.shopMain}>
        <div className={styles.recommendedSlideshow}>
          <h2>Recommended for You</h2>
          {recommendedItems.length===0 ? <p>No recommendations yet.</p> :
            <div className={styles.slideshowContainer}>
              {recommendedItems.map(item=>(
                <div key={item.id} className={styles.slide}>
                  <img src={cropImages[item.crop_name]||cropImages.Default} alt={item.crop_name} className={styles.slideImg}/>
                  <div className={styles.slideInfo}>
                    <h3>{item.crop_name}</h3>
                    <p>₹{item.price} {item.discount>0 && `(${item.discount}% off)`}</p>
                    <p>Available: {item.stock}</p>
                    <p>Farmer: {item.farmer_name}</p>
                    <div className={styles.slideActions}>
                      <button onClick={()=>addToCart(item)}>Add to Cart</button>
                      <button onClick={()=>buyNow(item)}>Buy Now</button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          }
        </div>

        <div className={styles.shopItems}>
          <h1>Available Crops</h1>
          <div className={styles.itemGrid}>
            {filteredItems.length===0 ? <p>No items match your filters.</p> :
              filteredItems.map(item=>(
                <div key={item.id} className={styles.itemCard}>
                  <img src={cropImages[item.product_name]||cropImages.Default} alt={item.product_name} className={styles.itemImg}/>
                  <h3>{item.product_name}</h3>
                  <p className={styles.price}>₹{item.price} {item.discount>0 && <span className={styles.discount}>({item.discount}% off)</span>}</p>
                  <p className={styles.seller}>Seller: {farmers[item.farmer]||"Loading..."}</p>
                  <p className={styles.stock}>Available: {item.stock}</p>
                  <div className={styles.qtySelector}>
                    <button onClick={()=>decreaseQty(item.id)}>-</button>
                    <span>{item.qty}</span>
                    <button onClick={()=>increaseQty(item.id)}>+</button>
                  </div>
                  <div className={styles.actions}>
                    <button className={styles.addCart} onClick={()=>addToCart(item)}>Add to Cart</button>
                    <button className={styles.buyNow} onClick={()=>buyNow(item)}>Buy Now</button>
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Shop;
