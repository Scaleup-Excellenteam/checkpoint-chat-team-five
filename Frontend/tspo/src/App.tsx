import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import MainPage from "./pages/mainpage";
import GeneralRoom from "./pages/generalroom";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/general" element={<GeneralRoom />} />
      </Routes>
    </Router>
  );
}

export default App;
