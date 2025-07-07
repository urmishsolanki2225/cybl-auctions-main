import { useState, useEffect } from "react";

const SmallTimer = ({ endTime }) => {
  const [timeLeft, setTimeLeft] = useState("");

  useEffect(() => {
    const updateTimer = () => {
      const end = new Date(endTime);
      const now = new Date();
      const diff = end - now;

      if (diff <= 0) {
        setTimeLeft("Time expired");
        return;
      }

      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
      const minutes = Math.floor((diff / (1000 * 60)) % 60);
      const seconds = Math.floor((diff / 1000) % 60);

      setTimeLeft(
        `${days}d ${hours}h ${minutes}m ${seconds}s`
      );
    };

    updateTimer(); // initial call
    const intervalId = setInterval(updateTimer, 1000);
    return () => clearInterval(intervalId);
  }, [endTime]);

  return <div className="timer-text">{timeLeft}</div>;
};

export default SmallTimer;
