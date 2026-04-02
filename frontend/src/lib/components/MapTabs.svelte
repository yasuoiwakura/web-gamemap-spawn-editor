<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { GameMap } from '$lib/types';

  export let maps: GameMap[] = [];
  export let currentMapId: string | null = null;

  const dispatch = createEventDispatcher();

  function selectMap(mapId: string) {
    dispatch('select', mapId);
  }
</script>

<div class="flex gap-2 items-center overflow-x-auto">
  {#each maps as map}
    <button
      class="px-4 py-2 rounded transition-colors {currentMapId === map.id 
        ? 'bg-blue-600 text-white' 
        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}"
      on:click={() => selectMap(map.id)}
    >
      {map.name}
    </button>
  {/each}
</div>