import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Register.css";

function Register() {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(false);

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    role: "",
  });

  const [message, setMessage] = useState("");

  const handleChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  // =============================
  // SIGNUP
  // =============================
  const handleSignup = async () => {
    setMessage("");

    if (!formData.name || !formData.email || !formData.password || !formData.role) {
      setMessage("⚠️ Please fill out all fields.");
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/users/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok) {
        setMessage("❌ Registration failed: " + JSON.stringify(data));
        return;
      }

      // Save user in localStorage
      localStorage.setItem("user_id", data.user_id);
      localStorage.setItem("userType", data.role);
      localStorage.setItem("email", data.email);

      setMessage("✅ User registered successfully!");

      navigate("/mainpage");

      // Reset form
      setFormData({ name: "", email: "", password: "", role: "" });

    } catch (err) {
      setMessage("🚫 Network error — check if Django is running.");
    }
  };


  // =============================
  // LOGIN
  // =============================
  const handleLogin = async () => {
    setMessage("");

    if (!formData.email || !formData.password) {
      setMessage("⚠️ Please enter email and password.");
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setMessage(`❌ ${data.error || "Login failed"}`);
        return;
      }

      // Store logged-in user details
      localStorage.setItem("user_id", data.user.user_id);
      localStorage.setItem("userType", data.user.role);
      localStorage.setItem("email", data.user.email);

      setMessage("✅ Login successful!");

      navigate("/mainpage");

    } catch (err) {
      setMessage("🚫 Network error — check if Django is running.");
    }
  };

  return (
    <div className="register-page">
      <header className="overlay">Smart Agri-Market Connect (SAMS)</header>

      <div className="form-container">
        <div className={`forms-wrapper ${isLogin ? "show-login" : "show-signup"}`}>
          
          {/* SIGNUP FORM */}
          <div className="form-box signup-box">
            <h2>Create Account</h2>

            <div className="input-group">
              <label>Name</label>
              <input
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Enter full name"
              />
            </div>

            <div className="input-group">
              <label>Email</label>
              <input
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="example@gmail.com"
              />
            </div>

            <div className="input-group">
              <label>Password</label>
              <input
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
              />
            </div>

            <div className="input-group">
              <label>Register As</label>
              <select name="role" value={formData.role} onChange={handleChange}>
                <option value="">Select role</option>
                <option value="customer">Customer</option>
                <option value="farmer">Farmer</option>
              </select>
            </div>

            <button onClick={handleSignup} className="action-btn">
              Sign Up
            </button>

            <p className="toggle-text">
              Already have an account?{" "}
              <span onClick={() => setIsLogin(true)}>Log In</span>
            </p>
          </div>

          {/* LOGIN FORM */}
          <div className="form-box login-box">
            <h2>Welcome Back</h2>

            <div className="input-group">
              <label>Email</label>
              <input
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="example@gmail.com"
              />
            </div>

            <div className="input-group">
              <label>Password</label>
              <input
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
              />
            </div>

            <button onClick={handleLogin} className="action-btn">
              Log In
            </button>

            <p className="toggle-text">
              New here? <span onClick={() => setIsLogin(false)}>Sign Up</span>
            </p>
          </div>
        </div>

        {message && <div className="form-message">{message}</div>}
      </div>
    </div>
  );
}

export default Register;