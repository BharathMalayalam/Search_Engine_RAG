import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './Preloader.css';

interface PreloaderProps {
  onComplete: () => void;
}

const Preloader: React.FC<PreloaderProps> = ({ onComplete }) => {
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState(1);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTimeout(() => setStage(2), 500);
          setTimeout(onComplete, 2500);
          return 100;
        }
        return prev + 1;
      });
    }, 15);

    return () => clearInterval(interval);
  }, [onComplete]);

  return (
    <div className="preloader-overlay">
      <motion.div 
        className="scan-line"
        animate={{ top: ['0%', '100%', '0%'] }}
        transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
      />

      <AnimatePresence>
        {stage === 1 && (
          <motion.div 
            className="robot-content"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.1, filter: 'blur(10px)' }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <div className="robot-container">
              <motion.div 
                className="robot-glow"
                animate={{ 
                  scale: [1, 1.2, 1],
                  opacity: [0.5, 0.8, 0.5]
                }}
                transition={{ duration: 2, repeat: Infinity }}
              />
              <motion.img 
                src="/images/robot.png" 
                alt="Robot Intro" 
                style={{ width: '100%', height: '100%', objectFit: 'contain', borderRadius: '50%' }}
                animate={{ y: [0, -10, 0] }}
                transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
              />
            </div>

            <div className="loading-text-container">
              <motion.h1 
                className="loading-title"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                Bharath AI
              </motion.h1>
              <motion.p 
                className="loading-subtitle"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                Initializing Neural Brain... {progress}%
              </motion.p>
              
              <div className="progress-bar-container">
                <motion.div 
                  className="progress-bar-fill"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          </motion.div>
        )}

        {stage === 2 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="loading-text-container"
          >
            <motion.h2 
              className="loading-title"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5 }}
            >
              System Ready
            </motion.h2>
            <motion.p 
              className="loading-subtitle"
              animate={{ opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              Establishing Secure Connection...
            </motion.p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Preloader;
