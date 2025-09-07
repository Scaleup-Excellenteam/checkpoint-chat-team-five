import type { ChangeEvent, KeyboardEvent } from "react";

interface InputProps {
  type?: "text" | "email" | "password" | "number";
  value: string;
  onChange: (e: ChangeEvent<HTMLInputElement>) => void;
  onKeyDown?: (e: KeyboardEvent<HTMLInputElement>) => void;
  placeholder?: string;
  label?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
  id?: string;
  name?: string;
}

function Input({
  type = "text",
  value,
  onChange,
  onKeyDown,
  placeholder,
  label,
  required = false,
  disabled = false,
  className = "",
  id,
  name,
}: InputProps) {
  const inputId = id || name;

  return (
    <div className="input-group">
      {label && (
        <label htmlFor={inputId} className="input-label">
          {label}
        </label>
      )}
      <input
        type={type}
        id={inputId}
        name={name}
        value={value}
        onChange={onChange}
        onKeyDown={onKeyDown}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        className={`input ${className}`.trim()}
      />
    </div>
  );
}

export default Input;
