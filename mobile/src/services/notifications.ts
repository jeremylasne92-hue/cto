import PushNotification from 'react-native-push-notification';
import { Platform } from 'react-native';

class NotificationService {
  configure(): void {
    PushNotification.configure({
      onRegister: (token) => {
        console.log('Notification token:', token);
      },
      onNotification: (notification) => {
        console.log('Notification received:', notification);
      },
      permissions: {
        alert: true,
        badge: true,
        sound: true,
      },
      popInitialNotification: true,
      requestPermissions: Platform.OS === 'ios',
    });

    this.createChannel();
  }

  private createChannel(): void {
    PushNotification.createChannel(
      {
        channelId: 'srs-reviews',
        channelName: 'SRS Reviews',
        channelDescription: 'Notifications for due SRS reviews',
        soundName: 'default',
        importance: 4,
        vibrate: true,
      },
      (created) => console.log(`Channel created: ${created}`)
    );
  }

  async scheduleDailyReminder(hour: number, minute: number): Promise<void> {
    PushNotification.cancelAllLocalNotifications();

    const now = new Date();
    const scheduledTime = new Date();
    scheduledTime.setHours(hour, minute, 0, 0);

    if (scheduledTime <= now) {
      scheduledTime.setDate(scheduledTime.getDate() + 1);
    }

    PushNotification.localNotificationSchedule({
      channelId: 'srs-reviews',
      title: 'Time to Review!',
      message: 'You have cards due for review today.',
      date: scheduledTime,
      allowWhileIdle: true,
      repeatType: 'day',
    });
  }

  async scheduleReviewReminder(dueCount: number): Promise<void> {
    if (dueCount === 0) return;

    PushNotification.localNotification({
      channelId: 'srs-reviews',
      title: 'Reviews Due',
      message: `You have ${dueCount} card${dueCount > 1 ? 's' : ''} waiting for review.`,
      playSound: true,
      soundName: 'default',
    });
  }

  cancelAllNotifications(): void {
    PushNotification.cancelAllLocalNotifications();
  }

  async requestPermissions(): Promise<boolean> {
    return new Promise((resolve) => {
      PushNotification.checkPermissions((permissions) => {
        if (permissions.alert && permissions.badge && permissions.sound) {
          resolve(true);
        } else {
          PushNotification.requestPermissions().then((granted) => {
            resolve(!!granted);
          });
        }
      });
    });
  }
}

export default new NotificationService();
