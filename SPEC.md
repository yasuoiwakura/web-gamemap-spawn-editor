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
| **Frontend** | SvelteKit | SSG-fähig, client-side Interaktivität, niedrige Einstiegshürde |
| **Mapping** | Leaflet | Einfachste Bibliothek für Overlays, Marker, Skalierung |
| **Persistenz (MVP)** | localStorage/IndexedDB | Lokale Speicherung, kein Backend nötig |
| **Persistenz (Future)** | Serverless API (Cloudflare Workers o.ä.) | Traffic-Sparen durch Client-first |
| **Hosting** | GitHub Pages oder Cloudflare Pages | Kostenlos, CDN-inklusive |

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
- [ ] Games erstellen (Name, Icon)
- [ ] Maps zu Games hinzufügen (Upload)
- [ ] Map-Bild anzeigen
- [ ] Overlay als temporäres Bild hochladen und via 2 Eck-Anfassern skalieren/positionieren (Seitenverhältnis gelockt, wie Profilbild-Crop)
- [ ] **Koordinaten immer relativ zur Map (0-1000)** - keine Pixel!
- [ ] Spawn-Typen erstellen (Name, Icon-Farbe) - **KEINE** Vektor-Icons im MVP
- [ ] POIs durch Klicken auf Overlay erstellen (Koordinaten werden auf Map umgerechnet)
- [ ] Spawn-Typ Filter (nur bestimmte Typen anzeigen)
- [ ] Kartenauswahl oben (1 Klick), Spawn-Auswahl rechts
- [ ] Spawn-Auswahl bleibt bei Kartwechsel erhalten
- [ ] localStorage Persistenz
- [ ] Statische Demo-Daten: PUBG + 1 Map + Gleiter-Spawns

### P1 (Next Release)
- [ ] Vektor-Icons für Spawn-Typen
- [ ] Spawn-Ausrichtung (Rotation)
- [ ] Flugbahn mit 2 Klicks
- [ ] Map-Größe in Metern eingeben
- [ ] Distanz-Linien anzeigen
- [ ] Export/Import als JSON

### P2 (Future)
- [ ] Serverless API für Sync-Check (gibt es neuere Daten?)
- [ ] User-Auth (optional, falls geteilt)
- [ ] Distanz-Flächen (Kreise um POIs)
- [ ] Heatmaps für Spawn-Dichte
- [ ] Mobile-optimierte Ansicht

## 5. Datenmodell

### Game
```typescript
interface Game {
  id: string;
  name: string;
  iconUrl?: string;
  createdAt: number;
}
```

### Map
```typescript
interface GameMap {
  id: string;
  gameId: string;
  name: string;
  imageUrl: string;        // URL oder Base64
  widthPx: number;         // Original-Breite in Pixel
  heightPx: number;        // Original-Höhe in Pixel
  realSizeMeters?: number; // Optional: Kartengröße in Metern
  createdAt: number;
}
```

### Overlay (Temporär - nur für aktive Session)
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

### AppState
```typescript
interface AppState {
  currentGameId: string | null;
  currentMapId: string | null;
  currentSpawnTypeId: string | null; // Bleibt bei Kartwechsel
  visibleSpawnTypeIds: string[];    // Filter
  // Overlay ist TEMPORÄR und wird NICHT in localStorage gespeichert!
  overlay: Overlay | null;
  games: Game[];
  maps: GameMap[];
  spawnTypes: SpawnType[];
  pois: POI[];
  flightPaths: FlightPath[];
}
```

## 6. API Design (Future)

### MVP: Kein Backend, nur localStorage

### Future: Serverless Sync-Check
```
GET /api/check-update?lastSync=<timestamp>
Response: { hasUpdates: boolean, latestTimestamp: number }
```

### Future: Full Sync API
```
GET /api/data
POST /api/data
DELETE /api/data/:type/:id
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
- [ ] **Icon-Format**: SVGs oder Font-Icons für Spawn-Typen? (SVGs flexibler, Font-Icons einfacher)
- [ ] **Mehrere Overlays**: Sollen mehrere Overlays pro Karte möglich sein (z.B. verschiedene Season-Maps)?
- [ ] **Share-Funktion**: Export-Link oder nur JSON-Export?
- [ ] **Map-Optimierung**: Sollen große Map-Bilder komprimiert werden?

### Für später (nicht MVP)
- [ ] **User-Auth**: Wenn geteilt, sollen Nutzer ihre eigenen Karten haben oder öffentlich?
- [ ] **Cloudflare Workers vs. Firebase**: Für Serverless-Backend
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

## 10. Projektstruktur (SvelteKit)

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
│   │   └── appState.ts          # Svelte Stores + localStorage
│   ├── types/
│   │   └── index.ts             # TypeScript Interfaces
│   └── utils/
│       ├── coordinates.ts       # Relative <-> Pixel Konvertierung
│       └── storage.ts            # localStorage Wrapper
├── routes/
│   ├── +page.svelte             # Hauptansicht
│   ├── +layout.svelte           # Layout
│   └── games/
│       └── [gameId]/
│           └── +page.svelte     # Game-Ansicht
└── static/
    ├── demo/
    │   └── pubg-erangel.json    # Demo-Daten
    └── icons/                   # Spawn-Type Icons
```

## 11. Nächste Schritte

1. **Design & Prototyping**: Lo-Fi Wireframes der Hauptansicht
2. **SvelteKit Setup**: Projekt initialisieren, Leaflet einbinden
3. **Datenmodell**: TypeScript Interfaces + localStorage Service
4. **Map-Anzeige**: Leaflet mit Demo-Map zum Laufen bringen
5. **Overlay-Funktion**: Bild-Upload + Transform-Anfassern
6. **POI-System**: Klick-Handler + Spawn-Typen
7. **UI-Layout**: Game/Map/Overlay Selector + Spawn Panel
8. **Persistenz**: Alles in localStorage speichern
9. **Demo-Daten**: PUBG-Erangel mit Gleiter-Spawns
10. **Testing**: Manuelle Tests + ggf. Playwright

---

*Erstellt: 2026-04-01*
*Version: 0.1 (Draft)*
