import React, { useState, useEffect } from "react";
import "./Weather.css";

const Weather = () => {
  const [current, setCurrent] = useState({});
  const [daily, setDaily] = useState([]);

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/weather/");
        const data = await res.json();

        setCurrent({
          temp: data.current_weather.temperature,
          cloudcover: data.current_weather.cloudcover,
          precipitation: data.current_weather.precipitation,
          date: data.current_weather.date
        });

        setDaily(data.next_7_days.map(d => ({
          day: new Date(d.date).toLocaleDateString("en-US", { weekday: "short" }),
          temperature: d.temperature,
          cloudcover: d.cloudcover,
          precipitation: d.precipitation < 0 ? 0.0 : d.precipitation
        })));
        console.log(setDaily)
      } catch (error) {
        console.error("Error fetching weather:", error);
      }
    };

    fetchWeather();
  }, []);

  return (
    <div className="weather-page">
      <h1 className="weather-title">Weather Overview</h1>

      {/* Current Weather */}
      <div className="weather-current">
        <div className="weather-main-info">
          <h2>{current.temp}°C</h2>
          <p>Cloudcover: {current.cloudcover}%</p>
          <p>Precipitation: {current.precipitation}mm</p>
        </div>
      </div>

      {/* Forecast */}
      <h2 className="forecast-title">📅 7-Day Forecast</h2>
      <div className="forecast-grid">
        {daily.map((day, index) => (
          <div key={index} className="forecast-card">
            <h3>{day.day}</h3>
            <p>Temp: {day.temperature}°C</p>
            <p>Cloud: {day.cloudcover}%</p>
            <p>Rain: {day.precipitation}mm</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Weather;

  /* 
  -------------------------------------------------------------------
  🧭 TO ENABLE REAL WEATHER DATA:
  1️⃣ Get your free API key from https://openweathermap.org/api
  2️⃣ Uncomment this entire useEffect block
  3️⃣ Optionally, replace `lat` and `lon` with the user’s coordinates
  -------------------------------------------------------------------

  useEffect(() => {
    const API_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b";
    const lat = 13.0827; // Example: Chennai
    const lon = 80.2707;

    const fetchWeather = async () => {
      try {
        const url = `https://api.openweathermap.org/data/2.5/onecall?lat=${lat}&lon=${lon}&exclude=minutely,hourly,alerts&units=metric&appid=${API_KEY}`;
        const res = await fetch(url);
        const data = await res.json();

        // 🌡️ Update current weather
        setCurrent({
          temp: data.current.temp,
          feels_like: data.current.feels_like,
          description: data.current.weather[0].description,
          humidity: data.current.humidity,
          wind_speed: data.current.wind_speed,
        });

        // 📅 Update 7-day forecast
        const week = data.daily.slice(0, 7).map((d) => ({
          day: new Date(d.dt * 1000).toLocaleDateString("en-US", {
            weekday: "short",
          }),
          description: d.weather[0].main,
          min: Math.round(d.temp.min),
          max: Math.round(d.temp.max),
        }));

        setDaily(week);
      } catch (error) {
        console.error("⚠️ Error fetching weather:", error);
      }
    };

    fetchWeather();
  }, []);
  */


/*import React, { useState, useEffect } from "react";
import "./Weather.css";

const Weather = () => {
  const [current, setCurrent] = useState({
    temp: "--",
    feels_like: "--",
    description: "--",
    humidity: "--",
    wind_speed: "--",
  });

  const [daily, setDaily] = useState([]);

  const [error, setError] = useState("");

  useEffect(() => {
    const API_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"; // <-- Replace with your own key

    const fetchWeather = async (lat, lon) => {
      try {
        const url = `https://api.openweathermap.org/data/2.5/onecall?lat=${lat}&lon=${lon}&exclude=minutely,hourly,alerts&units=metric&appid=${API_KEY}`;
        const res = await fetch(url);
        const data = await res.json();

        setCurrent({
          temp: data.current.temp,
          feels_like: data.current.feels_like,
          description: data.current.weather[0].description,
          humidity: data.current.humidity,
          wind_speed: data.current.wind_speed,
        });

        const week = data.daily.slice(0, 7).map((d) => ({
          day: new Date(d.dt * 1000).toLocaleDateString("en-US", { weekday: "short" }),
          description: d.weather[0].main,
          min: Math.round(d.temp.min),
          max: Math.round(d.temp.max),
        }));

        setDaily(week);
      } catch (err) {
        console.error("⚠️ Error fetching weather:", err);
        setError("Failed to fetch weather data.");
      }
    };

    // Get user's geolocation
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          fetchWeather(latitude, longitude);
        },
        (err) => {
          console.error("⚠️ Geolocation error:", err);
          setError("Location access denied. Using default location.");
          // Fallback: use Chennai
          fetchWeather(13.0827, 80.2707);
        }
      );
    } else {
      setError("Geolocation not supported by browser. Using default location.");
      fetchWeather(13.0827, 80.2707);
    }
  }, []);

  return (
    <div className="weather-page">
      <h1 className="weather-title">🌦️ Weather Overview</h1>

      {error && <p className="weather-error">{error}</p>}

      <div className="weather-current">
        <div className="weather-main-info">
          <h2>{current.temp}°C</h2>
          <p>{current.description}</p>
        </div>

        <div className="weather-details">
          <p><strong>Feels like:</strong> {current.feels_like}°C</p>
          <p><strong>Humidity:</strong> {current.humidity}%</p>
          <p><strong>Wind Speed:</strong> {current.wind_speed} m/s</p>
        </div>
      </div>

      <h2 className="forecast-title">📅 7-Day Forecast</h2>
      <div className="forecast-grid">
        {daily.map((day, index) => (
          <div key={index} className="forecast-card">
            <h3>{day.day}</h3>
            <p className="forecast-desc">{day.description}</p>
            <div className="forecast-temp">
              <span className="min">{day.min}°C</span>
              <span className="max">{day.max}°C</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Weather;*/