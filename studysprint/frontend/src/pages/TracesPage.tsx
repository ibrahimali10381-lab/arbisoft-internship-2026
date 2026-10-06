import { useCallback, useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api } from '../api/client'
import type { TraceEvent } from '../api/client'
import { ErrorBanner, Spinner } from '../components/ui'

export function TracesPage() {
  const [params, setParams] = useSearchParams()
  const runId = params.get('run') ?? undefined
  const [events, setEvents] = useState<TraceEvent[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(() => {
    api
      .listTraces(runId)
      .then(setEvents)
      .catch((err: Error) => setError(err.message))
  }, [runId])

  useEffect(load, [load])

  async function onClear() {
    await api.clearTraces()
    setEvents([])
  }

  return (
    <section className="card">
      <div className="row spread">
        <h1>Traces {runId && <small className="muted">run {runId}</small>}</h1>
        <div className="row">
          {runId && (
            <button type="button" className="secondary" onClick={() => setParams({})}>
              Show all
            </button>
          )}
          <button type="button" className="secondary" onClick={load}>
            Refresh
          </button>
          <button type="button" className="danger" onClick={onClear}>
            Clear
          </button>
        </div>
      </div>
      <ErrorBanner message={error} />
      {events === null && !error && <Spinner />}
      {events?.length === 0 && (
        <p className="muted">No traces yet. Upload, study or run the agent.</p>
      )}
      <table className="traces">
        <tbody>
          {events?.map((e) => (
            <tr key={e.id} className={e.status}>
              <td>
                <span className={`tag ${e.kind}`}>{e.kind}</span>
              </td>
              <td>
                <code>{e.name}</code>
              </td>
              <td className="small muted">{e.duration_ms} ms</td>
              <td className="small">
                <details>
                  <summary>{e.status}</summary>
                  <pre>{JSON.stringify(e.detail, null, 2)}</pre>
                </details>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}
