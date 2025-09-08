import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button, Input, Card } from "../components";
import { API_BASE_URL } from "../lib/api";
import "../App.css";

function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      localStorage.removeItem("tspo_session");
      const res = await fetch(`${API_BASE_URL}/users/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
        }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Login failed (${res.status})`);
      }
      const user = await res.json();
      localStorage.setItem(
        "tspo_session",
        JSON.stringify({ email: user.email, full_name: user.full_name })
      );
      navigate("/general");
    } catch (err) {
      alert((err as Error).message || "Network error: failed to reach server");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-container">
      <Card variant="elevated" className="auth-card">
        <h1>Login</h1>
        <form onSubmit={handleSubmit} className="auth-form">
          <Input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            label="Email"
            placeholder="Enter your email"
            required
            className="input"
          />
          <Input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            label="Password"
            placeholder="Enter your password"
            required
            className="input"
          />
          <Button
            type="submit"
            variant="primary"
            size="large"
            className="auth-button"
            disabled={submitting}
          >
            Login
          </Button>
        </form>
        <p className="auth-link">
          Don't have an account? <Link to="/register">Register here</Link>
        </p>
        <p className="auth-link">
          <Link to="/">← Back to Home</Link>
        </p>
      </Card>
    </div>
  );
}

export default Login;
