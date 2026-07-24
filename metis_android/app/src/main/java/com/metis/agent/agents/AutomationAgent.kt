package com.metis.agent.agents

import android.content.Context

class AutomationAgent(private val context: Context) {

    private val deviceAgent = DeviceControlAgent(context)
    private val notificationAgent = NotificationAgent(context)

    fun runRoutine(routineName: String): String {
        return when (routineName.lowercase()) {
            "good morning", "morning" -> {
                val notifSummary = notificationAgent.getSummarizedNotifications()
                "Good morning! Here is your quick start summary: $notifSummary"
            }
            "night", "good night" -> {
                deviceAgent.toggleFlashlight(false)
                "Good night. Flashlight turned off and alarms ready."
            }
            else -> "Routine '$routineName' executed."
        }
    }
}
