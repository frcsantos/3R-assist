import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const components = {
  h1: ({ children }) => (
    <h1 className="mb-card-gap font-headline-lg text-headline-xl text-on-surface">
      {children}
    </h1>
  ),
  h2: ({ children }) => (
    <h2 className="mb-element-gap mt-section-gap font-card-title text-card-title text-on-surface first:mt-0">
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 className="mb-fine-gap mt-card-gap font-label-caps text-label-caps uppercase text-on-surface-variant first:mt-0">
      {children}
    </h3>
  ),
  h4: ({ children }) => (
    <h4 className="mb-fine-gap mt-element-gap font-card-title text-card-title text-on-surface-variant first:mt-0">
      {children}
    </h4>
  ),
  p: ({ children }) => (
    <p className="mb-element-gap font-body-base text-body-base text-on-surface last:mb-0">
      {children}
    </p>
  ),
  ul: ({ children }) => (
    <ul className="mb-element-gap list-disc space-y-fine-gap pl-6 font-body-base text-body-base text-on-surface last:mb-0">
      {children}
    </ul>
  ),
  ol: ({ children }) => (
    <ol className="mb-element-gap list-decimal space-y-fine-gap pl-6 font-body-base text-body-base text-on-surface last:mb-0">
      {children}
    </ol>
  ),
  li: ({ children }) => <li className="leading-relaxed">{children}</li>,
  blockquote: ({ children }) => (
    <blockquote className="mb-element-gap border-l-4 border-info-border bg-info-bg px-card-gap py-element-gap font-body-base text-body-base text-info-text last:mb-0">
      {children}
    </blockquote>
  ),
  hr: () => <hr className="my-section-gap border-border-subtle" />,
  a: ({ href, children }) => (
    <a
      href={href}
      className="font-medium text-info-text underline decoration-info-border underline-offset-2 hover:opacity-80"
      target={href?.startsWith('http') ? '_blank' : undefined}
      rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
    >
      {children}
    </a>
  ),
  strong: ({ children }) => (
    <strong className="font-medium text-on-surface">{children}</strong>
  ),
  em: ({ children }) => <em className="italic">{children}</em>,
  code: ({ className, children }) => {
    if (className) {
      return <code className={className}>{children}</code>
    }

    return (
      <code className="rounded border border-border-subtle bg-surface-container px-1 py-0.5 font-monospace-data text-monospace-data text-on-surface">
        {children}
      </code>
    )
  },
  pre: ({ children }) => (
    <pre className="mb-element-gap overflow-x-auto rounded-lg border border-border-subtle bg-surface-container-low p-card-gap font-monospace-data text-monospace-data text-on-surface last:mb-0">
      {children}
    </pre>
  ),
  table: ({ children }) => (
    <div className="mb-element-gap overflow-x-auto rounded-lg border border-border-subtle last:mb-0">
      <table className="w-full border-collapse text-left">{children}</table>
    </div>
  ),
  thead: ({ children }) => (
    <thead className="bg-surface-container font-small-label text-small-label uppercase text-on-surface-variant">
      {children}
    </thead>
  ),
  tbody: ({ children }) => (
    <tbody className="divide-y divide-border-subtle font-body-base text-body-base">
      {children}
    </tbody>
  ),
  tr: ({ children }) => (
    <tr className="hover:bg-surface-container-low transition-colors">{children}</tr>
  ),
  th: ({ children }) => (
    <th className="px-container-padding py-3 font-medium">{children}</th>
  ),
  td: ({ children }) => (
    <td className="px-container-padding py-3 text-on-surface-variant">{children}</td>
  ),
}

export default function MarkdownRenderer({ children, className = '' }) {
  if (!children) return null

  return (
    <article className={`markdown-renderer ${className}`.trim()}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {children}
      </ReactMarkdown>
    </article>
  )
}
