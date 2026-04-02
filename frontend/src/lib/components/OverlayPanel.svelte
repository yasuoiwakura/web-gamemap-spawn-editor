<script lang="ts">
  import type { Overlay } from '$lib/types';

  interface Props {
    overlay: Overlay | null;
    onload?: (imageUrl: string) => void;
    onupdate?: (overlay: Overlay) => void;
    onclear?: () => void;
  }

  let { overlay, onload, onupdate, onclear }: Props = $props();

  let isDragging = $state(false);
  let dragHandle = $state<string | null>(null);
  let startX = $state(0);
  let startY = $state(0);
  let startOverlay = $state({ x: 0, y: 0, scale: 1 });

  function handleMouseDown(e: MouseEvent, handle: string) {
    if (!overlay) return;
    e.preventDefault();
    isDragging = true;
    dragHandle = handle;
    startX = e.clientX;
    startY = e.clientY;
    startOverlay = { x: overlay.x, y: overlay.y, scale: overlay.scale };
    
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
  }

  function handleMouseMove(e: MouseEvent) {
    if (!isDragging || !overlay) return;

    const dx = (e.clientX - startX) / 10;
    const dy = (e.clientY - startY) / 10;

    if (dragHandle === 'move') {
      onupdate?.({
        ...overlay,
        x: Math.max(0, Math.min(1000 - 1000 * overlay.scale, startOverlay.x + dx)),
        y: Math.max(0, Math.min(1000 - 1000 * overlay.scale, startOverlay.y + dy)),
      });
    } else if (dragHandle === 'scale') {
      const delta = Math.min(dx, dy) / 100;
      const newScale = Math.max(0.1, Math.min(2, startOverlay.scale + delta));
      onupdate?.({
        ...overlay,
        scale: newScale,
      });
    }
  }

  function handleMouseUp() {
    isDragging = false;
    dragHandle = null;
    window.removeEventListener('mousemove', handleMouseMove);
    window.removeEventListener('mouseup', handleMouseUp);
  }

  function handleFileSelect(e: Event) {
    const input = e.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = () => {
        onload?.(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  }
</script>

<div class="bg-gray-800 p-4 rounded-lg">
  <h3 class="text-lg font-semibold text-white mb-3">Overlay</h3>
  
  {#if overlay}
    <div class="relative w-full h-48 bg-gray-700 rounded overflow-hidden mb-3">
      <img 
        src={overlay.imageUrl} 
        alt="Overlay"
        class="absolute"
        style="
          left: {overlay.x / 10}px;
          top: {overlay.y / 10}px;
          width: {1000 * overlay.scale / 10}px;
          height: {1000 * overlay.scale / 10}px;
        "
        draggable="false"
      />
      
      <div 
        class="absolute w-4 h-4 bg-blue-500 rounded-full cursor-move"
        style="left: {overlay.x / 10}px; top: {overlay.y / 10}px; transform: translate(-50%, -50%)"
        onmousedown={(e) => handleMouseDown(e, 'move')}
        role="button"
        tabindex="0"
      ></div>
      
      <div 
        class="absolute w-4 h-4 bg-green-500 rounded-full cursor-se-resize"
        style="left: {(overlay.x + 1000 * overlay.scale) / 10}px; top: {(overlay.y + 1000 * overlay.scale) / 10}px; transform: translate(-50%, -50%)"
        onmousedown={(e) => handleMouseDown(e, 'scale')}
        role="button"
        tabindex="0"
      ></div>
    </div>
    
    <div class="text-sm text-gray-400 mb-3">
      <p>Position: ({Math.round(overlay.x)}, {Math.round(overlay.y)})</p>
      <p>Scale: {Math.round(overlay.scale * 100)}%</p>
    </div>
    
    <button
      class="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
      onclick={() => onclear?.()}
    >
      Remove Overlay
    </button>
  {:else}
    <label class="block">
      <span class="text-gray-400 text-sm">Upload overlay image:</span>
      <input 
        type="file" 
        accept="image/*" 
        class="block w-full mt-1 text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-blue-600 file:text-white hover:file:bg-blue-700"
        onchange={handleFileSelect}
      />
    </label>
  {/if}
</div>
