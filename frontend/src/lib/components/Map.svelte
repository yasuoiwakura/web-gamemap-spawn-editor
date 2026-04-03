<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import type { GameMap, POI, FlightPath, SpawnType, Overlay } from '$lib/types';

  interface Props {
    map: GameMap;
    pois: POI[];
    flightPaths: FlightPath[];
    spawnTypes: SpawnType[];
    overlay: Overlay | null;
    onmapclick?: (data: { x: number; y: number }) => void;
  }

  let { map, pois, flightPaths, spawnTypes, overlay, onmapclick }: Props = $props();

  let mapContainer: HTMLDivElement;
  let leafletMap: L.Map | null = null;
  let L: typeof import('leaflet') | null = null;
  let imageOverlay: L.ImageOverlay | null = null;
  let overlayImage: L.ImageOverlay | null = null;
  let poiMarkers: L.CircleMarker[] = [];
  let flightPathLines: L.Polyline[] = [];

  function updateMap() {
    if (!leafletMap || !map || !L) return;

    if (imageOverlay) {
      leafletMap.removeLayer(imageOverlay);
    }

    imageOverlay = L.imageOverlay(map.imageUrl, [[0, 0], [1000, 1000]]).addTo(leafletMap);
    leafletMap.setBounds([[0, 0], [1000, 1000]]);
  }

  function updatePOIs() {
    if (!leafletMap || !L) return;

    poiMarkers.forEach(m => leafletMap!.removeLayer(m));
    poiMarkers = [];

    pois.forEach(poi => {
      const spawnType = spawnTypes.find(st => st.id === poi.spawnTypeId);
      const color = spawnType?.color || '#ff0000';
      const radius = spawnType?.iconType === 'arrow' ? 12 : 8;

      const marker = L.circleMarker([1000 - poi.y, poi.x], {
        radius,
        color,
        fillColor: color,
        fillOpacity: 0.8,
        weight: 2,
      });

      if (poi.label) {
        marker.bindPopup(poi.label);
      }

      marker.addTo(leafletMap!);
      poiMarkers.push(marker);
    });
  }

  function updateFlightPaths() {
    if (!leafletMap || !L) return;

    flightPathLines.forEach(l => leafletMap!.removeLayer(l));
    flightPathLines = [];

    flightPaths.forEach(fp => {
      const line = L.polyline(
        [
          [1000 - fp.startY, fp.startX],
          [1000 - fp.endY, fp.endX],
        ],
        {
          color: '#00ff00',
          weight: 3,
          dashArray: '5, 10',
        }
      );
      line.addTo(leafletMap!);
      flightPathLines.push(line);
    });
  }

  function updateOverlayLayer() {
    if (!leafletMap || !L) return;

    if (overlayImage) {
      leafletMap.removeLayer(overlayImage);
      overlayImage = null;
    }

    if (!overlay) return;

    const x = overlay.x;
    const y = 1000 - overlay.y;
    const size = 1000 * overlay.scale;

    overlayImage = L.imageOverlay(overlay.imageUrl, [
      [y, x],
      [y + size, x + size]
    ]).addTo(leafletMap);
  }

  function handleMapClick(e: L.LeafletMouseEvent) {
    const x = Math.round(e.latlng.lng);
    const y = Math.round(1000 - e.latlng.lat);
    
    if (x >= 0 && x <= 1000 && y >= 0 && y <= 1000) {
      onmapclick?.({ x, y });
    }
  }

  $effect(() => {
    if (leafletMap && map) updateMap();
  });

  $effect(() => {
    if (leafletMap && pois) updatePOIs();
  });

  $effect(() => {
    if (leafletMap && flightPaths) updateFlightPaths();
  });

  $effect(() => {
    if (leafletMap && overlay !== undefined) updateOverlayLayer();
  });

  onMount(async () => {
    L = await import('leaflet');
    await import('leaflet/dist/leaflet.css');

    leafletMap = L.map(mapContainer, {
      crs: L.CRS.Simple,
      minZoom: -2,
      maxZoom: 4,
      zoomSnap: 0.5,
      zoomDelta: 0.5,
    });

    const bounds: L.LatLngBoundsExpression = [[0, 0], [1000, 1000]];
    leafletMap.setBounds(bounds);

    updateMap();

    leafletMap.on('click', handleMapClick as L.LeafletEventHandlerFn);
  });

  onDestroy(() => {
    if (leafletMap) {
      leafletMap.remove();
      leafletMap = null;
    }
  });
</script>

<div bind:this={mapContainer} class="w-full h-full min-h-[400px]"></div>

<style>
  :global(.leaflet-container) {
    background: #1a1a1a;
  }
</style>
