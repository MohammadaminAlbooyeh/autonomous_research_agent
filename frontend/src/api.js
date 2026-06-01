const API_BASE = '/api/research'
const ANALYTICS_BASE = '/api/analytics'

async function request(url, options = {}) {
  const resp = await fetch(`${API_BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return resp.json()
}

export function startResearch(topic, depth = 'medium') {
  return request('', {
    method: 'POST',
    body: JSON.stringify({ topic, depth }),
  })
}

export function listResearch(skip = 0, limit = 50) {
  return request(`?skip=${skip}&limit=${limit}`)
}

export function getResearch(taskId) {
  return request(`/${taskId}`)
}

export function deleteResearch(taskId) {
  return request(`/${taskId}`, { method: 'DELETE' })
}

export function getReport(taskId) {
  return request(`/${taskId}/report`)
}

export function exportReport(taskId, format = 'markdown') {
  return request(`/${taskId}/report/export?format=${format}`)
}

export function getStats() {
  return request('/stats')
}

async function analyticsRequest(url) {
  const resp = await fetch(`${ANALYTICS_BASE}${url}`)
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return resp.json()
}

export function getAnalyticsSummary(hours = 24) {
  return analyticsRequest(`/summary?hours=${hours}`)
}

export function getAnalyticsTopics(limit = 10, hours = 24) {
  return analyticsRequest(`/topics?limit=${limit}&hours=${hours}`)
}

export function getAnalyticsDepthDistribution(hours = 24) {
  return analyticsRequest(`/depth-distribution?hours=${hours}`)
}

export function getAnalyticsUserActivity(hours = 24) {
  return analyticsRequest(`/user-activity?hours=${hours}`)
}

export function getAnalyticsPerformanceTrends(hours = 24, intervalMinutes = 60) {
  return analyticsRequest(`/performance-trends?hours=${hours}&interval_minutes=${intervalMinutes}`)
}
