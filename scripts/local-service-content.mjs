// Keep planning copy in its authored guide, without repeating it in the local
// service overview. Limit removal to exact paragraphs in this known intro slot;
// curated local evidence, service lists, FAQs and disclosures stay intact.
export function removeRepeatedLocalIntro(html) {
  const guide = html.match(/<!-- service-guide:start -->([\s\S]*?)<!-- service-guide:end -->/);
  if (!guide) return html;
  const guideParagraphs = new Set([...guide[1].matchAll(/<p\b[^>]*>([\s\S]*?)<\/p>/g)].map(match => match[1]));
  return html.replace(
    /(<h2>Local [^<]+ Services<\/h2>)((?:\s*<p>[^<]+<\/p>)+)(\s*<div class="local-grid">)/g,
    (_, heading, paragraphs, grid) => heading + paragraphs.replace(
      /<p>([^<]+)<\/p>/g,
      (paragraph, text) => guideParagraphs.has(text) ? '' : paragraph,
    ) + grid,
  );
}
