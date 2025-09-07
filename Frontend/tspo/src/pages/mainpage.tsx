import { Link } from "react-router-dom";
import { Button, Card } from "../components";
import pizzaLogo from "../assets/pizza.webp";
import "../App.css";

function MainPage() {
  return (
    <>
      <div>
        <img src={pizzaLogo} className="logo pizza" alt="Pizza logo" />
      </div>
      <h1>Top Secret Pizza Lovers Organization</h1>
      <p className="subtitle">Join the ultimate pizza discussion community</p>
      <div className="card">
        <Link to="/login">
          <Button variant="primary" size="large" className="nav-button">
            Login
          </Button>
        </Link>
        <Link to="/register">
          <Button variant="primary" size="large" className="nav-button">
            Register
          </Button>
        </Link>
      </div>
      <div className="features">
        <Card variant="default" className="feature">
          <h3>🍕 Pizza Discussions</h3>
          <p>Share your favorite pizza recipes and toppings</p>
        </Card>
        <Card variant="default" className="feature">
          <h3>🏆 Pizza Rankings</h3>
          <p>Vote on the best pizza places and styles</p>
        </Card>
        <Card variant="default" className="feature">
          <h3>👥 Community</h3>
          <p>Connect with fellow pizza enthusiasts</p>
        </Card>
      </div>
    </>
  );
}

export default MainPage;
