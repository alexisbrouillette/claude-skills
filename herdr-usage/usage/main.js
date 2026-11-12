// Usage: Claude Code and Antigravity limits as a small floating window.
// Open: `herdr-app do mod.open '{"name":"usage"}'` (again closes it), or from the palette.
// Data comes from usage.py next to this file (see its header for where it reads from).

import { View, div, svg } from "gpui-kit";
import { v_flex, h_flex } from "gpui-base";
import { appHome, exec, props, closeOverlay, theme } from "herdr";

const ICON = (n) => `mods/usage/${n}.svg`;
const SOURCES = [
  { id: "claude", title: "Claude Code", every: 120 },
  { id: "agy", title: "Antigravity", every: 180 },
];

function left(iso) {
  if (!iso) return "";
  const s = (Date.parse(iso) - Date.now()) / 1000;
  if (!(s > 0)) return "resetting";
  const d = Math.floor(s / 86400), h = Math.floor((s % 86400) / 3600), m = Math.floor((s % 3600) / 60);
  return "resets in " + (d ? `${d}d ${h}h` : h ? `${h}h ${m}m` : `${m}m`);
}

export default class Usage extends View {
  init(_props, cx) {
    this.state = {};   // id -> { data, at, loading }
    for (const s of SOURCES) {
      this.refresh(s.id, cx);
      cx.timer.every(s.every * 1000, (cx) => this.refresh(s.id, cx));
    }
    cx.timer.every(30000, (cx) => cx.notify()); // "resets in" text
  }

  refresh(id, cx) {
    const cur = this.state[id] ?? (this.state[id] = {});
    if (cur.loading) return;
    cur.loading = true;
    cx.notify();
    cx.spawn(async (cx) => {
      try {
        const r = await exec("python3", [`${appHome()}/mods/usage/usage.py`, id], { timeout: 90000 });
        try { cur.data = JSON.parse(r.stdout); cur.at = new Date(); }
        catch { cur.data = { ok: false, error: (r.stderr || r.stdout || "no output").trim().slice(0, 120) }; }
      } catch (e) {
        cur.data = { ok: false, error: String(e).slice(0, 120) };
      } finally {
        cur.loading = false;
        cx.notify();
      }
    });
  }

  // Sidebar mode (props { compact: true }): one line per limit, short labels.
  short(label) {
    return label.replace("Claude and GPT models", "Claude/GPT").replace("Gemini Models", "Gemini")
      .replace("Five Hour", "5h").replace("Weekly", "wk");
  }

  compactRow(t, r) {
    const used = Math.max(0, Math.min(100, r.used ?? 0));
    const color = used >= 85 ? t.blocked : used >= 60 ? t.working : t.done;
    return h_flex().id(`c-${r.label}`).gap(8).items_center().h(18)
      .tooltip(`${r.label}: ${Math.round(used)}% used, ${left(r.resets_at)}`)
      .child(div().flex_none().w(116).truncate().text_color(t.muted).child(this.short(r.label)))
      .child(div().flex_1().h(5).rounded(3).overflow_hidden().bg(t.raised)
        .child(div().h_full().rounded(3).bg(color).w(`${used}%`).transition("width", { duration: 400, easing: "ease-out" })))
      .child(div().flex_none().w(30).text_right().text_color(t.foreground).child(`${Math.round(used)}%`));
  }

  row(t, r) {
    const used = Math.max(0, Math.min(100, r.used ?? 0));
    const color = used >= 85 ? t.blocked : used >= 60 ? t.working : t.done;
    return v_flex().gap(3)
      .child(h_flex().gap(8).items_center()
        .child(div().flex_1().min_w(0).truncate().text_color(t.foreground).child(r.label))
        .child(div().flex_none().font_semibold().text_color(t.foreground).child(`${Math.round(used)}%`)))
      .child(div().h(6).w_full().rounded(3).overflow_hidden().bg(t.raised)
        .child(div().h_full().rounded(3).bg(color).w(`${used}%`).transition("width", { duration: 400, easing: "ease-out" })))
      .child(div().text_size(11).text_color(t.dim).child(left(r.resets_at)));
  }

  section(t, s, compact) {
    const st = this.state[s.id] ?? {};
    const d = st.data;
    const head = h_flex().gap(8).items_center()
      .child(div().flex_1().font_semibold().text_size(compact ? 12 : 14).text_color(t.foreground)
        .child(s.title + (d?.plan ? ` · ${d.plan}` : "")))
      .when(Boolean(st.at) && !st.loading && !compact, (el) => el.child(div().text_size(11).text_color(t.dim)
        .child([st.at.getHours(), st.at.getMinutes()].map((n) => String(n).padStart(2, "0")).join(":"))))
      .child(st.loading
        ? svg(ICON("spinner")).size(13).flex_none().text_color(t.working).spin(900)
        : div().id(`refresh-${s.id}`).flex_none().px(5).rounded(4).text_color(t.dim).cursor_pointer()
            .hover((x) => x.bg(t.hover).text_color(t.foreground))
            .on_click((_e, cx) => { cx.stop_propagation(); this.refresh(s.id, cx); })
            .child("↻"));
    const body = !d
      ? div().text_color(t.dim).child("Loading…")
      : d.ok
        ? v_flex().gap(compact ? 4 : 10).children((d.rows ?? []).map((r) => compact ? this.compactRow(t, r) : this.row(t, r)))
        : div().text_color(t.blocked).child(d.error ?? "Unavailable");
    return v_flex().gap(compact ? 6 : 8).child(head).child(body);
  }

  render(cx) {
    const t = theme();
    const overlay = props()?.overlay;
    if (props()?.compact) {
      return v_flex().id("usage").size_full().overflow_hidden().px(14).py(10).gap(10).text_size(11)
        .children(SOURCES.map((s) => this.section(t, s, true)));
    }
    return v_flex().id("usage").w_full().bg(t.popover).p(14).gap(16).text_size(12)
      .child(h_flex().items_center()
        .child(div().flex_1().text_size(11).text_color(t.dim).child("USAGE (percent used)"))
        .when(Boolean(overlay), (el) => el.child(
          div().id("usage-close").flex_none().p(3).rounded(4).text_color(t.dim).cursor_pointer()
            .hover((x) => x.bg(t.hover).text_color(t.foreground))
            .on_mouse_down("left", (_e, cx) => cx.stop_propagation())
            .on_click((_e, cx) => { cx.stop_propagation(); closeOverlay(overlay); })
            .child(svg(ICON("x")).size(14)))))
      .children(SOURCES.map((s) => this.section(t, s)));
  }
}
