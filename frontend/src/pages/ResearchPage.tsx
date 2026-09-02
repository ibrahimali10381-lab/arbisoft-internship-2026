import { useEffect, useState, type FormEvent } from 'react'
import { getAgentMemory, rememberFact, runResearch, type ResearchResponse } from '../api/client'

const SESSION_KEY = 'noteslab-research-session'

function getSessionId() {
  const existing = localStorage.getItem(SESSION_KEY)
  if (existing) return existing
  const created = `session-${crypto.randomUUID()}`
  localStorage.setItem(SESSION_KEY, created)
  return created
}

export function ResearchPage() {
  const [sessionId] = useState(getSessionId)
  const [query, setQuery] = useState('latest advances in agentic AI')
  const [fact, setFact] = useState('')
  const [facts, setFacts] = useState<string[]>([])
  const [result, setResult] = useState<ResearchResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    void getAgentMemory(sessionId)
      .then((payload) => setFacts(payload.facts))
      .catch(() => setFacts([]))
  }, [sessionId])

  async function handleResearch(event: FormEvent) {
    event.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const response = await runResearch(query, sessionId)
      setResult(response)
      setFacts(response.remembered_facts)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Research failed')
    } finally {
      setLoading(false)
    }
  }

  async function handleRemember(event: FormEvent) {
    event.preventDefault()
    if (!fact.trim()) return
    const payload = await rememberFact(sessionId, fact.trim())
    setFacts(payload.facts)
    setFact('')
  }

  return (
    <section>
      <p className="eyebrow">Week 4 · Agentic AI</p>
      <h1>SerpAPI research agent</h1>
      <p className="lede">
        Planner → SerpAPI web-search skill → memory loop. Facts stored in this browser session are
        recalled on later queries.
      </p>

      <form className="note-form narrow" onSubmit={handleResearch}>
        <label className="field">
          <span>Research query</span>
          <input value={query} onChange={(e) => setQuery(e.target.value)} />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? 'Searching…' : 'Run research'}
        </button>
      </form>

      <form className="note-form narrow" onSubmit={handleRemember}>
        <label className="field">
          <span>Remember a fact for later</span>
          <input
            value={fact}
            onChange={(e) => setFact(e.target.value)}
            placeholder="e.g. Focus on open-source frameworks"
          />
        </label>
        <button type="submit" className="button ghost">
          Save to memory
        </button>
      </form>

      {error ? <p className="banner error">{error}</p> : null}

      <div className="research-grid">
        <div>
          <h2>Session memory</h2>
          {facts.length === 0 ? <p className="empty">No facts yet.</p> : null}
          <ul className="fact-list">
            {facts.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>

        {result ? (
          <div>
            <h2>Latest run</h2>
            <ol className="fact-list">
              {result.plan.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ol>
            <pre className="answer-block">{result.answer}</pre>
            <h3>Sources</h3>
            <ul className="fact-list">
              {result.sources.map((source) => (
                <li key={`${source.link}-${source.title}`}>
                  <a href={source.link} target="_blank" rel="noreferrer">
                    {source.title}
                  </a>
                  <div className="meta">{source.snippet}</div>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </section>
  )
}
