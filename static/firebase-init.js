var firebaseConfig = {
  apiKey: "AIzaSyAiacOv6e4ZNyCdKQh4chFYPYWI4XB-Jsk",
  authDomain: "thesis-system-3e86e.firebaseapp.com",
  databaseURL: "https://thesis-system-3e86e-default-rtdb.firebaseio.com",
  projectId: "thesis-system-3e86e",
  storageBucket: "thesis-system-3e86e.appspot.com",
  messagingSenderId: "806009555938",
  appId: "1:806009555938:web:eb1dd158748a6b630447bb",
};
firebase.initializeApp(firebaseConfig);

// Initialize Firebase
const auth = firebase.auth();
const db = firebase.firestore();
const storage = firebase.storage();
console.log("firebase initialized");

db.settings({ timestampsInSnapshots: true });
