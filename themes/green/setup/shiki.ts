import { defineShikiSetup } from '@slidev/types'

// Dark code blocks on the light canvas, matching the former Marp theme.
//
// The transformer stamps each block's widest line, in monospace columns, onto the
// <pre> as `--code-cols`. green.css turns that into a per-block font-size, so a
// short snippet reads at body scale while a wide one shrinks just enough to keep
// its longest line unwrapped.

const TAB_WIDTH = 4 // keep in sync with `tab-size` in green.css

// Hangul, CJK, kana, and fullwidth forms occupy two columns in a monospace grid.
const WIDE = /[ᄀ-ᅟ⺀-〾ぁ-㏿㐀-䶿一-鿿ꀀ-꓏ꥠ-꥿가-힣豈-﫿︐-︙︰-﹯＀-｠￠-￦]/u

function columns(line: string): number {
  let n = 0
  for (const ch of line) {
    if (ch === '\t') n += TAB_WIDTH - (n % TAB_WIDTH)
    else n += WIDE.test(ch) ? 2 : 1
  }
  return n
}

export default defineShikiSetup(() => {
  return {
    themes: {
      dark: 'one-dark-pro',
      light: 'one-dark-pro',
    },
    transformers: [
      {
        name: 'green:code-metrics',
        pre(node) {
          const cols = this.source
            .split('\n')
            .reduce((max, line) => Math.max(max, columns(line)), 1)
          const style = node.properties.style
          node.properties.style = style ? `${style};--code-cols:${cols}` : `--code-cols:${cols}`
        },
      },
    ],
  }
})
