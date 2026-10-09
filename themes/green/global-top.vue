<script setup lang="ts">
import { useSlideContext } from '@slidev/client'

// Global layers sit outside SlideWrapper, so $page is not injected here;
// nav is per-slide in print/export mode, giving the right number in PDFs too.
const { $slidev } = useSlideContext()
</script>

<template>
  <div class="slidev-page-no">{{ $slidev.nav.currentPage }}</div>
</template>
