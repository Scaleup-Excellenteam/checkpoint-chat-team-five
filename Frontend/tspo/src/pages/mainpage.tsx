import pizzaLogo from "../assets/pizza.webp";
import "../App.css";

function MainPage() {
  return (
    <>
      <div>
        <img src={pizzaLogo} className="logo pizza" alt="Pizza logo" />
      </div>
      <h1>Top Secret Pizza Lovers Organization</h1>
      <div className="card">
        <button>Login</button>
        <button>Register</button>
      </div>
    </>
  );
}

export default MainPage;
