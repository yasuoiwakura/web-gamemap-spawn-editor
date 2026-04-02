import type { Game, GameMap, SpawnType, POI, FlightPath } from '$lib/types';

const API_BASE = import.meta.env.VITE_API_URL || 'https://your-api-id.execute-api.eu-central-1.amazonaws.com/Prod';

class ApiClient {
  private cache: Map<string, { data: unknown; timestamp: number }> = new Map();
  private cacheTimeout = 5 * 60 * 1000;

  private async fetch<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  }

  private getCached<T>(key: string): T | null {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data as T;
    }
    this.cache.delete(key);
    return null;
  }

  private setCache(key: string, data: unknown): void {
    this.cache.set(key, { data, timestamp: Date.now() });
  }

  clearCache(): void {
    this.cache.clear();
  }

  // Games
  async getGames(forceRefresh = false): Promise<Game[]> {
    const cacheKey = 'games';
    if (!forceRefresh) {
      const cached = this.getCached<Game[]>(cacheKey);
      if (cached) return cached;
    }
    const data = await this.fetch<Game[]>('/games');
    this.setCache(cacheKey, data);
    return data;
  }

  async getGame(id: string): Promise<Game> {
    return this.fetch<Game>(`/games/${id}`);
  }

  async createGame(name: string, iconUrl?: string): Promise<Game> {
    const data = await this.fetch<Game>('/games', {
      method: 'POST',
      body: JSON.stringify({ name, iconUrl }),
    });
    this.clearCache();
    return data;
  }

  async updateGame(id: string, name: string, iconUrl?: string): Promise<Game> {
    const data = await this.fetch<Game>(`/games/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ name, iconUrl }),
    });
    this.clearCache();
    return data;
  }

  async deleteGame(id: string): Promise<void> {
    await this.fetch(`/games/${id}`, { method: 'DELETE' });
    this.clearCache();
  }

  // Maps
  async getMaps(gameId: string, forceRefresh = false): Promise<GameMap[]> {
    const cacheKey = `maps-${gameId}`;
    if (!forceRefresh) {
      const cached = this.getCached<GameMap[]>(cacheKey);
      if (cached) return cached;
    }
    const data = await this.fetch<GameMap[]>(`/games/${gameId}/maps`);
    this.setCache(cacheKey, data);
    return data;
  }

  async getMap(id: string): Promise<GameMap> {
    return this.fetch<GameMap>(`/maps/${id}`);
  }

  async createMap(gameId: string, map: Omit<GameMap, 'id' | 'gameId' | 'createdAt'>): Promise<GameMap> {
    const data = await this.fetch<GameMap>(`/games/${gameId}/maps`, {
      method: 'POST',
      body: JSON.stringify({ ...map, gameId }),
    });
    this.clearCache();
    return data;
  }

  async updateMap(id: string, map: Partial<GameMap>): Promise<GameMap> {
    const data = await this.fetch<GameMap>(`/maps/${id}`, {
      method: 'PUT',
      body: map,
    });
    this.clearCache();
    return data;
  }

  async deleteMap(id: string): Promise<void> {
    await this.fetch(`/maps/${id}`, { method: 'DELETE' });
    this.clearCache();
  }

  // Spawn Types
  async getSpawnTypes(gameId: string, forceRefresh = false): Promise<SpawnType[]> {
    const cacheKey = `spawn-types-${gameId}`;
    if (!forceRefresh) {
      const cached = this.getCached<SpawnType[]>(cacheKey);
      if (cached) return cached;
    }
    const data = await this.fetch<SpawnType[]>(`/games/${gameId}/spawn-types`);
    this.setCache(cacheKey, data);
    return data;
  }

  async createSpawnType(gameId: string, spawnType: Omit<SpawnType, 'id' | 'gameId'>): Promise<SpawnType> {
    const data = await this.fetch<SpawnType>(`/games/${gameId}/spawn-types`, {
      method: 'POST',
      body: JSON.stringify({ ...spawnType, gameId }),
    });
    this.clearCache();
    return data;
  }

  async updateSpawnType(id: string, spawnType: Partial<SpawnType>): Promise<SpawnType> {
    const data = await this.fetch<SpawnType>(`/spawn-types/${id}`, {
      method: 'PUT',
      body: spawnType,
    });
    this.clearCache();
    return data;
  }

  async deleteSpawnType(id: string): Promise<void> {
    await this.fetch(`/spawn-types/${id}`, { method: 'DELETE' });
    this.clearCache();
  }

  // POIs
  async getPOIs(mapId: string, forceRefresh = false): Promise<POI[]> {
    const cacheKey = `pois-${mapId}`;
    if (!forceRefresh) {
      const cached = this.getCached<POI[]>(cacheKey);
      if (cached) return cached;
    }
    const data = await this.fetch<POI[]>(`/maps/${mapId}/pois`);
    this.setCache(cacheKey, data);
    return data;
  }

  async createPOI(mapId: string, poi: Omit<POI, 'id' | 'mapId' | 'createdAt'>): Promise<POI> {
    const data = await this.fetch<POI>(`/maps/${mapId}/pois`, {
      method: 'POST',
      body: JSON.stringify({ ...poi, mapId }),
    });
    this.clearCache();
    return data;
  }

  async updatePOI(id: string, poi: Partial<POI>): Promise<POI> {
    const data = await this.fetch<POI>(`/pois/${id}`, {
      method: 'PUT',
      body: poi,
    });
    this.clearCache();
    return data;
  }

  async deletePOI(id: string): Promise<void> {
    await this.fetch(`/pois/${id}`, { method: 'DELETE' });
    this.clearCache();
  }

  // Flight Paths
  async getFlightPaths(mapId: string, forceRefresh = false): Promise<FlightPath[]> {
    const cacheKey = `flight-paths-${mapId}`;
    if (!forceRefresh) {
      const cached = this.getCached<FlightPath[]>(cacheKey);
      if (cached) return cached;
    }
    const data = await this.fetch<FlightPath[]>(`/maps/${mapId}/flight-paths`);
    this.setCache(cacheKey, data);
    return data;
  }

  async createFlightPath(mapId: string, flightPath: Omit<FlightPath, 'id' | 'mapId' | 'createdAt'>): Promise<FlightPath> {
    const data = await this.fetch<FlightPath>(`/maps/${mapId}/flight-paths`, {
      method: 'POST',
      body: JSON.stringify({ ...flightPath, mapId }),
    });
    this.clearCache();
    return data;
  }

  async deleteFlightPath(id: string): Promise<void> {
    await this.fetch(`/flight-paths/${id}`, { method: 'DELETE' });
    this.clearCache();
  }
}

export const api = new ApiClient();