// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDPz8gbt6xAEj6hHB--6EDiwNw-lMPO7Ro",
  authDomain: "carisma-bc876.firebaseapp.com",
  databaseURL: "https://carisma-bc876-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "carisma-bc876",
  storageBucket: "carisma-bc876.appspot.com",
  messagingSenderId: "1011415231473",
  appId: "1:1011415231473:web:6f396b17e692dcc8a4b250",
  measurementId: "G-PW9YTWKXBS"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);