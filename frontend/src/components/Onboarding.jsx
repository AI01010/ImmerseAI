import { useState } from 'react'
import './Onboarding.css'

const LEVELS = ['beginner', 'intermediate', 'advanced']
const SUGGESTED_GOALS = [
  'Machine Learning', 'Web Development', 'Python Programming',
  'Data Science', 'Crypto Trading', 'Music Production',
  'React & Frontend', 'System Design', 'Deep Learning'
]

export default function Onboarding({ onComplete }) {
  const [step, setStep] = useState(0)
  const [name, setName] = useState('')
  const [goal, setGoal] = useState('')
  const [level, setLevel] = useState('')
  const [background, setBackground] = useState('')

  const canNext = [
    name.trim().length > 0,
    goal.trim().length > 0,
    level.length > 0,
    true
  ][step]

  const handleNext = () => {
    if (step < 3) setStep(s => s + 1)
    else onComplete({ name, goal, level, background })
  }

  return (
    <div className="onboarding">
      <div className="ob-bg">
        <div className="ob-grid" />
        <div className="ob-glow" />
      </div>

      <div className="ob-container">
        <div className="ob-header">
          <div className="ob-logo">
            <span className="ob-mark">◈</span>
            <span className="ob-name">ImmerseAI</span>
          </div>
          <p className="ob-tagline">
            Your personal AI learning advisor.<br />
            <em>Built different. Learns with logic.</em>
          </p>
        </div>

        <div className="ob-card">
          <div className="ob-progress">
            {[0,1,2,3].map(i => (
              <div key={i} className={`ob-pip ${i <= step ? 'active' : ''} ${i < step ? 'done' : ''}`} />
            ))}
          </div>

          <div className="ob-step" key={step}>
            {step === 0 && (
              <div className="ob-field">
                <label className="ob-label">What should we call you?</label>
                <input
                  className="ob-input"
                  placeholder="your name..."
                  value={name}
                  onChange={e => setName(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && canNext && handleNext()}
                  autoFocus
                />
              </div>
            )}

            {step === 1 && (
              <div className="ob-field">
                <label className="ob-label">What do you want to learn?</label>
                <input
                  className="ob-input"
                  placeholder="e.g. machine learning, web dev..."
                  value={goal}
                  onChange={e => setGoal(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && canNext && handleNext()}
                  autoFocus
                />
                <div className="ob-chips">
                  {SUGGESTED_GOALS.map(g => (
                    <button
                      key={g}
                      className={`ob-chip ${goal === g ? 'selected' : ''}`}
                      onClick={() => setGoal(g)}
                    >{g}</button>
                  ))}
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="ob-field">
                <label className="ob-label">Where are you right now?</label>
                <div className="ob-levels">
                  {LEVELS.map(l => (
                    <button
                      key={l}
                      className={`ob-level ${level === l ? 'selected' : ''}`}
                      onClick={() => setLevel(l)}
                    >
                      <span className="ob-level-icon">
                        {l === 'beginner' ? '🌱' : l === 'intermediate' ? '🔥' : '⚡'}
                      </span>
                      <span className="ob-level-name">{l}</span>
                      <span className="ob-level-desc">
                        {l === 'beginner' ? 'Just starting out' :
                         l === 'intermediate' ? 'Know the basics' :
                         'Ready for advanced topics'}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="ob-field">
                <label className="ob-label">
                  Any background to know? <span className="ob-optional">(optional)</span>
                </label>
                <textarea
                  className="ob-input ob-textarea"
                  placeholder="e.g. I know Python basics, I've done one Coursera course..."
                  value={background}
                  onChange={e => setBackground(e.target.value)}
                  autoFocus
                  rows={3}
                />
                <div className="ob-summary">
                  <div className="ob-summary-row">
                    <span>name</span><span>{name}</span>
                  </div>
                  <div className="ob-summary-row">
                    <span>goal</span><span>{goal}</span>
                  </div>
                  <div className="ob-summary-row">
                    <span>level</span><span>{level}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          <button
            className={`ob-btn ${canNext ? '' : 'disabled'}`}
            onClick={handleNext}
            disabled={!canNext}
          >
            {step < 3 ? 'Continue →' : 'Build My Roadmap ◈'}
          </button>
        </div>
      </div>
    </div>
  )
}
