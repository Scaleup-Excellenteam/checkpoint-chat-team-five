import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function Logout() {
  const navigate = useNavigate();

  useEffect(() => {
    try {
      localStorage.removeItem("tspo_session");
    } catch {}
    navigate("/login", { replace: true });
  }, [navigate]);

  return null;
}

export default Logout;
