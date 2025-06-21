import React, { useState, useRef, useEffect } from 'react';
import { ItineraryData } from '@/types/components/Itinerary';
import './ItineraryEditor.css';

interface Message {
  id: string;
  text: string;
  type: 'user' | 'system';
  timestamp: Date;
}

interface ItineraryEditorProps {
  isLoading: boolean;
  onUpdate: (userRequest: string) => Promise<ItineraryData>;
}

const SMART_SUGGESTIONS = [
  'Add more local food experiences',
  'Include cultural activities',
  'Make it more relaxed',
  'Add shopping spots',
  'Optimize travel times'
];

export const ItineraryEditor: React.FC<ItineraryEditorProps> = ({ isLoading: externalLoading, onUpdate }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (text: string) => {
    if (!text.trim() || isUpdating || externalLoading) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      text: text.trim(),
      type: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, newMessage]);
    setInputValue('');
    setIsUpdating(true);

    try {
      await onUpdate(text);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        text: 'Itinerary updated successfully!',
        type: 'system',
        timestamp: new Date()
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        text: 'Failed to update itinerary. Please try again.',
        type: 'system',
        timestamp: new Date()
      }]);
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className={`itinerary-editor ${isOpen ? 'open' : ''}`}>
      <button 
        className="itinerary-editor__toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? 'Close editor' : 'Open editor'}
      >
        {isOpen ? '✕' : '✎'}
      </button>

      <div className="itinerary-editor__content">
        <div className="itinerary-editor__header">
          <h3>Refine Your Itinerary</h3>
        </div>

        <div className="itinerary-editor__messages">
          {messages.map(message => (
            <div 
              key={message.id}
              className={`itinerary-editor__message ${message.type}`}
            >
              {message.text}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <div className="itinerary-editor__suggestions">
          {SMART_SUGGESTIONS.map(suggestion => (
            <button
              key={suggestion}
              className="itinerary-editor__suggestion"
              onClick={() => handleSubmit(suggestion)}
              disabled={isUpdating || externalLoading}
            >
              {suggestion}
            </button>
          ))}
        </div>

        <div className="itinerary-editor__input">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="How would you like to modify your itinerary?"
            onKeyPress={(e) => e.key === 'Enter' && handleSubmit(inputValue)}
            disabled={isUpdating || externalLoading}
          />
          <button
            className="itinerary-editor__send-button"
            onClick={() => handleSubmit(inputValue)}
            disabled={isUpdating || externalLoading || !inputValue.trim()}
          >
            →
          </button>
        </div>
      </div>
    </div>
  );
};