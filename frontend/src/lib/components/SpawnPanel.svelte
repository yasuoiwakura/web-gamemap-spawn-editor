<script lang="ts">
  import type { SpawnType } from '$lib/types';

  interface Props {
    spawnTypes: SpawnType[];
    currentSpawnTypeId: string | null;
    visibleSpawnTypeIds: string[];
    onselectSpawnType?: (id: string) => void;
    ontoggleVisibility?: (id: string) => void;
    oncreate?: () => void;
  }

  let { spawnTypes, currentSpawnTypeId, visibleSpawnTypeIds, onselectSpawnType, ontoggleVisibility, oncreate }: Props = $props();

  function selectSpawnType(id: string) {
    onselectSpawnType?.(id);
  }

  function toggleVisibility(id: string) {
    ontoggleVisibility?.(id);
  }
</script>

<div class="bg-gray-800 p-4 rounded-lg">
  <h3 class="text-lg font-semibold text-white mb-3">Spawn Types</h3>
  
  {#if spawnTypes.length === 0}
    <p class="text-gray-400 text-sm">No spawn types yet</p>
  {:else}
    <div class="space-y-2">
      {#each spawnTypes as spawnType}
        <div class="flex items-center gap-2">
          <button
            class="flex-1 flex items-center gap-2 px-3 py-2 rounded transition-colors {currentSpawnTypeId === spawnType.id 
              ? 'bg-gray-600 text-white' 
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}"
            onclick={() => selectSpawnType(spawnType.id)}
          >
            <span 
              class="w-4 h-4 rounded-full" 
              style="background-color: {spawnType.color}"
            ></span>
            {spawnType.name}
          </button>
          <button
            class="px-2 py-1 text-xs rounded {visibleSpawnTypeIds.includes(spawnType.id) 
              ? 'bg-green-600 text-white' 
              : 'bg-gray-600 text-gray-400'}"
            onclick={() => toggleVisibility(spawnType.id)}
          >
            {visibleSpawnTypeIds.includes(spawnType.id) ? '✓' : '○'}
          </button>
        </div>
      {/each}
    </div>
  {/if}

  <button
    class="mt-3 w-full px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
    onclick={() => oncreate?.()}
  >
    + Add Spawn Type
  </button>
</div>
