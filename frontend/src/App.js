import React, { useState, useRef, useEffect, useCallback } from 'react';

const API_BASE = process.env.REACT_APP_API_URL || window.location.origin;

const styles = {
  root: {
    minHeight: '100vh',
    background: '#f8fafc', // 优化：清爽的浅灰蓝色底
    color: '#1e293b', // 优化：深石板色文字，阅读体验极佳
    fontFamily: "'Inter', -apple-system, system-ui, sans-serif",
    display: 'flex',
    flexDirection: 'column',
  },
  header: {
    borderBottom: '1px solid #e2e8f0', // 优化：浅色分割线
    padding: '16px 24px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    background: '#ffffff',
  },
  headerLeft: { display: 'flex', alignItems: 'center', gap: '12px' },
  logo: {
    width: '32px', height: '32px',
    background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)', // 优化：深紫色渐变
    borderRadius: '8px',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: '16px',
    boxShadow: '0 2px 8px rgba(79, 70, 229, 0.2)',
  },
  headerTitle: { fontSize: '15px', fontWeight: '600', color: '#0f172a', letterSpacing: '-0.2px' },
  headerSub: { fontSize: '12px', color: '#64748b', marginTop: '1px' },
  sessionBadge: {
    fontSize: '11px', color: '#6366f1',
    background: '#eff6ff',
    border: '1px solid #dbeafe',
    borderRadius: '20px', padding: '4px 10px',
    fontFamily: "'IBM Plex Mono', monospace",
  },
  main: { flex: 1, display: 'flex', maxWidth: '820px', width: '100%', margin: '0 auto', flexDirection: 'column', padding: '0 16px' },
  messageList: { flex: 1, padding: '24px 0', display: 'flex', flexDirection: 'column', gap: '24px', overflowY: 'auto' },
  empty: {
    flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
    gap: '12px', color: '#94a3b8', padding: '60px 0',
  },
  emptyIcon: { fontSize: '40px', opacity: 0.5 },
  emptyTitle: { fontSize: '16px', color: '#475569', fontWeight: '500' },
  emptyHints: { display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center', marginTop: '8px' },
  hint: {
    fontSize: '12px', color: '#475569', background: '#ffffff',
    border: '1px solid #e2e8f0', borderRadius: '20px',
    padding: '6px 14px', cursor: 'pointer', transition: 'all 0.15s',
    boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
  },
  msgRow: (role) => ({
    display: 'flex',
    flexDirection: role === 'user' ? 'row-reverse' : 'row',
    gap: '12px', alignItems: 'flex-start',
  }),
  avatar: (role) => ({
    width: '30px', height: '30px', borderRadius: '50%', flexShrink: 0,
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: '11px', fontWeight: '600', marginTop: '2px',
    background: role === 'user' ? '#f1f5f9' : '#6366f1',
    color: role === 'user' ? '#475569' : '#ffffff',
    border: role === 'user' ? '1px solid #e2e8f0' : 'none',
  }),
  bubble: (role) => ({
    maxWidth: '80%',
    background: role === 'user' ? '#6366f1' : '#ffffff', // 优化：用户蓝色，AI白色
    color: role === 'user' ? '#ffffff' : '#1e293b',
    border: role === 'user' ? 'none' : '1px solid #e2e8f0',
    borderRadius: role === 'user' ? '16px 4px 16px 16px' : '4px 16px 16px 16px',
    padding: '12px 16px',
    boxShadow: role === 'user' ? '0 4px 12px rgba(99, 102, 241, 0.2)' : '0 1px 3px rgba(0,0,0,0.05)',
  }),
  bubbleText: { fontSize: '14.5px', lineHeight: '1.6', whiteSpace: 'pre-wrap' },
  stepsList: { marginTop: '12px', display: 'flex', flexWrap: 'wrap', gap: '6px' },
  step: {
    fontSize: '11px', fontFamily: "'IBM Plex Mono', monospace",
    color: '#4338ca', background: '#eef2ff',
    border: '1px solid #e0e7ff',
    borderRadius: '4px', padding: '2px 8px',
  },
  sourcesList: { marginTop: '14px', paddingTop: '10px', borderTop: '1px solid #f1f5f9' },
  sourceLabel: { fontSize: '10px', color: '#94a3b8', marginBottom: '6px', textTransform: 'uppercase', fontWeight: 'bold' },
  sourceLink: {
    display: 'block', fontSize: '12px', color: '#3b82f6',
    fontFamily: "'IBM Plex Mono', monospace",
    textDecoration: 'none', marginTop: '3px',
    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
  },
  thinking: {
    fontSize: '13px', color: '#94a3b8', fontStyle: 'normal',
    display: 'flex', alignItems: 'center', gap: '8px',
  },
  dot: (i) => ({
    width: '5px', height: '5px', borderRadius: '50%',
    background: '#6366f1', display: 'inline-block',
    animation: `pulse 1.2s ease-in-out ${i * 0.2}s infinite`,
  }),
  inputArea: {
    padding: '16px 0 24px',
    background: '#f8fafc',
  },
  inputRow: {
    display: 'flex', gap: '10px', alignItems: 'flex-end',
    background: '#ffffff', border: '1px solid #e2e8f0',
    borderRadius: '16px', padding: '12px 14px',
    boxShadow: '0 4px 20px rgba(0,0,0,0.03)',
    transition: 'border-color 0.15s',
  },
  textarea: {
    flex: 1, background: 'transparent', border: 'none', outline: 'none',
    color: '#0f172a', fontSize: '15px', lineHeight: '1.5',
    resize: 'none', fontFamily: "inherit",
    maxHeight: '120px', minHeight: '22px',
  },
  sendBtn: (disabled) => ({
    width: '32px', height: '32px', borderRadius: '10px', border: 'none',
    background: disabled ? '#f1f5f9' : '#6366f1',
    color: disabled ? '#94a3b8' : '#ffffff',
    cursor: disabled ? 'not-allowed' : 'pointer',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: '16px', flexShrink: 0, transition: 'all 0.15s',
  }),
  clearBtn: {
    fontSize: '11px', color: '#94a3b8', background: 'transparent',
    border: 'none', padding: '4px 8px', cursor: 'pointer', marginTop: '8px',
    textDecoration: 'underline',
  },
};

const keyframes = `
@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.2); }
}
`;

function ThinkingDots() {
  return (
    <span style={styles.thinking}>
      <span style={styles.dot(0)} />
      <span style={styles.dot(1)} />
      <span style={styles.dot(2)} />
      AI is researching
    </span>
  );
}

function Message({ msg }) {
  const isUser = msg.role === 'user';
  return (
    <div style={styles.msgRow(msg.role)}>
      <div style={styles.avatar(msg.role)}>{isUser ? 'U' : 'AI'}</div>
      <div style={styles.bubble(msg.role)}>
        {msg.thinking ? (
          <ThinkingDots />
        ) : (
          <>
            <div style={styles.bubbleText}>{msg.content}</div>
            {msg.steps_taken && msg.steps_taken.length > 0 && (
              <div style={styles.stepsList}>
                {msg.steps_taken.map((s, i) => (
                  <span key={i} style={styles.step}>{s}</span>
                ))}
              </div>
            )}
            {msg.sources && msg.sources.length > 0 && (
              <div style={styles.sourcesList}>
                <div style={styles.sourceLabel}>Sources</div>
                {msg.sources.map((src, i) => (
                  <a key={i} href={src} target="_blank" rel="noreferrer" style={styles.sourceLink}>{src}</a>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

const HINTS = [
  "What are recent advances in RAG for LLMs?",
  "Explain transformer attention mechanisms",
  "Find papers on RLHF for language models",
  "What is chain-of-thought prompting?",
];

function generateSessionId() {
  return 'sess_' + Math.random().toString(36).slice(2, 10);
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(generateSessionId);
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const send = useCallback(async (queryText) => {
    const q = (queryText || input).trim();
    if (!q || loading) return;
    setInput('');

    setMessages(prev => [...prev, { role: 'user', content: q }]);
    setMessages(prev => [...prev, { role: 'assistant', thinking: true, content: '' }]);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q, session_id: sessionId, top_k: 3 }),
      });
      const data = await res.json();
      setMessages(prev => [
        ...prev.slice(0, -1),
        {
          role: 'assistant',
          content: data.answer || data.detail || 'No response.',
          steps_taken: data.steps_taken || [],
          sources: data.sources || [],
        },
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev.slice(0, -1),
        { role: 'assistant', content: '⚠ Could not reach the backend. Check the backend URL and deployment.' },
      ]);
    } finally {
      setLoading(false);
    }
  }, [input, loading, sessionId]);

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  const clearHistory = async () => {
    try {
      await fetch(`${API_BASE}/api/history/${sessionId}`, { method: 'DELETE' });
    } catch {}
    setMessages([]);
  };

  return (
    <>
      <style>{keyframes}</style>
      <div style={styles.root}>
        <header style={styles.header}>
          <div style={styles.headerLeft}>
            <div style={styles.logo}>🔍</div>
            <div>
              <div style={styles.headerTitle}>AI Research Agent</div>
              <div style={styles.headerSub}>RAG · arXiv · GPT-4o-mini</div>
            </div>
          </div>
          <div style={styles.sessionBadge}>{sessionId}</div>
        </header>

        <main style={styles.main}>
          <div style={styles.messageList}>
            {messages.length === 0 ? (
              <div style={styles.empty}>
                <div style={styles.emptyIcon}>◎</div>
                <div style={styles.emptyTitle}>Ask about any research topic</div>
                <div style={styles.emptyHints}>
                  {HINTS.map((h, i) => (
                    <span key={i} style={styles.hint} onClick={() => send(h)}>{h}</span>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((msg, i) => <Message key={i} msg={msg} />)
            )}
            <div ref={bottomRef} />
          </div>

          <div style={styles.inputArea}>
            <div style={styles.inputRow}>
              <textarea
                ref={textareaRef}
                style={styles.textarea}
                placeholder="Ask about a paper, topic, or concept..."
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKey}
                rows={1}
                disabled={loading}
              />
              <button style={styles.sendBtn(loading || !input.trim())} onClick={() => send()} disabled={loading || !input.trim()}>
                ↑
              </button>
            </div>
            {messages.length > 0 && (
              <button style={styles.clearBtn} onClick={clearHistory}>clear session</button>
            )}
          </div>
        </main>
      </div>
    </>
  );
}