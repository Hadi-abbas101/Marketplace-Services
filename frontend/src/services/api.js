const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const post = (path, data) => fetch(`${API_URL}${path}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ ...data })
})

export const registerUser = (user) => post('/api/users/register', user)
export const loginUser = (credentials) => post('/api/users/login', credentials)

export const getUserProfile = () => {
  const token = localStorage.getItem('access_token')
  return fetch(`${API_URL}/api/users/me`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  })
}
export const updateUserProfile = (profile) => {
  const token = localStorage.getItem('access_token')
  return fetch(`${API_URL}/api/users/me`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(profile)
  })
}

export const createService = (service) => {
  const token = localStorage.getItem('access_token')
  return fetch(`${API_URL}/api/services`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(service)
  })
}

export const updateService = (id, service) => {
  const token = localStorage.getItem('access_token')
  return fetch(`${API_URL}/api/services/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ ...service })
  })
}

export const getService = (id) =>
    fetch(`${API_URL}/api/services/${id}`)

export const getServices = () =>
    fetch(`${API_URL}/api/services`)

export const searchServices = (motCle = '', filters = {}) => {
  const params = new URLSearchParams({ mot_cle: motCle })

  if (
    filters.id_categorie !== undefined
    && filters.id_categorie !== null
    && filters.id_categorie !== ''
  ) {
    params.set('id_categorie', String(filters.id_categorie))
  }

  if (
    filters.budget_max !== undefined
    && filters.budget_max !== null
    && filters.budget_max !== ''
  ) {
    params.set('budget_max', String(filters.budget_max))
  }

  return fetch(`${API_URL}/api/services?${params}`)
}

export const updateServiceStatut = (id, statut) => {
  const token = localStorage.getItem('access_token')
  return fetch(`${API_URL}/api/services/${id}/statut`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ statut })
  })
}

export const getCategories = () =>
    fetch(`${API_URL}/api/categories`)

export const deleteService = (id) => {
  const token = localStorage.getItem('access_token')
  return fetch(`${API_URL}/api/services/${id}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`
    }
  })
}

export const getCandidatures = (serviceId) => {
  const token = localStorage.getItem('access_token')
  return fetch(`${API_URL}/api/services/${serviceId}/candidatures`, {
    headers: { Authorization: `Bearer ${token}` }
  })
}

export const updateCandidatureStatut = (candidatureId, statut) => {
  const token = localStorage.getItem('access_token')
  return fetch(`${API_URL}/api/candidatures/${candidatureId}/statut`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ statut })
  })
}

export const postulerService = (serviceId, message) => {
  const token = localStorage.getItem('access_token')
  return fetch(`${API_URL}/api/services/${serviceId}/candidatures`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ message })
  })
}

export const getMesCandidatures = () => {
  const token = localStorage.getItem('access_token')
  return fetch(`${API_URL}/api/candidatures/me`, {
    headers: { Authorization: `Bearer ${token}` }
  })
}

export const getFavoris = () => {
  const token = localStorage.getItem('access_token')
  return fetch(`${API_URL}/api/favoris`, {
    headers: { Authorization: `Bearer ${token}` }
  })
}

export const ajouterFavori = (serviceId) => {
  const token = localStorage.getItem('access_token')
  return fetch(`${API_URL}/api/services/${serviceId}/favoris`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` }
  })
}

export const retirerFavori = (serviceId) => {
  const token = localStorage.getItem('access_token')
  return fetch(`${API_URL}/api/services/${serviceId}/favoris`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` }
  })
}

const authFetch = (path, options = {}) => {
  const token = localStorage.getItem('access_token')
  return fetch(`${API_URL}${path}`, {
    ...options,
    headers: { Authorization: `Bearer ${token}`, ...options.headers }
  })
}

const authPost = (path, data) => authFetch(path, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
})

export const sendServiceMessage = (serviceId, contenu) => authPost(`/api/services/${serviceId}/messages`, { contenu })
export const getConversations = () => authFetch('/api/conversations')
export const getConversation = (id) => authFetch(`/api/conversations/${id}`)
export const sendMessage = (conversationId, contenu) => authPost(`/api/conversations/${conversationId}/messages`, { contenu })

export const openConversationSocket = (conversationId) => {
  const token = localStorage.getItem('access_token')
  return new WebSocket(`${API_URL.replace(/^http/, 'ws')}/api/ws/conversations/${conversationId}?token=${token}`)
}

export const getAvisService = (serviceId) =>
  fetch(`${API_URL}/api/services/${serviceId}/avis`)

export const creerAvis = (serviceId, { note, commentaire }) =>
  authPost(`/api/services/${serviceId}/avis`, { note, commentaire })
