import { useEffect, useRef, useState } from 'react'
import './ChatPanel.css'

export default function ChatPanel({ messages, loading, onSend, userProfile }) {
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSend = () => {
    if (!input.trim() || loading) return
    onSend(input)
    setInput('')
  }

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <span className="chat-header-label">conversation</span>
        <span className="chat-count">{messages.length} messages</span>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="chat-empty">
            <div className="chat-empty-icon">◈</div>
            <p>Analyzing your profile and building your roadmap...</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`msg msg-${msg.role} ${msg.error ? 'msg-error' : ''}`}>
            <div className="msg-meta">
              <span className="msg-role">
                {msg.role === 'user' ? (userProfile?.name || 'you') : 'ImmerseAI'}
              </span>
              <span className="msg-time">{formatTime(msg.ts)}</span>
            </div>
            <div className="msg-body">
              <MessageContent content={msg.content} />
            </div>
          </div>
        ))}

        {loading && (
          <div className="msg msg-agent">
            <div className="msg-meta">
              <span className="msg-role">ImmerseAI</span>
              <span className="msg-time">thinking...</span>
            </div>
            <div className="msg-body">
              <div className="typing-indicator">
                <span /><span /><span />
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="chat-input-area">
        <div className="chat-input-row">
          <textarea
            ref={inputRef}
            className="chat-input"
            placeholder="Ask anything about your learning path..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSend()
              }
            }}
            rows={1}
          />
          <button
            className={`chat-send ${(!input.trim() || loading) ? 'disabled' : ''}`}
            onClick={handleSend}
            disabled={!input.trim() || loading}
          >
            ↑
          </button>
        </div>
        <div className="chat-hint">Enter to send · Shift+Enter for new line</div>
      </div>
    </div>
  )
}

function MessageContent({ content }) {
  // Basic markdown-ish rendering
  const lines = content.split('\n')
  return (
    <div className="msg-content">
      {lines.map((line, i) => {
        if (line.startsWith('**') && line.endsWith('**')) {
          return <div key={i} className="msg-heading">{line.replace(/\*\*/g, '')}</div>
        }
        if (line.startsWith('- ') || line.startsWith('• ')) {
          return <div key={i} className="msg-bullet">{line.slice(2)}</div>
        }
        if (line.match(/^\d+\./)) {
          return <div key={i} className="msg-numbered">{line}</div>
        }
        if (line.startsWith('→')) {
          return <div key={i} className="msg-action">{line}</div>
        }
        if (line.trim() === '') return <div key={i} className="msg-spacer" />
        return <div key={i} className="msg-line">{renderInline(line)}</div>
      })}
    </div>
  )
}

function renderInline(text) {
  // Bold **text**
  const parts = text.split(/(\*\*[^*]+\*\*)/)
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i}>{part.slice(2, -2)}</strong>
    }
    return part
  })
}

function formatTime(ts) {
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
