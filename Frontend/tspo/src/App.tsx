import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import MainPage from "./pages/mainpage";
import Login from "./pages/login";
import Register from "./pages/register";
import GeneralRoom from "./pages/generalroom";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/general" element={<GeneralRoom />} />
      </Routes>
    </Router>
  );
}

export default App;
