import { useState } from 'react'
import './RoadmapPanel.css'

export default function RoadmapPanel({ roadmap, loading }) {
  const [tab, setTab] = useState('roadmap')

  if (loading) {
    return (
      <div className="roadmap-panel">
        <div className="roadmap-header">
          <span className="roadmap-title">Learning Roadmap</span>
        </div>
        <div className="roadmap-skeleton">
          {[1,2,3,4].map(i => (
            <div key={i} className="skeleton-block" style={{ animationDelay: `${i * 0.1}s` }} />
          ))}
        </div>
      </div>
    )
  }

  if (!roadmap) {
    return (
      <div className="roadmap-panel">
        <div className="roadmap-header">
          <span className="roadmap-title">Learning Roadmap</span>
        </div>
        <div className="roadmap-empty">
          <div className="roadmap-empty-graphic">
            <div className="re-ring re-ring-1" />
            <div className="re-ring re-ring-2" />
            <div className="re-ring re-ring-3" />
            <span className="re-icon">◈</span>
          </div>
          <p className="re-text">Your personalized roadmap will appear here after the AI analyzes your profile.</p>
          <div className="re-agents">
            <div className="re-agent">
              <span className="re-dot re-dot-blue" />
              <span>ProfileAgent</span>
            </div>
            <div className="re-agent">
              <span className="re-dot re-dot-green" />
              <span>CurriculumAgent</span>
            </div>
            <div className="re-agent">
              <span className="re-dot re-dot-amber" />
              <span>LogicAgent</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="roadmap-panel">
      <div className="roadmap-header">
        <span className="roadmap-title">Learning Roadmap</span>
        <div className="roadmap-tabs">
          <button className={`rtab ${tab === 'roadmap' ? 'active' : ''}`} onClick={() => setTab('roadmap')}>
            path
          </button>
          <button className={`rtab ${tab === 'resources' ? 'active' : ''}`} onClick={() => setTab('resources')}>
            resources
          </button>
        </div>
      </div>

      <div className="roadmap-body">
        {roadmap.level && (
          <div className="roadmap-meta">
            <div className="meta-chip">
              <span className="meta-label">level</span>
              <span className="meta-value">{roadmap.level}</span>
            </div>
            {roadmap.estimatedTime && (
              <div className="meta-chip">
                <span className="meta-label">est. time</span>
                <span className="meta-value">{roadmap.estimatedTime}</span>
              </div>
            )}
          </div>
        )}

        {tab === 'roadmap' && (
          <div className="roadmap-phases">
            {roadmap.phases.length > 0 ? (
              roadmap.phases.map((phase, pi) => (
                <PhaseCard key={pi} phase={phase} index={pi} total={roadmap.phases.length} />
              ))
            ) : (
              <div className="roadmap-raw">
                <p className="raw-label">AI Response</p>
                <p className="raw-text">{roadmap.raw?.slice(0, 600)}...</p>
              </div>
            )}

            {roadmap.nextAction && (
              <div className="next-action">
                <span className="na-label">next step</span>
                <span className="na-arrow">→</span>
                <span className="na-text">{roadmap.nextAction}</span>
              </div>
            )}
          </div>
        )}

        {tab === 'resources' && (
          <div className="resources-list">
            {roadmap.resources.length > 0 ? (
              roadmap.resources.map((r, i) => (
                <ResourceCard key={i} resource={r} index={i} />
              ))
            ) : (
              <div className="no-resources">
                <p>Resources will appear here once the AI finds the best materials for your level.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function PhaseCard({ phase, index, total }) {
  const [open, setOpen] = useState(true)
  const colors = ['var(--blue)', 'var(--accent)', 'var(--green)', '#c084fc']
  const color = colors[index % colors.length]

  return (
    <div className="phase-card" style={{ '--phase-color': color }}>
      <div className="phase-connector">
        <div className="phase-line" />
        <div className="phase-node" />
        {index < total - 1 && <div className="phase-line phase-line-bottom" />}
      </div>
      <div className="phase-content">
        <button className="phase-header" onClick={() => setOpen(o => !o)}>
          <div className="phase-number">Phase {index + 1}</div>
          <div className="phase-name">{phase.title.replace(/Phase \d+\s*[—-]?\s*/i, '')}</div>
          <span className="phase-toggle">{open ? '−' : '+'}</span>
        </button>
        {open && (
          <div className="phase-items">
            {phase.items.map((item, i) => (
              <div key={i} className="phase-item">
                <span className="phase-item-dot" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function ResourceCard({ resource, index }) {
  return (
    <a
      className="resource-card"
      href={resource.url}
      target="_blank"
      rel="noreferrer"
      style={{ animationDelay: `${index * 0.05}s` }}
    >
      <div className="rc-icon">📺</div>
      <div className="rc-info">
        <div className="rc-title">{resource.title}</div>
        <div className="rc-channel">{resource.channel}</div>
      </div>
      <div className="rc-arrow">↗</div>
    </a>
  )
}
