<script lang="ts">
  import type { GameMap } from '$lib/types';

  interface Props {
    maps: GameMap[];
    currentMapId: string | null;
    onselect?: (mapId: string) => void;
  }

  let { maps, currentMapId, onselect }: Props = $props();

  function selectMap(mapId: string) {
    onselect?.(mapId);
  }
</script>

<div class="flex gap-2 items-center overflow-x-auto">
  {#each maps as map}
    <button
      class="px-4 py-2 rounded transition-colors {currentMapId === map.id 
        ? 'bg-blue-600 text-white' 
        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}"
      onclick={() => selectMap(map.id)}
    >
      {map.name}
    </button>
  {/each}
</div>
