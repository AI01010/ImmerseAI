import { useState, useRef, useEffect } from 'react'
import ChatPanel from './components/ChatPanel'
import RoadmapPanel from './components/RoadmapPanel'
import Onboarding from './components/Onboarding'
import './App.css'

const ADK_BASE = import.meta.env.VITE_ADK_URL || ''
const APP_NAME = 'agent'

function generateSessionId() {
  return 'sess_' + Math.random().toString(36).slice(2, 10)
}

export default function App() {
  const [phase, setPhase] = useState('onboarding') // onboarding | app
  const [userProfile, setUserProfile] = useState(null)
  const [messages, setMessages] = useState([])
  const [roadmap, setRoadmap] = useState(null)
  const [loading, setLoading] = useState(false)
  const sessionId = useRef(generateSessionId())
  const userId = useRef('user_' + Math.random().toString(36).slice(2, 8))

  const handleOnboardingComplete = (profile) => {
    setUserProfile(profile)
    setPhase('app')
    // Send initial message automatically
    const intro = `Hi! I'm ${profile.name}. I want to learn ${profile.goal}. I'm currently at ${profile.level} level. ${profile.background ? 'Background: ' + profile.background : ''}`
    sendMessage(intro, profile)
  }

  const sendMessage = async (text, profile = userProfile) => {
    if (!text.trim() || loading) return

    const userMsg = { role: 'user', content: text, ts: Date.now() }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)

    try {
      const res = await fetch(`${ADK_BASE}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          app_name: APP_NAME,
          user_id: userId.current,
          session_id: sessionId.current,
          new_message: {
            role: 'user',
            parts: [{ text }]
          }
        })
      })

      const data = await res.json()
      const agentText = extractText(data)

      const agentMsg = { role: 'agent', content: agentText, ts: Date.now() }
      setMessages(prev => [...prev, agentMsg])

      // Parse roadmap from response
      const parsed = parseRoadmap(agentText)
      if (parsed) setRoadmap(parsed)

    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'agent',
        content: '⚠️ Connection error. Make sure `uv run adk web` is running on port 8000.',
        ts: Date.now(),
        error: true
      }])
    }

    setLoading(false)
  }

  return (
    <div className="app-shell">
      {phase === 'onboarding' ? (
        <Onboarding onComplete={handleOnboardingComplete} />
      ) : (
        <div className="workspace">
          <header className="topbar">
            <div className="topbar-left">
              <span className="logo-mark">◈</span>
              <span className="logo-text">ImmerseAI</span>
            </div>
            <div className="topbar-center">
              {userProfile && (
                <span className="session-tag">
                  {userProfile.name} · <em>{userProfile.goal}</em> · {userProfile.level}
                </span>
              )}
            </div>
            <div className="topbar-right">
              <div className="status-dot" />
              <span className="status-text">live</span>
            </div>
          </header>

          <div className="panels">
            <ChatPanel
              messages={messages}
              loading={loading}
              onSend={sendMessage}
              userProfile={userProfile}
            />
            <RoadmapPanel roadmap={roadmap} loading={loading && messages.length <= 1} />
          </div>
        </div>
      )}
    </div>
  )
}

function extractText(data) {
  if (!data) return 'No response.'
  if (Array.isArray(data)) {
    return data
      .filter(e => e?.content?.parts)
      .flatMap(e => e.content.parts)
      .map(p => p.text || '')
      .join('\n')
      .trim() || 'Processing complete.'
  }
  if (data.response) return data.response
  if (data.text) return data.text
  return JSON.stringify(data)
}

function parseRoadmap(text) {
  if (!text.includes('Phase') && !text.includes('ROADMAP') && !text.includes('Step')) return null

  const phases = []
  const phaseRegex = /\*\*Phase\s*\d+[^*]*\*\*([^]*?)(?=\*\*Phase|\*\*Recommended|$)/gi
  let match
  while ((match = phaseRegex.exec(text)) !== null) {
    const title = match[0].match(/\*\*([^*]+)\*\*/)?.[1] || 'Phase'
    const items = match[1].match(/[-•]\s*([^\n]+)/g)?.map(s => s.replace(/^[-•]\s*/, '').trim()) || []
    if (items.length) phases.push({ title, items })
  }

  const resources = []
  const resourceRegex = /📺\s*([^\n—-]+)[—-]\s*([^\n—-]+)[—-]\s*(https?:\/\/[^\s\n]+)/g
  while ((match = resourceRegex.exec(text)) !== null) {
    resources.push({ title: match[1].trim(), channel: match[2].trim(), url: match[3].trim() })
  }

  const timeMatch = text.match(/Estimated(?:\s+Total)?\s+(?:Learning\s+)?Time[:\s]+([^\n]+)/i)
  const nextMatch = text.match(/Next\s+(?:Immediate\s+)?Action[:\s→]+([^\n]+)/i)
  const levelMatch = text.match(/Current\s+Level[:\s]+([^\n]+)/i)

  return {
    phases,
    resources,
    estimatedTime: timeMatch?.[1]?.trim(),
    nextAction: nextMatch?.[1]?.trim(),
    level: levelMatch?.[1]?.trim(),
    raw: text
  }
}
