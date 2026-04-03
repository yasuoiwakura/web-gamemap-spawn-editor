export interface Game {
  id: string;
  name: string;
  iconUrl?: string;
  createdAt: number;
}

export interface GameMap {
  id: string;
  gameId: string;
  name: string;
  imageUrl: string;
  widthPx: number;
  heightPx: number;
  realSizeMeters?: number;
  createdAt: number;
}

export interface Overlay {
  imageUrl: string;
  x: number;
  y: number;
  scale: number;
}

export interface SpawnType {
  id: string;
  gameId: string;
  name: string;
  color: string;
  iconType: 'dot' | 'arrow' | 'custom';
  rotationEnabled: boolean;
}

export interface POI {
  id: string;
  mapId: string;
  spawnTypeId: string;
  x: number;
  y: number;
  rotation?: number;
  label?: string;
  createdAt: number;
}

export interface FlightPath {
  id: string;
  mapId: string;
  startX: number;
  startY: number;
  endX: number;
  endY: number;
  createdAt: number;
}

export interface ClientState {
  currentGameId: string | null;
  currentMapId: string | null;
  currentSpawnTypeId: string | null;
  visibleSpawnTypeIds: string[];
  overlay: Overlay | null;
}