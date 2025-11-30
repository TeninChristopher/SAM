import React, { useState, useEffect } from "react";
import mostselling from "../assets/mostselling.jfif";
import cheapest from "../assets/cheapest.jfif";
import newcrop from "../assets/newcrop.jfif";
import shop from "../assets/shop.jfif";
import cart from "../assets/cart.jfif";
import tomato from "../assets/tomato.jpg";
import potato from "../assets/potato.jpg";
import onion from "../assets/onion.jpg";
import wheat from "../assets/Wheat.jfif";
import contactfarmer from "../assets/contactfarmer.jpg";
import styles from "./CustomerDashboard.module.css";

function CustomerDashboard({ setSelectedPage }) {
  const slides = [
    { title: "Most Selling Crop", text: "🌾 Rice — Top-selling crop this week!", img: mostselling },
    { title: "Cheapest Crop", text: "💵 Wheat — ₹1,920/quintal today!", img: cheapest },
    { title: "Newest Crop on Sale", text: "🆕 Fresh Maize added today!", img: newcrop },
  ];

  const [currentSlide, setCurrentSlide] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setCurrentSlide(prev => (prev + 1) % slides.length), 3000);
    return () => clearInterval(timer);
  }, [slides.length]);

  return (
    <div className={styles.dashboardContainer}>
      <h1 className={styles.dashboardTitle}>Dashboard</h1>

      {/* Banner Slider */}
      <div className={styles.newsSection}>
        <div className={styles.newsImage}>
          <img src={slides[currentSlide].img} alt="slide" />
        </div>
        <div className={styles.newsContent}>
          <h3>{slides[currentSlide].title}</h3>
          <p>{slides[currentSlide].text}</p>
        </div>
      </div>

      {/* Shop + Cart */}
      <div className={styles.infoBoxGrid}>
        {[{img: shop, title:"Shop Now", link:"Shop"}, {img: cart, title:"See Cart", link:"Cart"}].map((box, idx) => (
          <div className={styles.infoBox} key={idx}>
            <img src={box.img} alt={box.title} />
            <div className={styles.infoText}>
              <h4>{box.title}</h4>
              <p onClick={() => setSelectedPage(box.link)}>Go →</p>
            </div>
          </div>
        ))}
      </div>

      {/* Offers Slider */}
      <h2 className={styles.sectionTitle}>🌟 Crops on Special Offer</h2>
      <div className={styles.offersSlider}>
        <div className={styles.offersTrack}>
          {[
            { name: "Tomato", img: tomato, offer: "15% off" },
            { name: "Potato", img: potato, offer: "10% off" },
            { name: "Onion", img: onion, offer: "20% off" },
            { name: "Wheat", img: wheat, offer: "5% off" },
          ].map((item, index) => (
            <div className={styles.offerCard} key={index}>
              <img src={item.img} alt={item.name} />
              <h4>{item.name}</h4>
              <p>{item.offer}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Contact Farmer 
      <h2 className={styles.sectionTitle}>📞 Contact Farmer</h2>
      <div className={styles.contactBox}>
        <img src={contactfarmer} alt="Farmer Contact" />
        <div className={styles.infoText}>
          <h4>Reach Verified Farmers</h4>
          <a href="/contact-farmer">Contact Now →</a>
        </div>
      </div>*/}
    </div>
  );
}

export default CustomerDashboard;