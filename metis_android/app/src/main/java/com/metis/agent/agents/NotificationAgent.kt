package com.metis.agent.agents

import android.content.Context
import com.metis.agent.service.MetisNotificationListener

class NotificationAgent(private val context: Context) {

    fun getSummarizedNotifications(): String {
        val notifications = MetisNotificationListener.getRecentNotifications()
        if (notifications.isEmpty()) {
            return "You have no unread notifications right now."
        }

        val summary = StringBuilder("You have ${notifications.size} recent notification(s):\n")
        notifications.take(5).forEachIndexed { idx, notif ->
            summary.append("${idx + 1}. ${notif.title} from ${notif.appName}: ${notif.text}\n")
        }
        return summary.toString()
    }
}
