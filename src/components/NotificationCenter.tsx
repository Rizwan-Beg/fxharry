import React, { useState } from 'react';
import { Bell, X, AlertTriangle, Info, CheckCircle } from 'lucide-react';

interface NotificationCenterProps {
  notifications: Array<{
    id: string;
    type: 'info' | 'warning' | 'error' | 'success';
    title: string;
    message: string;
    timestamp: string;
  }>;
}

export function NotificationCenter({ notifications = [] }: NotificationCenterProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  const getIcon = (type: string) => {
    switch (type) {
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-400" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-400" />;
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      default:
        return <Info className="h-4 w-4 text-blue-400" />;
    }
  };

  const getBackgroundColor = (type: string) => {
    switch (type) {
      case 'warning':
        return 'bg-yellow-900 border-yellow-700';
      case 'error':
        return 'bg-red-900 border-red-700';
      case 'success':
        return 'bg-green-900 border-green-700';
      default:
        return 'bg-blue-900 border-blue-700';
    }
  };

  const visibleNotifications = notifications.filter(n => !dismissed.has(n.id));
  const unreadCount = visibleNotifications.length;

  const dismissNotification = (id: string) => {
    setDismissed(prev => new Set([...prev, id]));
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-400 hover:text-white transition-colors"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-gray-800 border border-gray-700 rounded-lg shadow-lg z-50">
          <div className="p-4 border-b border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Notifications</h3>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-white"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {visibleNotifications.length === 0 ? (
              <div className="p-4 text-center text-gray-400">
                <Bell className="h-12 w-12 mx-auto mb-2 text-gray-600" />
                <p>No notifications</p>
              </div>
            ) : (
              <div className="space-y-2 p-2">
                {visibleNotifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`p-3 rounded-lg border ${getBackgroundColor(notification.type)}`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3">
                        {getIcon(notification.type)}
                        <div className="flex-1 min-w-0">
                          <h4 className="text-sm font-medium text-white">
                            {notification.title}
                          </h4>
                          <p className="text-sm text-gray-300 mt-1">
                            {notification.message}
                          </p>
                          <p className="text-xs text-gray-400 mt-2">
                            {new Date(notification.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => dismissNotification(notification.id)}
                        className="text-gray-400 hover:text-white ml-2"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {visibleNotifications.length > 0 && (
            <div className="p-3 border-t border-gray-700">
              <button
                onClick={() => {
                  visibleNotifications.forEach(n => dismissNotification(n.id));
                }}
                className="w-full text-sm text-gray-400 hover:text-white transition-colors"
              >
                Dismiss All
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}