import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Sparkles, 
  Mail, 
  Clipboard, 
  CheckCircle, 
  Zap, 
  Settings2,
  FileText,
  AlertCircle,
  Loader2,
  Globe
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './App.css';
import Preloader from './components/Preloader';

interface Profile {
  content_type: string;
  tone: string;
  audience: string;
}

const App: React.FC = () => {
  const [query, setQuery] = useState('');
  const [email, setEmail] = useState('');
  const [sendEmail, setSendEmail] = useState(false);
  const [profile, setProfile] = useState<Profile>({
    content_type: 'Blog',
    tone: 'professional',
    audience: 'general'
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState('');
  const [status, setStatus] = useState<{ msg: string; type: 'success' | 'error' | null }>({ msg: '', type: null });
  const [isAppLoaded, setIsAppLoaded] = useState(false);
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
  const resultRef = useRef<HTMLTextAreaElement>(null);

  const loadingMessages = [
    'Consulting Neural Core...',
    'Fetching Web Sources...',
    'Synthesizing Multi-Agent Insights...',
    'Optimizing RAG Pipeline...',
    'Aggregating Peer Reviews...',
    'Finalizing Knowledge Draft...'
  ];

  useEffect(() => {
    let interval: any;
    if (loading) {
      interval = setInterval(() => {
        setLoadingMessageIndex(prev => (prev + 1) % loadingMessages.length);
      }, 2000);
    } else {
      setLoadingMessageIndex(0);
    }
    return () => clearInterval(interval);
  }, [loading]);

  const showStatus = (msg: string, type: 'success' | 'error') => {
    setStatus({ msg, type });
    setTimeout(() => setStatus({ msg: '', type: null }), 5000);
  };

  const handleRunTask = async () => {
    if (!query.trim()) {
      showStatus("Please enter a research topic or request.", "error");
      return;
    }

    if (sendEmail && !email) {
      showStatus("Please provide an email address for delivery.", "error");
      return;
    }

    setLoading(true);
    setResult('');
    
    try {
      const apiBase = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiBase}/run-task`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          content: query, 
          profile: profile,
          email: email, 
          send_email: sendEmail,
          super_agent: true
        })
      });

      const data = await response.json();

      if (response.ok) {
        setResult(data.message);
        showStatus("Synthesized successfully!", "success");
      } else {
        showStatus("Error: " + data.message, "error");
      }
    } catch (error) {
      showStatus("Connection to AI engine failed.", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleSendEmail = async () => {
    if (!email) {
      showStatus("Enter email address first.", "error");
      return;
    }

    showStatus("Sending to inbox...", "success");
    try {
      const apiBase = import.meta.env.VITE_API_URL || '';
      const response = await fetch(`${apiBase}/send-edited-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: result, email: email })
      });
      if (response.ok) showStatus("Delivered successfully!", "success");
      else showStatus("Failed to send email.", "error");
    } catch(e) {
      showStatus("Delivery failed.", "error");
    }
  };

  const copyToClipboard = () => {
    if (resultRef.current) {
      resultRef.current.select();
      navigator.clipboard.writeText(result);
      showStatus("Content copied!", "success");
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { duration: 0.5, staggerChildren: 0.1 } }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <>
      <AnimatePresence>
        {!isAppLoaded && (
          <motion.div 
            key="preloader"
            initial={{ opacity: 1 }}
            exit={{ opacity: 0, scale: 1.05 }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
            style={{ position: 'fixed', inset: 0, zIndex: 10000 }}
          >
            <Preloader onComplete={() => setIsAppLoaded(true)} />
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div 
        className={`app-container ${!isAppLoaded ? 'hidden-opacity' : ''}`}
        initial={{ opacity: 0 }}
        animate={{ opacity: isAppLoaded ? 1 : 0 }}
        transition={{ duration: 1, delay: 0.2 }}
      >
        {/* Main Content Area */}
        <main className="main-content-fluid">
          <div className="page-header">
            <motion.h1 
              className="hero-title"
              initial={{ y: -20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              What should we research today?
            </motion.h1>
            <motion.p 
              className="hero-subtitle"
              initial={{ y: -10, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.6 }}
            >
              Powered by autonomous agents and real-time RAG pipeline.
            </motion.p>
          </div>

          <div className="workspace-container">
            {/* Input & Config Section */}
            <motion.div 
              className="central-panel"
              initial="hidden"
              animate="visible"
              variants={containerVariants}
            >
              <motion.div className="glass-morphism search-card" variants={itemVariants}>
                <div className="search-header">
                   <div className="badge-group">
                      <div className="badge-pill pulse">
                        <span className="dot"></span>
                        Neural Engine Active
                      </div>
                      <div className="badge-pill outline">GPT-4o + RAG</div>
                   </div>
                </div>
                
                <div className="search-input-wrapper">
                  <textarea 
                    placeholder="Describe your research topic or ask a complex question..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="hero-input"
                  />
                  <div className="search-controls">
                    <div className="control-left">
                       <button className="control-btn" title="Add source"><Globe size={16} /></button>
                       <button className="control-btn" title="Analyze file"><FileText size={16} /></button>
                    </div>
                    <motion.button 
                      className="send-btn"
                      onClick={handleRunTask}
                      disabled={loading}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      {loading ? <Loader2 className="animate-spin" size={20} /> : <Zap size={20} fill="#fff" />}
                    </motion.button>
                  </div>
                </div>
              </motion.div>

              {/* Quick Config Row */}
              <motion.div className="quick-config-row" variants={itemVariants}>
                <div className="config-item glass-morphism">
                   <Settings2 size={16} className="text-secondary" />
                   <select 
                      value={profile.content_type} 
                      onChange={(e) => setProfile({...profile, content_type: e.target.value})}
                      className="minimal-select"
                    >
                      <option value="Blog">Blog Post</option>
                      <option value="Report">Research Report</option>
                      <option value="LinkedIn">LinkedIn</option>
                      <option value="Technical">Technical Doc</option>
                    </select>
                </div>

                <div className="config-item glass-morphism">
                   <Zap size={16} className="text-primary" />
                   <select 
                      value={profile.tone} 
                      onChange={(e) => setProfile({...profile, tone: e.target.value})}
                      className="minimal-select"
                    >
                      <option value="professional">Professional</option>
                      <option value="casual">Casual</option>
                      <option value="technical">Technical</option>
                    </select>
                </div>

                <div className="config-item glass-morphism email-toggle" onClick={() => setSendEmail(!sendEmail)}>
                   <Mail size={16} className={sendEmail ? 'text-primary' : 'text-muted'} />
                   <span>{sendEmail ? (email || 'Email Ready') : 'Delivery Off'}</span>
                </div>
              </motion.div>

              {sendEmail && (
                <motion.div 
                  className="floating-email-input glass-morphism"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                >
                  <input 
                    type="email" 
                    placeholder="Enter your email for delivery..."
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="minimal-input"
                  />
                </motion.div>
              )}
            </motion.div>

            {/* Results Section - Shows below or integrated */}
            <div className="results-container-fluid">
              <AnimatePresence mode="wait">
                {result ? (
                  <motion.div 
                    className="glass-morphism showcase-card"
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    key="result"
                  >
                    <div className="showcase-header">
                      <div className="title-area">
                        <Sparkles className="text-secondary" size={20} />
                        <h3>Synthesized Content</h3>
                      </div>
                      <div className="action-row">
                        <button className="action-pill" onClick={copyToClipboard}>
                          <Clipboard size={14} />
                          <span>Copy</span>
                        </button>
                        <button className="action-pill primary" onClick={handleSendEmail}>
                          <Send size={14} />
                          <span>Email Me</span>
                        </button>
                      </div>
                    </div>
                    <div className="content-view">
                      <textarea 
                        ref={resultRef}
                        value={result}
                        onChange={(e) => setResult(e.target.value)}
                        className="premium-editor"
                      />
                    </div>
                    <div className="content-footer">
                      <div className="meta-info">
                        <div className="ai-tag">Generated by BharathAI Pro</div>
                        <span>•</span>
                        <div className="time-tag">Just now</div>
                      </div>
                    </div>
                  </motion.div>
                ) : (
                  !loading && (
                    <motion.div 
                      className="suggestions-grid"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.8 }}
                    >
                      <div className="suggestion-item glass-morphism" onClick={() => setQuery("Recent breakthroughs in sustainable energy")}>
                        <Globe size={14} />
                        <span>Sustainability Trends</span>
                      </div>
                      <div className="suggestion-item glass-morphism" onClick={() => setQuery("Market analysis of AI in healthcare 2024")}>
                        <FileText size={14} />
                        <span>AI Healthcare Report</span>
                      </div>
                      <div className="suggestion-item glass-morphism" onClick={() => setQuery("Explain quantum entanglement for high schoolers")}>
                        <Sparkles size={14} />
                        <span>Quantum Physics</span>
                      </div>
                    </motion.div>
                  )
                )}
              </AnimatePresence>

              {loading && (
                <motion.div 
                  className="loading-state-orchestrator"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 1.1 }}
                >
                   <div className="loading-visual-container">
                      <div className="loading-glow"></div>
                      <div className="ripple-ring"></div>
                      <div className="ripple-ring delay-1"></div>
                      <div className="ripple-ring delay-2"></div>
                      <Loader2 size={64} className="animate-spin text-primary-glow-icon" />
                   </div>
                   <motion.div 
                     className="loading-info"
                     key={loadingMessageIndex}
                     initial={{ y: 10, opacity: 0 }}
                     animate={{ y: 0, opacity: 1 }}
                   >
                     <h3>
                       {query.length > 20 ? `Analyzing "${query.substring(0, 20)}..."` : `Researching ${query}`}
                     </h3>
                     <p className="cycling-status">
                       {loadingMessages[loadingMessageIndex]}
                     </p>
                   </motion.div>
                </motion.div>
              )}
            </div>
          </div>
        </main>

        {/* Status Notifications */}
        <AnimatePresence>
          {status.msg && (
            <motion.div 
              className={`status-notification ${status.type}`}
              initial={{ opacity: 0, y: 50, x: '-50%' }}
              animate={{ opacity: 1, y: 0, x: '-50%' }}
              exit={{ opacity: 0, y: 50, x: '-50%' }}
              style={{ left: '50%' }}
            >
              {status.type === 'success' ? <CheckCircle size={20} /> : <AlertCircle size={20} />}
              <span>{status.msg}</span>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </>
  );
};

export default App;
