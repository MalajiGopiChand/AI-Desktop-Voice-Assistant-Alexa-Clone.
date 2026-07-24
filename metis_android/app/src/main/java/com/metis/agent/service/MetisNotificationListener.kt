package com.metis.agent.service

import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.util.Log

data class MetisNotification(
    val appName: String,
    val title: String,
    val text: String,
    val timestamp: Long
)

class MetisNotificationListener : NotificationListenerService() {

    companion object {
        private val notificationHistory = mutableListOf<MetisNotification>()

        fun getRecentNotifications(): List<MetisNotification> {
            return notificationHistory.toList()
        }
    }

    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        super.onNotificationPosted(sbn)
        sbn?.let {
            val packageName = it.packageName
            val extras = it.notification.extras
            val title = extras.getString("android.title") ?: ""
            val text = extras.getCharSequence("android.text")?.toString() ?: ""

            if (title.isNotBlank() || text.isNotBlank()) {
                val notif = MetisNotification(packageName, title, text, System.currentTimeMillis())
                notificationHistory.add(0, notif)
                if (notificationHistory.size > 50) notificationHistory.removeAt(notificationHistory.size - 1)
                Log.d("MetisNotifListener", "Captured notification from $packageName: $title - $text")
            }
        }
    }
}
