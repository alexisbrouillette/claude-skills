// Sidebar button: opens/closes the Knowledge base window (mod "knowledge"), with the number of saved sources.
import { View, div, svg } from "gpui-kit";
import { h_flex } from "gpui-base";
import { home, readTextFile, run, theme } from "herdr";

export default class KbButton extends View {
  init(_props, cx) {
    this.count = null;
    this.raw = null;
    this.load(cx);
    cx.timer.every(5000, (cx) => this.load(cx));
  }

  load(cx) {
    cx.spawn(async (cx) => {
      const text = await readTextFile(`${home()}/.research-kb/entries.jsonl`);
      if (text === this.raw) return;
      this.raw = text;
      this.count = (text ?? "").split("\n").filter((l) => l.trim()).length;
      cx.notify();
    });
  }

  render(cx) {
    const t = theme();
    return h_flex().id("kb-open").size_full().px(14).gap(8).items_center().cursor_pointer()
      .text_size(12).text_color(t.muted)
      .hover((s) => s.bg(t.hover).text_color(t.foreground))
      .on_click(() => run("mod.open", { name: "knowledge" }))
      .child(svg("mods/kb-button/book-open.svg").size(14).flex_none())
      .child(div().flex_1().child("Knowledge base"))
      .when(this.count != null, (el) => el.child(div().text_size(11).text_color(t.dim).child(String(this.count))));
  }
}
