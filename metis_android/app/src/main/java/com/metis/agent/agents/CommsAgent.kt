package com.metis.agent.agents

import android.content.Context
import android.telephony.SmsManager
import android.util.Log
import com.metis.agent.service.MetisAccessibilityService

class CommsAgent(private val context: Context) {

    fun sendSMS(phoneNumber: String, messageText: String): String {
        return try {
            val smsManager = SmsManager.getDefault()
            smsManager.sendTextMessage(phoneNumber, null, messageText, null, null)
            "SMS message successfully sent to $phoneNumber."
        } catch (e: Exception) {
            Log.e("CommsAgent", "Failed to send SMS: ${e.message}")
            "Failed to send SMS: ${e.message}"
        }
    }

    fun sendWhatsAppMessage(contactName: String, messageText: String): String {
        val accessibilityService = MetisAccessibilityService.instance
        if (accessibilityService != null) {
            val success = accessibilityService.performWhatsAppAutomation(contactName, messageText)
            return if (success) {
                "Sent WhatsApp message to $contactName."
            } else {
                "Opened WhatsApp chat for $contactName. Please tap send."
            }
        }
        return "Accessibility Service is not active. Please grant Accessibility permission in settings."
    }
}
