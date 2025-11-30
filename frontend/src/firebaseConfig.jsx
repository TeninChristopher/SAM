// src/firebaseConfig.js
import { initializeApp } from "firebase/app";
import { getDatabase } from "firebase/database";

// ⬇️ Use the firebaseConfig object from Firebase console (Project settings → Your apps → Web)
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  databaseURL: "https://farmersensorproject-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "XXXXXXX",
  appId: "1:XXXXXXX:web:YYYYYYYY"
};

const app = initializeApp(firebaseConfig);
export const db = getDatabase(app);