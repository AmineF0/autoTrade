import { useMemo } from 'react';

interface MarkdownMessageProps {
  content: string;
}

export function MarkdownMessage({ content }: MarkdownMessageProps) {
  const formattedContent = useMemo(() => {
    return content
      // Bold text with **
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Italic text with *
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      // Code blocks with ```
      .replace(/```(.*?)```/g, '<code>$1</code>')
      // Inline code with `
      .replace(/`(.*?)`/g, '<code>$1</code>')
      // Lists with -
      .replace(/^- (.*?)$/gm, '• $1')
      // Headers with #
      .replace(/^# (.*?)$/gm, '<h1>$1</h1>')
      .replace(/^## (.*?)$/gm, '<h2>$1</h2>')
      .replace(/^### (.*?)$/gm, '<h3>$1</h3>')
      .replace(/^#### (.*?)$/gm, '<h4>$1</h4>')
      .replace(/^##### (.*?)$/gm, '<h5>$1</h5>')
      .replace(/\n/g, '<br />');
  }, [content]);

  return (
    <div 
      className="prose dark:prose-invert max-w-none"
      dangerouslySetInnerHTML={{ __html: formattedContent }}
    />
  );
}