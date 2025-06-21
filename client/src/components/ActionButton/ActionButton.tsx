import React from 'react';
import './ActionButton.css';

export interface ActionButtonProps {
  label: string;
  icon: string;
  onClick: () => void;
  variant: 'primary' | 'secondary' | 'tertiary' | 'quaternary';
  disabled?: boolean;
}

export const ActionButton: React.FC<ActionButtonProps> = ({
  label,
  icon,
  onClick,
  variant,
  disabled = false
}) => {
  return (
    <button
      className={`action-button action-button--${variant}`}
      onClick={onClick}
      disabled={disabled}
    >
      <span className="action-button__icon">{icon}</span>
      <span className="action-button__label">{label}</span>
    </button>
  );
};