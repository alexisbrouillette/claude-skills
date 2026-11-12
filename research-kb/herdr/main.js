// Knowledge base: sources (papers, blog posts) saved by research-kb, newest first.
// Open/close: `herdr-app do mod.open '{"name":"knowledge"}'`. Click an entry to read the source in your browser.
// Data: ~/.research-kb/entries.jsonl, written by ~/.claude/skills/research-kb/scripts/kb.py.

import { View, div, svg } from "gpui-kit";
import { v_flex, h_flex, InputState, Input } from "gpui-base";
import { exec, home, props, closeOverlay, readTextFile, theme } from "herdr";

const KIND = { paper: "paper", blog: "blog", docs: "docs", other: "other" };

function ago(iso) {
  const d = Math.floor((Date.now() - Date.parse(iso)) / 86400000);
  if (!(d >= 0)) return "";
  return d === 0 ? "today" : d === 1 ? "yesterday" : d < 30 ? `${d}d ago` : iso.slice(0, 10);
}

function who(e) {
  const a = e.authors ?? [];
  if (!a.length) return "";
  const last = a[0].trim().split(/\s+/).pop();
  return a.length > 1 ? `${last} et al.` : last;
}

export default class Knowledge extends View {
  init(_props, cx) {
    this.entries = [];
    this.raw = null;
    this.filter = "";
    this.input = InputState.new({ placeholder: "Search title, why, project, tags…" });
    this.input.on("change", (_e, cx) => { this.filter = this.input.value().toLowerCase(); cx.notify(); });
    this.load(cx);
    cx.timer.every(3000, (cx) => this.load(cx));
  }

  load(cx) {
    cx.spawn(async (cx) => {
      const text = await readTextFile(`${home()}/.research-kb/entries.jsonl`);
      if (text === this.raw) return;
      this.raw = text;
      const out = [];
      for (const line of (text ?? "").split("\n")) {
        if (!line.trim()) continue;
        try { out.push(JSON.parse(line)); } catch { /* half-written line */ }
      }
      this.entries = out.sort((a, b) => (b.added ?? "").localeCompare(a.added ?? ""));
      cx.notify();
    });
  }

  card(t, e) {
    const meta = [who(e), e.year, e.project, ago(e.added)].filter(Boolean).join(" · ");
    return v_flex().id(`e-${e.id}`).gap(4).px(12).py(10).rounded(6).cursor_pointer()
      .hover((s) => s.bg(t.hover))
      .tooltip(e.url)
      .on_click(() => exec("xdg-open", [e.url]))
      .child(h_flex().gap(8).items_start()
        .child(div().flex_1().min_w(0).font_semibold().text_size(13).text_color(t.foreground).child(e.title))
        .child(div().flex_none().text_size(10).px(6).py(1).rounded(4).bg(t.raised).text_color(t.muted).child(KIND[e.kind] ?? "other"))
        .child(div().flex_none().text_size(12).text_color(e.verified ? t.done : t.blocked)
          .tooltip(e.verified ? `Verified via ${e.verified_by}` : "Could not be verified")
          .child(e.verified ? "✓" : "?")))
      .child(div().text_size(11).text_color(t.dim).child(meta))
      .when(Boolean(e.why), (el) => el.child(div().text_size(12).text_color(t.muted).child(e.why)))
      .child(div().truncate().text_size(11).text_color(t.accent).child("↗ " + e.url));
  }

  render(cx) {
    const t = theme();
    const q = this.filter;
    const shown = q
      ? this.entries.filter((e) => [e.title, e.why, e.project, (e.tags ?? []).join(" "), (e.authors ?? []).join(" ")].join(" ").toLowerCase().includes(q))
      : this.entries;
    const overlay = props()?.overlay;
    return v_flex().id("kb").size_full().bg(t.popover).text_size(12)
      .child(h_flex().gap(8).items_center().px(14).pt(12).pb(8)
        .child(div().flex_1().font_semibold().text_size(14).text_color(t.foreground).child("Knowledge base"))
        .child(div().text_size(11).text_color(t.dim).child(`${shown.length}${q ? ` of ${this.entries.length}` : ""} sources`))
        .when(Boolean(overlay), (el) => el.child(
          div().id("kb-close").flex_none().p(3).rounded(4).text_color(t.dim).cursor_pointer()
            .hover((x) => x.bg(t.hover).text_color(t.foreground))
            .on_mouse_down("left", (_e, cx) => cx.stop_propagation())
            .on_click((_e, cx) => { cx.stop_propagation(); closeOverlay(overlay); })
            .child(svg("mods/knowledge/x.svg").size(14)))))
      .child(div().px(14).pb(8).child(
        div().h(28).px(8).rounded(6).bg(t.raised).flex().items_center()
          .child(Input.new(this.input).flex_1().h_full().text_size(12).text_color(t.foreground))))
      .child(v_flex().id("kb-list").flex_1().min_h(0).overflow_y_scrollbar().px(6).pb(8).gap(2)
        .when(shown.length === 0, (el) => el.child(div().p(14).text_color(t.dim).child(
          this.raw === null ? "No knowledge base yet. Sources appear here as research-kb saves them." : "Nothing matches.")))
        .children(shown.map((e) => this.card(t, e))));
  }
}
