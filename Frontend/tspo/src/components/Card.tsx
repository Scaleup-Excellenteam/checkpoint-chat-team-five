import { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
  variant?: "default" | "elevated" | "outlined";
}

function Card({ children, className = "", variant = "default" }: CardProps) {
  const baseClasses = "card-component";
  const variantClasses = {
    default: "card-default",
    elevated: "card-elevated",
    outlined: "card-outlined",
  };

  const classes =
    `${baseClasses} ${variantClasses[variant]} ${className}`.trim();

  return <div className={classes}>{children}</div>;
}

export default Card;
