import { useState, type FormEvent } from 'react'
import {
  listTraces,
  runMultiHop,
  runSupervisor,
  type MultiHopResponse,
  type SupervisorResponse,
  type TraceEvent,
} from '../api/client'

export function AgentsPage() {
  const [query, setQuery] = useState(
    'search notes about MCP and research latest agent orchestration news',
  )
  const [question, setQuestion] = useState(
    'Using the internship brief, what should Phase 3 focus on?',
  )
  const [supervisor, setSupervisor] = useState<SupervisorResponse | null>(null)
  const [multiHop, setMultiHop] = useState<MultiHopResponse | null>(null)
  const [traces, setTraces] = useState<TraceEvent[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSupervise(event: FormEvent) {
    event.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const result = await runSupervisor(query, 'ui-supervisor', 'internship-brief.txt')
      setSupervisor(result)
      setTraces(result.traces)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Supervisor failed')
    } finally {
      setLoading(false)
    }
  }

  async function handleMultiHop(event: FormEvent) {
    event.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const result = await runMultiHop(question, 'ui-multihop')
      setMultiHop(result)
      setTraces(result.traces)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Multi-hop failed')
    } finally {
      setLoading(false)
    }
  }

  async function refreshTraces() {
    const payload = await listTraces()
    setTraces(payload.events)
  }

  return (
    <section>
      <p className="eyebrow">Week 5 · Orchestration</p>
      <h1>Supervisor, workers & traces</h1>
      <p className="lede">
        Route a task to research / notes / file workers, run a multi-hop demo (file → memory →
        SerpAPI), and inspect timestamped tool-call traces.
      </p>

      <div className="research-grid">
        <form className="note-form" onSubmit={handleSupervise}>
          <label className="field">
            <span>Supervisor query</span>
            <textarea rows={4} value={query} onChange={(e) => setQuery(e.target.value)} />
          </label>
          <button type="submit" disabled={loading}>
            {loading ? 'Routing…' : 'Run supervisor'}
          </button>
        </form>

        <form className="note-form" onSubmit={handleMultiHop}>
          <label className="field">
            <span>Multi-hop question</span>
            <textarea rows={4} value={question} onChange={(e) => setQuestion(e.target.value)} />
          </label>
          <button type="submit" className="button ghost" disabled={loading}>
            Run multi-hop demo
          </button>
        </form>
      </div>

      {error ? <p className="banner error">{error}</p> : null}

      {supervisor ? (
        <div className="narrow" style={{ maxWidth: '100%', marginTop: '1.5rem' }}>
          <h2>Supervisor route</h2>
          <p className="meta">{supervisor.route.join(' → ')}</p>
          <pre className="answer-block">{supervisor.answer}</pre>
        </div>
      ) : null}

      {multiHop ? (
        <div className="narrow" style={{ maxWidth: '100%', marginTop: '1.5rem' }}>
          <h2>Multi-hop steps</h2>
          <ol className="fact-list">
            {multiHop.steps.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
          <pre className="answer-block">{multiHop.answer}</pre>
        </div>
      ) : null}

      <div style={{ marginTop: '1.5rem' }}>
        <div className="section-head">
          <h2>Trace log</h2>
          <button type="button" className="button ghost" onClick={() => void refreshTraces()}>
            Refresh traces
          </button>
        </div>
        {traces.length === 0 ? <p className="empty">No tool calls traced yet.</p> : null}
        <ul className="note-list">
          {traces
            .slice()
            .reverse()
            .slice(0, 30)
            .map((event) => (
              <li key={`${event.id}-${event.phase}`} className="note-card">
                <div>
                  <h2>
                    {event.agent} · {event.tool} · {event.phase}
                  </h2>
                  <p className="meta">{event.timestamp}</p>
                  {event.result_preview ? <p>{event.result_preview}</p> : null}
                  {event.error ? <p className="field-error">{event.error}</p> : null}
                </div>
              </li>
            ))}
        </ul>
      </div>
    </section>
  )
}
