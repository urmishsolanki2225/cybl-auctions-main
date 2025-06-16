import { useState, useEffect } from 'react';
import './LiveTimer.css';

interface LiveTimerProps {
  endTime: string; // ISO string format
  onTimeUp?: () => void;
  className?: string;
}

interface TimeLeft {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
}

const LiveTimer = ({ endTime, onTimeUp, className = '' }: LiveTimerProps) => {
  const [timeLeft, setTimeLeft] = useState<TimeLeft>({ days: 0, hours: 0, minutes: 0, seconds: 0 });
  const [isExpired, setIsExpired] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date().getTime();
      const end = new Date(endTime).getTime();
      const difference = end - now;

      if (difference > 0) {
        const days = Math.floor(difference / (1000 * 60 * 60 * 24));
        const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((difference % (1000 * 60)) / 1000);

        setTimeLeft({ days, hours, minutes, seconds });
      } else {
        setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0 });
        setIsExpired(true);
        if (onTimeUp) {
          onTimeUp();
        }
        clearInterval(timer);
      }
    }, 1000);

    return () => clearInterval(timer);
  }, [endTime, onTimeUp]);

  if (isExpired) {
    return (
      <div className={`live-timer expired ${className}`}>
        <span className="timer-expired">Auction Ended</span>
      </div>
    );
  }

  return (
    <div className={`live-timer ${className}`}>
      <div className="timer-container">
        <div className="timer-unit">
          <span className="timer-number">{timeLeft.days.toString().padStart(2, '0')}</span>
          <span className="timer-label">Days</span>
        </div>
        <div className="timer-separator">:</div>
        <div className="timer-unit">
          <span className="timer-number">{timeLeft.hours.toString().padStart(2, '0')}</span>
          <span className="timer-label">Hours</span>
        </div>
        <div className="timer-separator">:</div>
        <div className="timer-unit">
          <span className="timer-number">{timeLeft.minutes.toString().padStart(2, '0')}</span>
          <span className="timer-label">Minutes</span>
        </div>
        <div className="timer-separator">:</div>
        <div className="timer-unit">
          <span className="timer-number">{timeLeft.seconds.toString().padStart(2, '0')}</span>
          <span className="timer-label">Seconds</span>
        </div>
      </div>
    </div>
  );
};

export default LiveTimer;