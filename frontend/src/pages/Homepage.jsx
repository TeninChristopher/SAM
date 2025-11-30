import React from "react";
import "./Homepage.css";
import { useNavigate } from "react-router-dom";
import farmerImg1 from "../assets/farmer-img-1.jpg";
import farmerImg2 from "../assets/farmer-img-2.1.jpg";
import farmerImg3 from "../assets/farmer-img-3.jpg";

function Homepage() {
  const navigate = useNavigate();
  const handleLogin = () => {
    // after validation, redirect to farmer dashboard
    navigate("/register");
  };
  return (
    <div className="main">
      <div className="overlay-1">
        <div className="overlay-1-title">Smart Agri-Market Connect (SAMS)</div>
        <div className="overlay-1-user">
          <div className="overlay-1-loginbox" onClick={handleLogin}>Login</div>
          <div className="overlay-1-signupbox" onClick={handleLogin}>Sign-Up</div>
        </div>
      </div>

      <div className="part-a">
        <div className="image-flex">

          <div className="image-box img-1">
            <div className="hover-panel">
              <h2>Direct Market Access</h2>
              <p>
              Empowers farmers by connecting them directly with customers, removing middlemen
              and ensuring fair prices. This creates a transparent, efficient, and trusted 
              farmer–customer relationship.
              </p>
              </div>
          </div>

          <div className="image-box img-2">
            <div className="hover-panel">
              <h2>Smart Pricing & Insights</h2>
              <p>
              Provides real-time market trends, price forecasts, and demand analysis so farmers 
              can make informed decisions and maximize their earnings with confidence.
              </p>
            </div>
          </div>

          <div className="image-box img-3">
            <div className="hover-panel">
              <h2>Seamless Buying Experience</h2>
              <p>
              Offers customers an easy, reliable, and transparent platform to purchase 
              fresh produce directly from farmers—ensuring quality, trust, and convenience.
              </p>
            </div>
          </div>

          <div className="title">About Us</div>
        </div>
      </div>

      <div className="divide-column"></div>

      <div className="part-b">
        <div className="contact-container">
          <div className="contact-text">
            <h2>Get in Touch</h2>
            <p>We would love to hear from you! Fill out the form and we will get back to you as soon as possible.</p>
          </div>

          <form className="contact-form" onSubmit={(e) => e.preventDefault()}>
            <input type="text" name="name" placeholder="Your Name" required />
            <input type="email" name="email" placeholder="Your Email" required />
            <textarea name="message" placeholder="Your Message" rows="5" required />
            <button type="submit">Send Message</button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default Homepage;