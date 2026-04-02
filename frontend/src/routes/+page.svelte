<script lang="ts">
  import { onMount } from 'svelte';
  import Map from '$lib/components/Map.svelte';
  import GameSelector from '$lib/components/GameSelector.svelte';
  import MapTabs from '$lib/components/MapTabs.svelte';
  import SpawnPanel from '$lib/components/SpawnPanel.svelte';
  import OverlayPanel from '$lib/components/OverlayPanel.svelte';
  import {
    games,
    maps,
    spawnTypes,
    pois,
    flightPaths,
    clientState,
    isLoading,
    error,
    loadGames,
    loadMaps,
    loadSpawnTypes,
    loadPOIs,
    loadFlightPaths,
    createGame,
    createMap,
    createSpawnType,
    createPOI,
    createFlightPath,
    setCurrentGame,
    setCurrentMap,
    setCurrentSpawnType,
    setVisibleSpawnTypes,
    setOverlay,
  } from '$lib/stores';

  let showCreateGame = $state(false);
  let showCreateMap = $state(false);
  let showCreateSpawnType = $state(false);
  let newGameName = $state('');
  let newMapName = $state('');
  let newMapUrl = $state('');
  let newMapWidth = $state(1920);
  let newMapHeight = $state(1080);
  let newSpawnTypeName = $state('');
  let newSpawnTypeColor = $state('#ff0000');
  let flightMode = $state(false);
  let flightStart: { x: number; y: number } | null = $state(null);

  let currentGame = $derived($games.find(g => g.id === $clientState.currentGameId) || null);
  let currentMap = $derived($maps.find(m => m.id === $clientState.currentMapId) || null);

  $effect(() => {
    if ($clientState.currentGameId) {
      loadMaps($clientState.currentGameId);
      loadSpawnTypes($clientState.currentGameId);
    }
  });

  $effect(() => {
    if ($clientState.currentMapId) {
      loadPOIs($clientState.currentMapId);
      loadFlightPaths($clientState.currentMapId);
    }
  });

  onMount(() => {
    loadGames();
  });

  async function handleCreateGame() {
    if (!newGameName.trim()) return;
    await createGame(newGameName.trim());
    newGameName = '';
    showCreateGame = false;
  }

  async function handleCreateMap() {
    if (!newMapName.trim() || !newMapUrl.trim()) return;
    if (!$clientState.currentGameId) return;
    
    await createMap($clientState.currentGameId, {
      name: newMapName.trim(),
      imageUrl: newMapUrl.trim(),
      widthPx: newMapWidth,
      heightPx: newMapHeight,
    });
    
    newMapName = '';
    newMapUrl = '';
    showCreateMap = false;
  }

  async function handleCreateSpawnType() {
    if (!newSpawnTypeName.trim()) return;
    if (!$clientState.currentGameId) return;
    
    await createSpawnType($clientState.currentGameId, {
      name: newSpawnTypeName.trim(),
      color: newSpawnTypeColor,
      iconType: 'dot',
      rotationEnabled: false,
    });
    
    newSpawnTypeName = '';
    newSpawnTypeColor = '#ff0000';
    showCreateSpawnType = false;
  }

  function handleMapClick(event: CustomEvent<{ x: number; y: number }>) {
    const { x, y } = event.detail;
    
    if (flightMode && $clientState.currentMapId) {
      if (!flightStart) {
        flightStart = { x, y };
      } else {
        createFlightPath($clientState.currentMapId, {
          startX: flightStart.x,
          startY: flightStart.y,
          endX: x,
          endY: y,
        });
        flightStart = null;
      }
      return;
    }

    if ($clientState.currentMapId && $clientState.currentSpawnTypeId) {
      createPOI($clientState.currentMapId, {
        spawnTypeId: $clientState.currentSpawnTypeId,
        x,
        y,
      });
    }
  }

  function handleSelectGame(event: CustomEvent<string>) {
    setCurrentGame(event.detail);
  }

  function handleSelectMap(event: CustomEvent<string>) {
    setCurrentMap(event.detail);
  }

  function handleSelectSpawnType(event: CustomEvent<string>) {
    setCurrentSpawnType(event.detail);
  }

  function handleToggleVisibility(event: CustomEvent<string>) {
    const id = event.detail;
    setVisibleSpawnTypes(
      $clientState.visibleSpawnTypeIds.includes(id)
        ? $clientState.visibleSpawnTypeIds.filter(i => i !== id)
        : [...$clientState.visibleSpawnTypeIds, id]
    );
  }

  function handleOverlayLoad(event: CustomEvent<string>) {
    setOverlay({
      imageUrl: event.detail,
      x: 0,
      y: 0,
      scale: 0.5,
    });
  }

  function handleOverlayUpdate(event: CustomEvent<typeof $clientState.overlay>) {
    setOverlay(event.detail);
  }

  function handleOverlayClear() {
    setOverlay(null);
  }

  function toggleFlightMode() {
    flightMode = !flightMode;
    flightStart = null;
  }
</script>

<div class="min-h-screen bg-gray-900 text-white">
  <header class="bg-gray-800 p-4 flex items-center justify-between">
    <h1 class="text-xl font-bold">GameMap Spawn Editor</h1>
    
    <div class="flex items-center gap-4">
      <GameSelector 
        games={$games} 
        currentGameId={$clientState.currentGameId}
        on:select={handleSelectGame}
      />
      
      {#if $clientState.currentGameId}
        <button
          class="px-3 py-2 bg-blue-600 rounded hover:bg-blue-700"
          onclick={() => showCreateGame = true}
        >
          + Game
        </button>
      {/if}
    </div>
  </header>

  {#if currentGame}
    <div class="bg-gray-700 p-3 flex items-center gap-4">
      <span class="text-gray-400">Maps:</span>
      <MapTabs 
        maps={$maps}
        currentMapId={$clientState.currentMapId}
        on:select={handleSelectMap}
      />
      
      {#if $clientState.currentGameId}
        <button
          class="px-3 py-2 bg-green-600 rounded hover:bg-green-700"
          onclick={() => showCreateMap = true}
        >
          + Map
        </button>
      {/if}
      
      <div class="ml-auto flex items-center gap-2">
        <button
          class="px-3 py-2 rounded {flightMode ? 'bg-yellow-600' : 'bg-gray-600'}"
          onclick={toggleFlightMode}
        >
          {flightMode ? 'Flight Mode (2 clicks)' : 'Flight Mode'}
        </button>
      </div>
    </div>
  {/if}

  <main class="flex h-[calc(100vh-140px)]">
    <div class="flex-1 relative">
      {#if currentMap}
        <Map 
          map={currentMap}
          pois={$pois}
          flightPaths={$flightPaths}
          spawnTypes={$spawnTypes}
          overlay={$clientState.overlay}
          on:mapClick={handleMapClick}
        />
      {:else}
        <div class="flex items-center justify-center h-full text-gray-500">
          {#if currentGame}
            Select or create a map
          {:else}
            Select or create a game first
          {/if}
        </div>
      {/if}
    </div>

    <aside class="w-64 bg-gray-800 p-4 overflow-y-auto space-y-4">
      <SpawnPanel
        spawnTypes={$spawnTypes}
        currentSpawnTypeId={$clientState.currentSpawnTypeId}
        visibleSpawnTypeIds={$clientState.visibleSpawnTypeIds}
        on:selectSpawnType={handleSelectSpawnType}
        on:toggleVisibility={handleToggleVisibility}
        on:create={() => showCreateSpawnType = true}
      />
      
      <OverlayPanel
        overlay={$clientState.overlay}
        on:load={handleOverlayLoad}
        on:update={handleOverlayUpdate}
        on:clear={handleOverlayClear}
      />
    </aside>
  </main>

  {#if $isLoading}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="text-white text-xl">Loading...</div>
    </div>
  {/if}

  {#if $error}
    <div class="fixed bottom-4 right-4 bg-red-600 text-white px-4 py-2 rounded">
      {$error}
    </div>
  {/if}
</div>

{#if showCreateGame}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-gray-800 p-6 rounded-lg w-96">
      <h2 class="text-xl font-bold mb-4">Create Game</h2>
      <input
        type="text"
        bind:value={newGameName}
        placeholder="Game name"
        class="w-full bg-gray-700 text-white px-3 py-2 rounded mb-4"
      />
      <div class="flex gap-2 justify-end">
        <button class="px-4 py-2 bg-gray-600 rounded" onclick={() => showCreateGame = false}>Cancel</button>
        <button class="px-4 py-2 bg-blue-600 rounded" onclick={handleCreateGame}>Create</button>
      </div>
    </div>
  </div>
{/if}

{#if showCreateMap}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-gray-800 p-6 rounded-lg w-[500px]">
      <h2 class="text-xl font-bold mb-4">Create Map</h2>
      <div class="space-y-3">
        <input
          type="text"
          bind:value={newMapName}
          placeholder="Map name"
          class="w-full bg-gray-700 text-white px-3 py-2 rounded"
        />
        <input
          type="text"
          bind:value={newMapUrl}
          placeholder="Map image URL"
          class="w-full bg-gray-700 text-white px-3 py-2 rounded"
        />
        <div class="flex gap-2">
          <input
            type="number"
            bind:value={newMapWidth}
            placeholder="Width"
            class="flex-1 bg-gray-700 text-white px-3 py-2 rounded"
          />
          <input
            type="number"
            bind:value={newMapHeight}
            placeholder="Height"
            class="flex-1 bg-gray-700 text-white px-3 py-2 rounded"
          />
        </div>
      </div>
      <div class="flex gap-2 justify-end mt-4">
        <button class="px-4 py-2 bg-gray-600 rounded" onclick={() => showCreateMap = false}>Cancel</button>
        <button class="px-4 py-2 bg-green-600 rounded" onclick={handleCreateMap}>Create</button>
      </div>
    </div>
  </div>
{/if}

{#if showCreateSpawnType}
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-gray-800 p-6 rounded-lg w-96">
      <h2 class="text-xl font-bold mb-4">Create Spawn Type</h2>
      <div class="space-y-3">
        <input
          type="text"
          bind:value={newSpawnTypeName}
          placeholder="Name"
          class="w-full bg-gray-700 text-white px-3 py-2 rounded"
        />
        <div class="flex items-center gap-2">
          <label class="text-gray-400">Color:</label>
          <input
            type="color"
            bind:value={newSpawnTypeColor}
            class="w-10 h-10 rounded cursor-pointer"
          />
        </div>
      </div>
      <div class="flex gap-2 justify-end mt-4">
        <button class="px-4 py-2 bg-gray-600 rounded" onclick={() => showCreateSpawnType = false}>Cancel</button>
        <button class="px-4 py-2 bg-blue-600 rounded" onclick={handleCreateSpawnType}>Create</button>
      </div>
    </div>
  </div>
{/if}