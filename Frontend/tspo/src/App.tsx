import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import MainPage from "./pages/mainpage";
import Login from "./pages/login";
import Register from "./pages/register";
import GeneralRoom from "./pages/generalroom";
import Logout from "./pages/logout.tsx";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/general" element={<GeneralRoom />} />
        <Route path="/logout" element={<Logout />} />
      </Routes>
    </Router>
  );
}

export default App;
