# Multi-Map Viewer - Spezifikation

## 1. Problem Statement

Ein spieleoffener Map-Viewer für taktische Spiele (z.B. PUBG), der es Nutzern ermöglicht:
- Karten verschiedener Spiele anzuzeigen
- Spawnpunkte und POIs auf Karten zu verwalten
- Benutzerdefinierte Karten-Overlays auszurichten und zu skalieren
- Taktische Elemente wie Flugbahnen einzuzeichnen
- Schnell zwischen Karten und Ansichten zu wechseln

## 2. Tech Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Frontend** | SvelteKit | SSG-fähig, client-side Interaktivität |
| **Mapping** | Leaflet | Einfachste Bibliothek für Overlays, Marker, Skalierung |
| **Backend (MVP)** | Python FastAPI → AWS Lambda | Developer-Stärke, Serverless |
| **Database** | DynamoDB | AWS Serverless, skalierbar |
| **Caching** | localStorage (Client) + API Gateway Cache | Schnelle Map-Wechsel, keine lokalen Daten |
| **Hosting** | AWS S3 + CloudFront / GitHub Pages | Kostenlos / CDN-inklusive |

### Architektur-Entscheidungen

```
┌─────────────────────────────────────────────────────────┐
│  Frontend: SvelteKit                                   │
│  → Liest: localStorage → API (MVP)                     │
│  → Später: localStorage → CDN JSON → API               │
└─────────────────────────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
    ┌─────────────┐            ┌─────────────┐
    │  REST API   │            │ Static JSON │
    │   (Lambda)  │            │   (Future)  │
    └─────────────┘            └─────────────┘
          │
          ▼
    ┌─────────────┐
    │  DynamoDB   │
    └─────────────┘
```

### Daten-Priorisierung

| Priority | Quelle | Beschreibung |
|----------|--------|---------------|
| **1 (Read)** | localStorage | Cache für schnelle Map-Wechsel |
| **2 (Read)** | CDN JSON | Später: statische JSON-Files |
| **3 (Read)** | API → DynamoDB | MVP: Primary Read |
| **1 (Write)** | API → DynamoDB | Daten-Sicherheit |
| **2 (Write)** | localStorage invalidieren | Cache aktualisieren |

### Vendor-Lock Hinweis

- **DynamoDB**: AWS-spezifisch, später übertragbar
- **Homelab-Option**: Export Pipeline → JSON-Files ohne Backend
- **Future**: Vollständig statisch (CDN-only) ohne Backend-Kosten möglich

## 3. User Stories

### 3.1 Maps verwalten
```
Als Nutzer
kann ich Maps zu einem Spiel hinzufügen (via Upload)
sodass ich verschiedene Karten des Spiels sehen kann.
```

### 3.2 Overlay ausrichten
```
Als Nutzer
kann ich ein eigenes Bild als Overlay auf die Map legen
und es mittels Anfassern skalieren/positionieren
sodass die Koordinaten exakt übereinstimmen.
```

### 3.3 Spawnpunkte erstellen
```
Als Nutzer
kann ich auf dem Overlay klicken um POIs/Spawnpunkte zu erstellen
sodass ich strategische Orte markieren kann.
```

### 3.4 Spawn-Kategorien
```
Als Nutzer
kann ich verschiedene Spawn-Typen erstellen (Gleiter, Fahrzeuge, Tankstellen)
mit eigenen Icons und Ausrichtungen
sodass ich die Karte intuitiv lesen kann.
```

### 3.5 Flugbahn einzeichnen
```
Als Nutzer
kann ich mit 2 Klicks eine Flugbahn einzeichnen
sodass ich sehe wo das Flugzeug über die Karte fliegt.
```

### 3.6 Schneller Kartwechsel
```
Als Nutzer
kann ich mit 1 Klick die Karte wechseln
und die Spawn-Auswahl bleibt erhalten
sodass ich schnell zwischen Karten navigieren kann.
```

### 3.7 Distanzmessung (Future)
```
Als Nutzer
kann ich die Kartengröße in Metern angeben
und Distanzen als Flächen anzeigen lassen
sodass ich real-world Abstände visualisieren kann.
```

## 4. Features & Prioritäten

### MVP (Must Have)
- [ ] AWS Lambda + API Gateway aufsetzen
- [ ] Python FastAPI als Handler (Mangum)
- [ ] DynamoDB Tables erstellen (Games, Maps, SpawnTypes, POIs, FlightPaths)
- [ ] Games erstellen (Name, Icon)
- [ ] Maps zu Games hinzufügen (externe Bild-URL)
- [ ] Map-Bild anzeigen
- [ ] Overlay als temporäres Bild hochladen und via 2 Eck-Anfassern skalieren/positionieren (Seitenverhältnis gelockt, wie Profilbild-Crop)
- [ ] **Koordinaten immer relativ zur Map (0-1000)** - keine Pixel!
- [ ] Spawn-Typen erstellen (Name, Icon-Farbe) - **KEINE** Vektor-Icons im MVP
- [ ] POIs durch Klicken auf Overlay erstellen (Koordinaten werden auf Map umgerechnet)
- [ ] Spawn-Typ Filter (nur bestimmte Typen anzeigen)
- [ ] Kartenauswahl oben (1 Klick), Spawn-Auswahl rechts
- [ ] Spawn-Auswahl bleibt bei Kartwechsel erhalten
- [ ] localStorage als Caching-Layer (API-Responses cachen, KEINE Bilder!)
- [ ] API-Responses werden in localStorage gecached
- [ ] Statische Demo-Daten: PUBG + 1 Map + Gleiter-Spawns

### P1 (Next Release)
- [ ] Vektor-Icons für Spawn-Typen
- [ ] Spawn-Ausrichtung (Rotation)
- [ ] Flugbahn mit 2 Klicks
- [ ] Map-Größe in Metern eingeben
- [ ] Distanz-Linien anzeigen
- [ ] Export/Import als JSON

### P2 (Future)
- [ ] CDN JSON Export Pipeline (DynamoDB → S3 → CloudFront)
- [ ] User-Auth (optional, falls geteilt)
- [ ] Distanz-Flächen (Kreise um POIs)
- [ ] Heatmaps für Spawn-Dichte
- [ ] Mobile-optimierte Ansicht
- [ ] Homelab-Option: Exportierte JSONs ohne Backend hosten

## 5. Datenmodell

### DynamoDB Tables

**Hinweis**: Alle Koordinaten sind relativ zur Map (0-1000), nicht in Pixeln.

### Game
```typescript
interface Game {
  id: string;           // UUID
  name: string;
  iconUrl?: string;
  createdAt: number;    // Unix Timestamp
}
```

### Map
```typescript
interface GameMap {
  id: string;           // UUID
  gameId: string;       // Partition Key
  name: string;
  imageUrl: string;     // URL oder Base64
  widthPx: number;     // Original-Breite in Pixel
  heightPx: number;    // Original-Höhe in Pixel
  realSizeMeters?: number; // Optional: Kartengröße in Metern
  createdAt: number;
}
```

### Overlay (Temporär - nur für aktive Session, NICHT in DB!)
```typescript
interface Overlay {
  imageUrl: string;   // Base64 vom Upload
  // Transform relativ zur Map (0-1000)
  x: number;         // Position X (0-1000)
  y: number;         // Position Y (0-1000)
  scale: number;     // Skalierung (1.0 = 100% der Map-Größe)
  // Hinweis: Overlay wird NICHT persistent gespeichert!
  // Nur temporär für "Abpaus-Flow" im aktuellen Session
}
```

**Wichtig**: Das Overlay dient nur als temporäres Hilfsmittel um POIs zu erstellen. Es wird nach der Session verworfen und nicht gespeichert. Der User kann seine eigene Karte hochladen, skalieren und positionieren, um dann POIs "abzupausen".

### SpawnType
```typescript
interface SpawnType {
  id: string;
  gameId: string;
  name: string;
  color: string;         // Hex-Farbe
  iconType: 'dot' | 'arrow' | 'custom'; // MVP: nur dot
  rotationEnabled: boolean;
}
```

### POI (Spawn Point)
```typescript
interface POI {
  id: string;
  mapId: string;
  spawnTypeId: string;
  // Relative Koordinaten zur Map (0-1000)
  x: number;
  y: number;
  // Optional: Ausrichtung in Grad (0-360) - P1
  rotation?: number;
  label?: string;
  createdAt: number;
}
```

### FlightPath
```typescript
interface FlightPath {
  id: string;
  mapId: string;
  startX: number;  // 0-1000
  startY: number;  // 0-1000
  endX: number;    // 0-1000
  endY: number;    // 0-1000
  createdAt: number;
}
```

### Client-Side Cache (localStorage)
```typescript
interface ClientCache {
  games: Game[];
  maps: GameMap[];
  spawnTypes: SpawnType[];
  pois: POI[];
  flightPaths: FlightPath[];
  lastFetch: number;    // Timestamp des letzten API-Calls
  currentGameId: string | null;
  currentMapId: string | null;
  currentSpawnTypeId: string | null;
  visibleSpawnTypeIds: string[];
}
```
**Hinweis**: localStorage dient als Cache, nicht als Primary Storage. Source of Truth ist die DynamoDB.

## 6. API Design

### MVP: AWS Serverless (Lambda + DynamoDB)

```
Base URL: https://{api-id}.execute-api.{region}.amazonaws.com/prod
```

#### Games

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/games` | Alle Games abrufen |
| GET | `/games/{id}` | Einzelnes Game abrufen |
| POST | `/games` | Neues Game erstellen |
| PUT | `/games/{id}` | Game aktualisieren |
| DELETE | `/games/{id}` | Game löschen |

#### Maps

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/games/{gameId}/maps` | Alle Maps eines Games |
| GET | `/maps/{id}` | Einzelne Map abrufen |
| POST | `/games/{gameId}/maps` | Neue Map erstellen |
| PUT | `/maps/{id}` | Map aktualisieren |
| DELETE | `/maps/{id}` | Map löschen |

#### SpawnTypes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/games/{gameId}/spawn-types` | Alle Spawn-Typen eines Games |
| POST | `/games/{gameId}/spawn-types` | Neuen Spawn-Typ erstellen |
| PUT | `/spawn-types/{id}` | Spawn-Typ aktualisieren |
| DELETE | `/spawn-types/{id}` | Spawn-Typ löschen |

#### POIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/maps/{mapId}/pois` | Alle POIs einer Map |
| POST | `/maps/{mapId}/pois` | Neuen POI erstellen |
| PUT | `/pois/{id}` | POI aktualisieren |
| DELETE | `/pois/{id}` | POI löschen |

#### FlightPaths

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/maps/{mapId}/flight-paths` | Alle Flugbahnen einer Map |
| POST | `/maps/{mapId}/flight-paths` | Neue Flugbahn erstellen |
| DELETE | `/flight-paths/{id}` | Flugbahn löschen |

### Future: CDN Static JSON

```
GET /export/{type}.json
```
Exportiert alle Daten als statische JSON-Files für CDN-Hosting.

### Future: Sync-Check

```
GET /api/check-update?lastSync=<timestamp>
Response: { hasUpdates: boolean, latestTimestamp: number }
```

## 7. UI Layout

```
┌─────────────────────────────────────────────────────────┐
│  [Game Selector ▼]  [Map 1] [Map 2] [Map 3]    [+ Map]  │ <- 1 Klick Wechsel, Spawn-Auswahl bleibt
├─────────────────────────────────────────────┬───────────┤
│                                             │ Spawns:   │
│                                             │ ○ Gleiter │
│           MAP + OVERLAY CANVAS              │ ○ Fahrz   │
│                                             │ ○ Tanke   │
│    [Pins]  [Flight Path]  [POI clicks]     │ [+ Type]  │
│                                             │           │
│                                             │ Overlays: │
│                                             │ [Toggle]  │
├─────────────────────────────────────────────┴───────────┤
│  Status: Map "Erangel" geladen | 12 POIs | Overlay: ✗  │
└─────────────────────────────────────────────────────────┘
```

## 8. Offene Fragen / Entscheidungen

### Im Specfile notiert (offen)
- [x] **Overlay-Kalibrierung**: 2 Eck-Anfasser, Seitenverhältnis gelockt ✓ (entschieden)
- [x] **Persistenz**: Serverless Backend mit DynamoDB (entschieden)
- [x] **Caching**: localStorage als Client-Cache (entschieden)
- [x] **Backend-Sprache**: Python FastAPI (entschieden)
- [ ] **Icon-Format**: SVGs oder Font-Icons für Spawn-Typen? (SVGs flexibler, Font-Icons einfacher)
- [ ] **Mehrere Overlays**: Sollen mehrere Overlays pro Karte möglich sein (z.B. verschiedene Season-Maps)?
- [ ] **Share-Funktion**: Export-Link oder nur JSON-Export?
- [ ] **Map-Optimierung**: Sollen große Map-Bilder komprimiert werden?

### Architektur-Entscheidungen (dokumentiert)
- AWS Serverless Stack (Lambda + DynamoDB)
- Python Backend (FastAPI)
- CDN JSON Export Pipeline (Future)
- Homelab-Option über statische JSONs (Future)

### Für später (nicht MVP)
- [ ] **User-Auth**: Wenn geteilt, sollen Nutzer ihre eigenen Karten haben oder öffentlich?
- [ ] **Homelab**: SQLite-Adapter oder reine JSON-Export Lösung?
- [ ] **PWA**: Offline-Fähigkeit als separate App?

## 9. Akzeptanzkriterien MVP

### Must Pass
1. Nutzer kann ein Spiel "PUBG" erstellen
2. Nutzer kann eine Map "Erangel" mit Bild hinzufügen
3. Nutzer kann ein Overlay hochladen und an die Map anpassen
4. Nutzer kann Spawn-Typ "Gleiter" erstellen
5. Nutzer kann POIs durch Klicken auf das Overlay erstellen
6. POIs werden als farbige Punkte auf der Map angezeigt
7. Kartenauswahl ändert nicht die Spawn-Auswahl
8. Alle Daten persistieren in localStorage
9. Demo-Daten: PUBG + Erangel + 3 Gleiter-Spawns laden automatisch

### Nice to Have
- Flugbahn mit 2 Klicks
- Spawn-Rotation

## 10. Projektstruktur

### Full-Stack Architektur

```
web-gamemap-spawn-editor/
├── frontend/                  # SvelteKit App
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/   # UI Komponenten
│   │   │   ├── stores/       # Svelte Stores + localStorage Cache
│   │   │   ├── types/       # TypeScript Interfaces
│   │   │   └── utils/       # Hilfsfunktionen
│   │   └── routes/          # SvelteKit Pages
│   └── static/              # Statische Assets
├── backend/                  # Python FastAPI (Lambda)
│   ├── app/
│   │   ├── main.py         # FastAPI App
│   │   ├── routers/       # API Endpoints
│   │   ├── models/        # Pydantic Models
│   │   └── services/      # Business Logic
│   ├── requirements.txt   # Python Dependencies
│   └── serverless.yml     # AWS Serverless Config
└── infrastructure/          # Terraform/CloudFormation (später)
```

### Frontend (SvelteKit)

```
src/
├── lib/
│   ├── components/
│   │   ├── Map.svelte           # Leaflet-Integration
│   │   ├── OverlayCanvas.svelte # Overlay mit Anfassern
│   │   ├── POIMarker.svelte     # Spawn-Punkte
│   │   ├── FlightPath.svelte    # Flugbahn
│   │   ├── GameSelector.svelte  # Spiel-Auswahl
│   │   ├── MapTabs.svelte       # Map-Register
│   │   ├── SpawnPanel.svelte    # Rechte Leiste
│   │   └── TypeEditor.svelte   # Spawn-Typ bearbeiten
│   ├── stores/
│   │   ├── appState.ts          # Svelte Stores
│   │   └── cache.ts            # localStorage Cache Manager
│   ├── types/
│   │   └── index.ts             # TypeScript Interfaces
│   ├── api/
│   │   └── client.ts           # API Client
│   └── utils/
│       ├── coordinates.ts       # Relative <-> Pixel Konvertierung
│       └── cache.ts            # localStorage Wrapper
├── routes/
│   ├── +page.svelte             # Hauptansicht
│   └── +layout.svelte           # Layout
└── static/
    ├── demo/
    │   └── pubg-erangel.json    # Demo-Daten
    └── icons/                   # Spawn-Type Icons
```

### Backend (Python FastAPI → Lambda)

```
backend/app/
├── main.py              # FastAPI Entry Point (Mangum für Lambda)
├── routers/
│   ├── games.py         # /games Endpoints
│   ├── maps.py          # /maps Endpoints
│   ├── spawn_types.py  # /spawn-types Endpoints
│   ├── pois.py          # /pois Endpoints
│   └── flight_paths.py # /flight-paths Endpoints
├── models/
│   ├── game.py         # Pydantic Models
│   ├── map.py
│   ├── spawn_type.py
│   ├── poi.py
│   └── flight_path.py
├── services/
│   ├── dynamodb.py     # DynamoDB Operations
│   └── cache.py        # Cache Invalidation
└── utils/
    ├── id.py           # UUID Generator
    └── responses.py    # Response Formatter
```

### DynamoDB Tables

| Table | Partition Key | Sort Key | Description |
|-------|--------------|----------|-------------|
| `games` | `id` | - | Alle Games |
| `maps` | `gameId` | `id` | Maps pro Game |
| `spawn-types` | `gameId` | `id` | Spawn-Typen pro Game |
| `pois` | `mapId` | `id` | POIs pro Map |
| `flight-paths` | `mapId` | `id` | Flugbahnen pro Map |

## 11. Nächste Schritte

### Phase 1: Backend (MVP)

1. **AWS Account aufsetzen** (falls nicht vorhanden)
2. **Serverless Framework** installieren
3. **DynamoDB Tables** erstellen (games, maps, spawn-types, pois, flight-paths)
4. **Python FastAPI** Code schreiben
5. **Lambda Handler** konfigurieren (Mangum)
6. **API deployen** und testen

### Phase 2: Frontend (MVP)

1. **SvelteKit Projekt** initialisieren
2. **Leaflet** einbinden
3. **API Client** schreiben mit Cache-Logik
4. **UI Komponenten** entwickeln
5. **localStorage Cache** implementieren

### Phase 3: Integration

1. **API-Calls** mit localStorage-Cache verbinden
2. **Demo-Daten** laden (PUBG + Erangel + Gleiter-Spawns)
3. **Testen** der kompletten User Flows

### Phase 4: Pipeline (Future)

1. **Export Script** schreiben (DynamoDB → JSON)
2. **S3 Bucket** aufsetzen für statische JSONs
3. **CloudFront** als CDN konfigurieren
4. **Trigger** für automatische Exports (Cron/Event)

### Phase 5: Homelab-Option (Future)

1. **Exportierte JSONs** lokal hosten
2. **Optional**: Python API mit SQLite
3. **Docker Compose** für lokalen Betrieb

---

*Erstellt: 2026-04-01*
*Version: 0.2 - Serverless Architektur mit Python Backend*
