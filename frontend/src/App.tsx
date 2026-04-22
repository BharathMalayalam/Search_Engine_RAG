import React, { useState, useRef } from 'react';
import { 
  Send, 
  Sparkles, 
  Settings, 
  Mail, 
  History, 
  Clipboard, 
  CheckCircle, 
  Zap, 
  Settings2,
  ChevronDown,
  Monitor,
  BrainCircuit,
  MessageSquare,
  FileText,
  AlertCircle,
  Loader2,
  Globe,
  MoreVertical,
  Code2
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
  const [activeTab, setActiveTab] = useState<'agent' | 'history' | 'settings'>('agent');
  const [showConfig, setShowConfig] = useState(true);
  const [isAppLoaded, setIsAppLoaded] = useState(false);
  const resultRef = useRef<HTMLTextAreaElement>(null);

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
      const response = await fetch('/run-task', {
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
      const response = await fetch('/send-edited-email', {
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
        {/* Sidebar Navigation */}
        <aside className="sidebar glass-morphism">
          <div className="logo-container">
            <div className="logo-icon">
              <Sparkles size={24} className="sparkle-primary" />
            </div>
            <span className="logo-text">Bharath<span className="text-primary-gradient">AI</span></span>
          </div>

          <nav className="sidebar-nav">
            <button 
              className={`nav-item ${activeTab === 'agent' ? 'active' : ''}`}
              onClick={() => setActiveTab('agent')}
            >
              <BrainCircuit size={20} />
              <span>Super Agent</span>
            </button>
            <button 
              className={`nav-item ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => setActiveTab('history')}
            >
              <History size={20} />
              <span>Memory Log</span>
            </button>
            <button 
              className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`}
              onClick={() => setActiveTab('settings')}
            >
              <Settings size={20} />
              <span>Settings</span>
            </button>
          </nav>

          <div className="sidebar-footer">
            <div className="user-profile">
              <div className="user-avatar">B</div>
              <div className="user-info">
                <p className="user-name">Bharath S</p>
                <p className="user-plan">Pro Tier</p>
              </div>
              <MoreVertical size={16} className="text-muted" />
            </div>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="main-content">
          <header className="content-header">
             <div className="header-left">
              <h1 className="gradient-text">
                {activeTab === 'agent' ? 'Cognitive Workspace' : activeTab === 'history' ? 'Neural Memory' : 'System Configuration'}
              </h1>
              <p className="header-subtitle">
                {activeTab === 'agent' ? 'Autonomous Research & Content Generation' : 'Past interactions and learned patterns'}
              </p>
             </div>
             <div className="header-right">
                <button className="icon-btn"><Globe size={18} /></button>
                <button className="icon-btn"><Code2 size={18} /></button>
                <button className="cta-btn secondary">Upgrade</button>
             </div>
          </header>

          <div className="workspace-grid">
            {/* Left Panel: Input & Settings */}
            <motion.div 
              className="input-panel"
              initial="hidden"
              animate="visible"
              variants={containerVariants}
            >
              <motion.div className="glass-morphism card" variants={itemVariants}>
                <div className="card-header">
                  <div className="card-title-group">
                     <MessageSquare className="icon-primary" size={20} />
                     <h3>Research Query</h3>
                  </div>
                  <div className="badge">RAG Active</div>
                </div>
                <div className="textarea-wrapper">
                  <textarea 
                    placeholder="Ask me anything... (e.g., 'Describe the future of quantum computing')"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="main-input"
                  />
                  <div className="input-footer">
                    <span className="char-count">{query.length} characters</span>
                    <div className="input-actions">
                      <button className="icon-btn-small"><Sparkles size={14} /></button>
                      <button className="icon-btn-small"><Monitor size={14} /></button>
                    </div>
                  </div>
                </div>
              </motion.div>

              <motion.div className="glass-morphism card config-card" variants={itemVariants}>
                <div className="card-header clickable" onClick={() => setShowConfig(!showConfig)}>
                  <div className="card-title-group">
                     <Settings2 className="icon-secondary" size={20} />
                     <h3>Agent Personality</h3>
                  </div>
                  <ChevronDown size={18} className={`transition-transform ${showConfig ? 'rotate-180' : ''}`} />
                </div>
                
                <AnimatePresence>
                  {showConfig && (
                    <motion.div 
                      className="config-grid"
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                    >
                      <div className="form-group">
                        <label>Format</label>
                        <select 
                          value={profile.content_type} 
                          onChange={(e) => setProfile({...profile, content_type: e.target.value})}
                        >
                          <option value="Blog">Blog Post</option>
                          <option value="LinkedIn">LinkedIn Update</option>
                          <option value="Instagram">Instagram Caption</option>
                          <option value="Letter">Formal Letter</option>
                          <option value="Report">Research Report</option>
                        </select>
                      </div>
                      <div className="form-group">
                        <label>Tone</label>
                        <select 
                          value={profile.tone} 
                          onChange={(e) => setProfile({...profile, tone: e.target.value})}
                        >
                          <option value="professional">Professional</option>
                          <option value="casual">Friendly</option>
                          <option value="technical">Technical</option>
                          <option value="persuasive">Persuasive</option>
                        </select>
                      </div>
                      <div className="form-group">
                        <label>Audience</label>
                        <select 
                          value={profile.audience} 
                          onChange={(e) => setProfile({...profile, audience: e.target.value})}
                        >
                          <option value="student">Students</option>
                          <option value="developer">Developers</option>
                          <option value="business">Business</option>
                          <option value="general">General</option>
                        </select>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>

              <motion.div className="glass-morphism card" variants={itemVariants}>
                 <div className="email-toggle-row" onClick={() => setSendEmail(!sendEmail)}>
                    <div className={`checkbox ${sendEmail ? 'checked' : ''}`}>
                      {sendEmail && <CheckCircle size={14} />}
                    </div>
                    <div className="toggle-info">
                      <p className="toggle-label">Inbox Delivery</p>
                      <p className="toggle-desc">Automatically send final draft to your email</p>
                    </div>
                    <Mail className={sendEmail ? 'text-primary' : 'text-muted'} size={20} />
                 </div>
                 
                 {sendEmail && (
                   <motion.div 
                     className="email-input-container"
                     initial={{ opacity: 0, y: -10 }}
                     animate={{ opacity: 1, y: 0 }}
                   >
                     <input 
                       type="email" 
                       placeholder="your-email@example.com"
                       value={email}
                       onChange={(e) => setEmail(e.target.value)}
                       className="email-input"
                     />
                   </motion.div>
                 )}
              </motion.div>

              <motion.button 
                className="execute-btn" 
                onClick={handleRunTask}
                disabled={loading}
                variants={itemVariants}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {loading ? (
                  <>
                    <Loader2 className="animate-spin" size={20} />
                    <span>Synthesizing Knowledge...</span>
                  </>
                ) : (
                  <>
                    <Zap size={20} fill="#fff" />
                    <span>Execute Super Agent</span>
                  </>
                )}
              </motion.button>
            </motion.div>

            {/* Right Panel: Results/Workspace */}
            <div className="results-panel">
              <AnimatePresence mode="wait">
                {result ? (
                  <motion.div 
                    className="glass-morphism result-card"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    key="result"
                  >
                    <div className="result-header">
                      <div className="header-info">
                        <Sparkles className="text-secondary" size={18} />
                        <h3>AI Output</h3>
                      </div>
                      <div className="result-actions">
                        <button className="action-btn" onClick={copyToClipboard}>
                          <Clipboard size={16} />
                          <span>Copy</span>
                        </button>
                        <button className="action-btn primary" onClick={handleSendEmail}>
                          <Send size={16} />
                          <span>Deliver</span>
                        </button>
                      </div>
                    </div>
                    <div className="editor-container">
                      <textarea 
                        ref={resultRef}
                        value={result}
                        onChange={(e) => setResult(e.target.value)}
                        className="result-editor"
                      />
                    </div>
                    <div className="result-footer">
                      <div className="token-usage">
                        <Zap size={12} className="text-primary" />
                        <span>Optimized via RAG pipeline</span>
                      </div>
                      <div className="save-timestamp">
                        Synced just now
                      </div>
                    </div>
                  </motion.div>
                ) : (
                  <motion.div 
                    className="empty-state"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    key="empty"
                  >
                    <div className="empty-icon-container">
                      <BrainCircuit size={64} className="empty-icon" />
                      <div className="pulse-ring"></div>
                    </div>
                    <h2>Neural Core Ready</h2>
                    <p>Input a research topic to begin the autonomous synthesis process. I'll search multiple web sources, crawl relevant data, and generate premium content tailored to your profile.</p>
                    <div className="feature-grid">
                      <div className="feature-item">
                         <Globe size={16} />
                         <span>Web Research</span>
                      </div>
                      <div className="feature-item">
                         <FileText size={16} />
                         <span>RAG Augmented</span>
                      </div>
                      <div className="feature-item">
                         <Zap size={16} />
                         <span>Neural Intent</span>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </main>

        {/* Status Notifications */}
        <AnimatePresence>
          {status.msg && (
            <motion.div 
              className={`status-notification ${status.type}`}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 50 }}
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
