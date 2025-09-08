import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button, Input, Card } from "../components";
import { API_BASE_URL } from "../lib/api";
import "../App.css";

function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
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

    if (formData.password !== formData.confirmPassword) {
      alert("Passwords don't match!");
      return;
    }

    setSubmitting(true);
    try {
      localStorage.removeItem("tspo_session");
      const res = await fetch(`${API_BASE_URL}/users/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: formData.email,
          full_name: formData.username,
          password: formData.password,
        }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Register failed (${res.status})`);
      }
      navigate("/login");
    } catch (err) {
      alert((err as Error).message || "Network error: failed to reach server");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-container">
      <Card variant="elevated" className="auth-card">
        <h1>Register</h1>
        <form onSubmit={handleSubmit} className="auth-form">
          <Input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            label="Username"
            placeholder="Choose a username"
            required
            className="input"
          />
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
            placeholder="Create a password"
            required
            className="input"
          />
          <Input
            type="password"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            label="Confirm Password"
            placeholder="Confirm your password"
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
            Register
          </Button>
        </form>
        <p className="auth-link">
          Already have an account? <Link to="/login">Login here</Link>
        </p>
        <p className="auth-link">
          <Link to="/">← Back to Home</Link>
        </p>
      </Card>
    </div>
  );
}

export default Register;
