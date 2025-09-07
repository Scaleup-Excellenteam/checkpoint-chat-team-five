import { useState } from "react";
import { Link } from "react-router-dom";
import { Button, Input, Card } from "../components";
import "../App.css";

function Register() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      alert("Passwords don't match!");
      return;
    }

    // TODO: Implement registration logic
    console.log("Registration attempt:", formData);
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
          />
          <Input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            label="Email"
            placeholder="Enter your email"
            required
          />
          <Input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            label="Password"
            placeholder="Create a password"
            required
          />
          <Input
            type="password"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            label="Confirm Password"
            placeholder="Confirm your password"
            required
          />
          <Button
            type="submit"
            variant="primary"
            size="large"
            className="auth-button"
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
