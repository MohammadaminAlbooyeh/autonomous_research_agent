const API_BASE = '/api/research'

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
