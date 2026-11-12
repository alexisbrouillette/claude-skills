// Task progress: ONE shared Herdr pane showing every task (cards), read from the hub file written by progress.py.
// Opened by `progress.py open FILE` beside the agent's pane:
//   pane.split { direction: "down", mod: "task-progress", props: { file } }
// Source of truth: ~/.claude/skills/task-progress/herdr (copied here by progress.py).

import { View, div, svg } from "gpui-kit";
import { v_flex, h_flex } from "gpui-base";
import { props, readTextFile, run, theme, panes } from "herdr";

const ICON = (name) => `mods/task-progress/${name}.svg`;

function fmt(s) {
  s = Math.max(0, Math.floor(s));
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
  const p2 = (n) => String(n).padStart(2, "0");
  return h ? `${h}:${p2(m)}:${p2(sec)}` : `${p2(m)}:${p2(sec)}`;
}

function clock(ts) {
  const d = new Date(ts * 1000);
  return [d.getHours(), d.getMinutes(), d.getSeconds()].map((n) => String(n).padStart(2, "0")).join(":");
}

export default class TaskProgress extends View {
  init(_props, cx) {
    this.raw = null;
    this.data = null;
    this.missing = false;
    this.trackW = 0;
    cx.timer.every(250, (cx) => this.poll(cx));
    // Elapsed / ETA text: once a second, only while running.
    cx.timer.every(1000, (cx) => { if ((this.data?.tasks ?? []).some((t) => t.status === "running")) cx.notify(); });
    this.poll(cx);
  }

  poll(cx) {
    const file = props()?.file;
    if (!file || this.reading) return;
    this.reading = true;
    cx.spawn(async (cx) => {
      try {
        const text = await readTextFile(file);
        if (text === this.raw) return;
        this.raw = text;
        this.missing = text == null;
        if (text != null) {
          try { this.data = JSON.parse(text); } catch { return; } // mid-write: keep the last good one
        }
        cx.notify();
      } finally {
        this.reading = false;
      }
    });
  }

  // progress.py records the pane it split into the state file as "pane".
  myPane() {
    const id = this.data?.pane ?? props()?.pane;
    return panes().some((p) => p.pane === id) ? id : null;
  }

  bar(t, d, color) {
    const pct = d.percent;
    const track = div()
      .id(`track-${this.cardIdx ?? 0}`)
      .relative()
      .flex_1()
      .h(8)
      .rounded(4)
      .overflow_hidden()
      .bg(t.raised)
      .on_size_change((size, cx) => { if (size.width !== this.trackW) { this.trackW = size.width; cx.notify(); } });
    if (pct == null) {
      const w = Math.max(24, Math.round(this.trackW / 5));
      return track.child(
        div().absolute().top(0).h_full().w(w).rounded(4).bg(color)
          .loop("left", { from: -w, to: Math.max(0, this.trackW), period: 2400, easing: "ease-in-out" }));
    }
    return track.child(
      div().h_full().rounded(4).bg(color).w(`${Math.max(0, Math.min(100, pct))}%`)
        .transition("width", { duration: 350, easing: "ease-out" }));
  }

  card(t, d, i, pane) {
    const status = d.status ?? "running";
    const color = status === "done" ? t.done : status === "failed" ? t.blocked : t.working;
    const now = Date.now() / 1000;
    const el = (d.end ?? now) - (d.start ?? now);
    const pct = d.percent;
    let meta = `elapsed ${fmt(el)}`;
    if (status === "running" && pct != null && pct >= 3) meta += `  ·  ~${fmt((el * (100 - pct)) / pct)} left`;
    this.cardIdx = i;

    const icon = status === "running"
      ? svg(ICON("spinner")).size(16).flex_none().text_color(color).spin(900)
      : svg(ICON(status === "done" ? "circle-check" : "circle-x")).size(16).flex_none().text_color(color);

    const header = h_flex().gap(10).items_center()
      .child(icon)
      .child(div().flex_1().min_w(0).truncate().font_semibold().text_size(14).text_color(t.foreground).child(d.title || "Task"))
      .child(div().flex_none().text_size(11).text_color(t.dim).child(meta))
      .when(i === 0 && Boolean(pane), (e) => e.child(
        div().id("close").flex_none().p(3).rounded(4).text_color(t.dim).cursor_pointer()
          .hover((s) => s.bg(t.hover).text_color(t.foreground))
          .on_click((_e, cx) => { cx.stop_propagation(); run("pane.close", { pane }); })
          .child(svg(ICON("x")).size(14))));

    const step = status === "running"
      ? h_flex().gap(8).items_center()
          .child(div().flex_none().text_color(color).child("▸"))
          .child(div().flex_1().min_w(0).truncate().text_color(t.foreground).child(d.step ?? ""))
      : div().truncate().font_semibold().text_color(color)
          .child(d.msg || (status === "done" ? "Completed" : "Failed"));

    const log = status === "running" ? (d.log ?? []).slice(-3) : [];
    return v_flex().id(`card-${i}`).gap(6).flex_none()
      .when(i > 0, (e) => e.mt(6).pt(10).border_t(1).border_color(t.border))
      .child(header)
      .when(Boolean(d.desc), (e) => e.child(div().truncate().text_size(12).text_color(t.muted).child(d.desc)))
      .when(pct != null, (e) => e.child(
        h_flex().gap(10).items_center()
          .child(this.bar(t, d, color))
          .child(div().flex_none().w(40).text_right().font_semibold().text_color(t.foreground).child(`${Math.round(pct)}%`))))
      .child(step)
      .children(log.map(([ts, line], j) =>
        h_flex().id(`log-${i}-${j}`).gap(10).text_size(12)
          .child(div().flex_none().text_color(t.dim).child(clock(ts)))
          .child(div().flex_1().min_w(0).truncate().text_color(t.muted).child(line))));
  }

  render(cx) {
    const t = theme();
    const root = v_flex().id("root").size_full().overflow_hidden().bg(t.background).p(16).gap(4).text_size(13);
    const now = Date.now() / 1000;
    const tasks = (this.data?.tasks ?? []).filter((d) => d.status === "running" || !d.end || now - d.end < 120);

    if (!this.data || tasks.length === 0) {
      return root.items_center().justify_center().text_color(t.dim)
        .child(this.missing ? "No progress file yet…" : "No active tasks");
    }
    const pane = this.myPane();
    return root.children(tasks.map((d, i) => this.card(t, d, i, pane)));
  }
}
