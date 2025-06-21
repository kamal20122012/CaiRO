import React from 'react';
import './Loader.css';

interface LoaderProps {
  text: string;
}

export const Loader: React.FC<LoaderProps> = ({ text }) => {
  return (
    <div className="loader">
      <div className="loader__spinner"></div>
      <p className="loader__text">{text}</p>
    </div>
  );
};