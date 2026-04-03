<script lang="ts">
  import type { Game } from '$lib/types';

  interface Props {
    games: Game[];
    currentGameId: string | null;
    onselect?: (gameId: string) => void;
  }

  let { games, currentGameId, onselect }: Props = $props();

  function selectGame(gameId: string) {
    onselect?.(gameId);
  }
</script>

<div class="flex gap-2 items-center">
  <label for="game-select" class="text-sm font-medium text-gray-300">Game:</label>
  <select
    id="game-select"
    class="bg-gray-800 border border-gray-700 text-white rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
    value={currentGameId || ''}
    onchange={(e) => selectGame(e.currentTarget.value)}
  >
    <option value="">Select Game</option>
    {#each games as game}
      <option value={game.id}>{game.name}</option>
    {/each}
  </select>
</div>
