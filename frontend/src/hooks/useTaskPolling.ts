import { useState, useEffect, useRef, useCallback } from 'react'
import { getTaskStatus, type TaskStatus } from '../api'

export function useTaskPolling(taskId: string | null, interval = 1500) {
  const [status, setStatus] = useState<TaskStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const stopPolling = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
  }, [])

  useEffect(() => {
    if (!taskId) {
      setStatus(null)
      setLoading(false)
      stopPolling()
      return
    }

    setLoading(true)

    const poll = async () => {
      try {
        const s = await getTaskStatus(taskId)
        setStatus(s)
        if (s.status === 'completed' || s.status === 'failed') {
          setLoading(false)
          stopPolling()
        }
      } catch {
        setLoading(false)
        stopPolling()
      }
    }

    poll()
    timerRef.current = setInterval(poll, interval)

    return stopPolling
  }, [taskId, interval, stopPolling])

  return { status, loading }
}
