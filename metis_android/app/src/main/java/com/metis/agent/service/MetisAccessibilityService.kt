package com.metis.agent.service

import android.accessibilityservice.AccessibilityService
import android.content.Intent
import android.os.Bundle
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo

class MetisAccessibilityService : AccessibilityService() {

    companion object {
        var instance: MetisAccessibilityService? = null
            private set
    }

    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Intercept window events for app UI automation
    }

    override fun onInterrupt() {}

    fun performWhatsAppAutomation(contactName: String, messageText: String): Boolean {
        val rootNode = rootInActiveWindow ?: return false
        
        // Search and click search bar or contact name in WhatsApp
        val searchNodes = rootNode.findAccessibilityNodeInfosByText("Search")
        if (searchNodes.isNotEmpty()) {
            searchNodes[0].performAction(AccessibilityNodeInfo.ACTION_CLICK)
        }

        // Fill message body
        val textInputNodes = rootNode.findAccessibilityNodeInfosByText("Type a message")
        if (textInputNodes.isNotEmpty()) {
            val arguments = Bundle().apply {
                putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_STRING, messageText)
            }
            textInputNodes[0].performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, arguments)
            return true
        }

        return false
    }

    override fun onDestroy() {
        super.onDestroy()
        if (instance == this) instance = null
    }
}
