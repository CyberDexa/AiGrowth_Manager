'use client';

import { HelpCircle } from 'lucide-react';
import { Tooltip } from './Tooltip';

interface HelpIconProps {
  content: string;
  side?: 'top' | 'right' | 'bottom' | 'left';
}

export default function HelpIcon({ content, side = 'top' }: HelpIconProps) {
  return (
    <Tooltip content={content} side={side}>
      <button
        type="button"
        className="inline-flex items-center justify-center text-gray-400 hover:text-gray-600 transition-colors"
        aria-label="Help"
      >
        <HelpCircle className="h-4 w-4" />
      </button>
    </Tooltip>
  );
}
