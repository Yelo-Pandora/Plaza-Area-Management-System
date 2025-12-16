import { request } from './index'

// Storearea
export function getStoreareaById(id) {
  return request(`api/search/storearea/${id}/`, { method: 'GET' })
}

export function searchStoreareaByName(name) {
  const q = new URLSearchParams({ name }).toString()
  return request(`api/search/storearea/search/?${q}`, { method: 'GET' })
}

export function listStoreareaByType(type = '') {
  const q = new URLSearchParams({ type }).toString()
  return request(`api/search/storearea/list/?${q}`, { method: 'GET' })
}

export function getStoreareaEvents(id) {
  return request(`api/search/storearea/${id}/events/`, { method: 'GET' })
}

export function getStoreareaMapIds(id) {
  return request(`api/search/storearea/${id}/map/`, { method: 'GET' })
}

export function getStoreareaIdsByMapAndType(map_id = '', type = '') {
  const q = new URLSearchParams({ map_id, type }).toString()
  return request(`api/search/storearea/list/map/?${q}`, { method: 'GET' })
}

export function getAllStoreareaIdsByMap(map_id) {
  const q = new URLSearchParams({ map_id }).toString()
  return request(`api/search/storearea/list/all_by_map/?${q}`, { method: 'GET' })
}

// Event
export function getEventById(id) {
  return request(`api/search/event/${id}/`, { method: 'GET' })
}

export function searchEventByName(name) {
  const q = new URLSearchParams({ name }).toString()
  return request(`api/search/event/search/?${q}`, { method: 'GET' })
}

export function listEventByType(type = '') {
  const q = new URLSearchParams({ type }).toString()
  return request(`api/search/event/list/?${q}`, { method: 'GET' })
}

export function getEventAreas(event_id) {
  return request(`api/search/event/${event_id}/areas/`, { method: 'GET' })
}

// Eventarea
export function getEventareaById(id) {
  return request(`api/search/eventarea/${id}/`, { method: 'GET' })
}

export function getEventareaIdsByMapAndType(map_id = '', type = '') {
  const q = new URLSearchParams({ map_id, type }).toString()
  return request(`api/search/eventarea/list/ids_by_map_type/?${q}`, { method: 'GET' })
}

export function getEventareaMapIds(id) {
  return request(`api/search/eventarea/${id}/map/`, { method: 'GET' })
}

export function getAllEventareaIdsByMap(map_id) {
  const q = new URLSearchParams({ map_id }).toString()
  return request(`api/search/eventarea/list/all_by_map/?${q}`, { method: 'GET' })
}

// Facility
export function getFacilityById(id) {
  return request(`api/search/facility/${id}/`, { method: 'GET' })
}

export function getFacilityIdsByMapAndType(map_id = '', type = '') {
  const q = new URLSearchParams({ map_id, type }).toString()
  return request(`api/search/facility/list/ids_by_map_type/?${q}`, { method: 'GET' })
}

export function getFacilityMapIds(id) {
  return request(`api/search/facility/${id}/map/`, { method: 'GET' })
}

export function getAllFacilityIdsByMap(map_id) {
  const q = new URLSearchParams({ map_id }).toString()
  return request(`api/search/facility/list/all_by_map/?${q}`, { method: 'GET' })
}

// Otherarea
export function getOtherareaById(id) {
  return request(`api/search/otherarea/${id}/`, { method: 'GET' })
}

export function getOtherareaIdsByMapAndType(map_id = '', type = '') {
  const q = new URLSearchParams({ map_id, type }).toString()
  return request(`api/search/otherarea/list/ids_by_map_type/?${q}`, { method: 'GET' })
}

export function getOtherareaMapIds(id) {
  return request(`api/search/otherarea/${id}/map/`, { method: 'GET' })
}

export function getAllOtherareaIdsByMap(map_id) {
  const q = new URLSearchParams({ map_id }).toString()
  return request(`api/search/otherarea/list/all_by_map/?${q}`, { method: 'GET' })
}
