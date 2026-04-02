import { writable, derived, get } from 'svelte/store';
import type { Game, GameMap, SpawnType, POI, FlightPath, ClientState, Overlay } from '$lib/types';
import { api } from '$lib/api/client';

const STORAGE_KEY = 'gamemap-state';

function loadFromStorage<T>(key: string, defaultValue: T): T {
  if (typeof window === 'undefined') return defaultValue;
  try {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : defaultValue;
  } catch {
    return defaultValue;
  }
}

function saveToStorage(key: string, value: unknown): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    console.error('Failed to save to localStorage:', e);
  }
}

// Client State
const storedState = loadFromStorage<ClientState>('client-state', {
  currentGameId: null,
  currentMapId: null,
  currentSpawnTypeId: null,
  visibleSpawnTypeIds: [],
  overlay: null,
});

export const clientState = writable<ClientState>(storedState);

clientState.subscribe((value) => {
  saveToStorage('client-state', value);
});

// Data Stores
export const games = writable<Game[]>([]);
export const maps = writable<GameMap[]>([]);
export const spawnTypes = writable<SpawnType[]>([]);
export const pois = writable<POI[]>([]);
export const flightPaths = writable<FlightPath[]>([]);

// Loading states
export const isLoading = writable(false);
export const error = writable<string | null>(null);

// Derived stores
export const currentGame = derived([games, clientState], ([$games, $clientState]) => 
  $games.find(g => g.id === $clientState.currentGameId) || null
);

export const currentMap = derived([maps, clientState], ([$maps, $clientState]) => 
  $maps.find(m => m.id === $clientState.currentMapId) || null
);

export const currentSpawnType = derived([spawnTypes, clientState], ([$spawnTypes, $clientState]) => 
  $spawnTypes.find(st => st.id === $clientState.currentSpawnTypeId) || null
);

export const visiblePOIs = derived([pois, clientState], ([$pois, $clientState]) => {
  if ($clientState.visibleSpawnTypeIds.length === 0) return $pois;
  return $pois.filter(p => $clientState.visibleSpawnTypeIds.includes(p.spawnTypeId));
});

// Actions
export async function loadGames(): Promise<void> {
  isLoading.set(true);
  error.set(null);
  try {
    const data = await api.getGames();
    games.set(data);
  } catch (e) {
    error.set(e instanceof Error ? e.message : 'Failed to load games');
  } finally {
    isLoading.set(false);
  }
}

export async function loadMaps(gameId: string): Promise<void> {
  isLoading.set(true);
  error.set(null);
  try {
    const data = await api.getMaps(gameId);
    maps.set(data);
  } catch (e) {
    error.set(e instanceof Error ? e.message : 'Failed to load maps');
  } finally {
    isLoading.set(false);
  }
}

export async function loadSpawnTypes(gameId: string): Promise<void> {
  try {
    const data = await api.getSpawnTypes(gameId);
    spawnTypes.set(data);
  } catch (e) {
    error.set(e instanceof Error ? e.message : 'Failed to load spawn types');
  }
}

export async function loadPOIs(mapId: string): Promise<void> {
  try {
    const data = await api.getPOIs(mapId);
    pois.set(data);
  } catch (e) {
    error.set(e instanceof Error ? e.message : 'Failed to load POIs');
  }
}

export async function loadFlightPaths(mapId: string): Promise<void> {
  try {
    const data = await api.getFlightPaths(mapId);
    flightPaths.set(data);
  } catch (e) {
    error.set(e instanceof Error ? e.message : 'Failed to load flight paths');
  }
}

export async function createGame(name: string, iconUrl?: string): Promise<Game> {
  const game = await api.createGame(name, iconUrl);
  games.update(g => [...g, game]);
  clientState.update(s => ({ ...s, currentGameId: game.id }));
  return game;
}

export async function createMap(gameId: string, map: Omit<GameMap, 'id' | 'gameId' | 'createdAt'>): Promise<GameMap> {
  const newMap = await api.createMap(gameId, map);
  maps.update(m => [...m, newMap]);
  clientState.update(s => ({ ...s, currentMapId: newMap.id }));
  return newMap;
}

export async function createSpawnType(gameId: string, spawnType: Omit<SpawnType, 'id' | 'gameId'>): Promise<SpawnType> {
  const newSpawnType = await api.createSpawnType(gameId, spawnType);
  spawnTypes.update(st => [...st, newSpawnType]);
  return newSpawnType;
}

export async function createPOI(mapId: string, poi: Omit<POI, 'id' | 'mapId' | 'createdAt'>): Promise<POI> {
  const newPOI = await api.createPOI(mapId, poi);
  pois.update(p => [...p, newPOI]);
  return newPOI;
}

export async function createFlightPath(mapId: string, flightPath: Omit<FlightPath, 'id' | 'mapId' | 'createdAt'>): Promise<FlightPath> {
  const newFlightPath = await api.createFlightPath(mapId, flightPath);
  flightPaths.update(fp => [...fp, newFlightPath]);
  return newFlightPath;
}

export async function deletePOI(id: string): Promise<void> {
  await api.deletePOI(id);
  pois.update(p => p.filter(poi => poi.id !== id));
}

export async function deleteFlightPath(id: string): Promise<void> {
  await api.deleteFlightPath(id);
  flightPaths.update(fp => fp.filter(f => f.id !== id));
}

export function setCurrentGame(gameId: string | null): void {
  clientState.update(s => ({ ...s, currentGameId: gameId, currentMapId: null }));
}

export function setCurrentMap(mapId: string | null): void {
  clientState.update(s => ({ ...s, currentMapId: mapId }));
}

export function setCurrentSpawnType(spawnTypeId: string | null): void {
  clientState.update(s => ({ ...s, currentSpawnTypeId: spawnTypeId }));
}

export function setVisibleSpawnTypes(spawnTypeIds: string[]): void {
  clientState.update(s => ({ ...s, visibleSpawnTypeIds: spawnTypeIds }));
}

export function setOverlay(overlay: Overlay | null): void {
  clientState.update(s => ({ ...s, overlay }));
}