"use client";

interface TopicSuggestionsProps {
  angles: string[];
  hooks: string[];
  onSelectHook?: (hook: string) => void;
}

export function TopicSuggestions({ angles, hooks, onSelectHook }: TopicSuggestionsProps) {
  if (angles.length === 0 && hooks.length === 0) return null;

  return (
    <div className="space-y-4">
      {angles.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Trending Angles</h4>
          <ul className="space-y-1">
            {angles.map((angle, i) => (
              <li key={i} className="text-sm text-gray-600 pl-3 border-l-2 border-blue-200">
                {angle}
              </li>
            ))}
          </ul>
        </div>
      )}
      {hooks.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Hook Ideas</h4>
          <ul className="space-y-1">
            {hooks.map((hook, i) => (
              <li
                key={i}
                className="text-sm text-gray-600 pl-3 border-l-2 border-green-200 cursor-pointer hover:bg-green-50 rounded py-1"
                onClick={() => onSelectHook?.(hook)}
              >
                {hook}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
