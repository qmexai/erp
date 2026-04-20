import {initializeApp} from "firebase/app";
import {getAuth} from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyCnKbwDca0MT-fuS0UKC8dcbO10_hRpu1o",
  authDomain: "qmexaierp.firebaseapp.com",
  projectId: "qmexaierp",
  storageBucket: "qmexaierp.firebasestorage.app",
  messagingSenderId: "481955202418",
  appId: "1:481955202418:web:cb3a25e058770f31a989eb",
  measurementId: "G-ZNPF0NRTHV"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
// const analytics = getAnalytics(app);

export const auth = getAuth(app);

export default app;