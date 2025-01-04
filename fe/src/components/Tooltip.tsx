import { ReactNode } from 'react';

interface TooltipProps {
  children: ReactNode;
  content: string;
}

export function Tooltip({ children, content }: TooltipProps) {
  return (
    <div className="relative group">
      {children}
      <div className="absolute z-10 invisible group-hover:visible bg-gray-900 text-white text-sm rounded-lg py-2 px-3 right-0 min-w-[200px] -top-2 transform -translate-y-full opacity-0 group-hover:opacity-100 transition-all duration-200">
        {content}
        <div className="absolute bottom-0 right-4 transform translate-y-1/2 rotate-45 w-2 h-2 bg-gray-900"></div>
      </div>
    </div>
  );
}