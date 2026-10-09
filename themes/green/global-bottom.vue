<script setup lang="ts">
import { onMounted, onBeforeUnmount } from 'vue'

// Vertical half of the code auto-fit (green.css owns the horizontal half).
//
// green.css sizes each block to its own longest line, but how tall a block may
// grow depends on how much room the rest of the slide leaves — and CSS cannot
// add up the heights of sibling elements. So this measures it: `--code-scale`
// shrinks every block on a slide together, and we search for the largest scale
// the slide still fits. Below ~0.5 the `--code-size-min` floor takes over, which
// is the size code was before auto-fit existed, so a slide that was already
// packed full is never made worse.

const MIN_SCALE = 0.4
const STEPS = 7 // settles within ~0.005 of the largest scale that fits

function fits(layout: HTMLElement) {
  return layout.scrollHeight <= layout.clientHeight
}

function fit(layout: HTMLElement) {
  if (!layout.querySelector('.slidev-code')) return
  layout.style.removeProperty('--code-scale')
  if (fits(layout)) return

  let lo = MIN_SCALE
  let hi = 1
  for (let i = 0; i < STEPS; i++) {
    const mid = (lo + hi) / 2
    layout.style.setProperty('--code-scale', `${mid}`)
    if (fits(layout)) lo = mid
    else hi = mid
  }
  layout.style.setProperty('--code-scale', `${lo}`)
}

let queued = false
function fitAll() {
  if (queued) return
  queued = true
  requestAnimationFrame(() => {
    queued = false
    document.querySelectorAll<HTMLElement>('.slidev-layout').forEach(fit)
  })
}

// Slides mount as you navigate (and all at once when exporting), so watch for
// them rather than fitting only what is on screen at startup. childList only —
// observing attributes would re-trigger on the inline style we just wrote.
const observer = typeof MutationObserver !== 'undefined' ? new MutationObserver(fitAll) : null

onMounted(() => {
  fitAll()
  document.fonts?.ready.then(fitAll) // glyph metrics change what fits
  observer?.observe(document.body, { childList: true, subtree: true })
  window.addEventListener('resize', fitAll)
})

onBeforeUnmount(() => {
  observer?.disconnect()
  window.removeEventListener('resize', fitAll)
})
</script>

<template>
  <span hidden />
</template>
