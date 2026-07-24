package com.metis.agent.agents

import android.content.Context
import android.util.Log

class SecurityAgent(private val context: Context) {

    private val trustedActions = mutableSetOf<String>()

    fun requiresConfirmation(actionName: String): Boolean {
        if (trustedActions.contains(actionName)) return false
        val sensitive = listOf("send_sms", "send_whatsapp", "make_call", "delete_file")
        return sensitive.contains(actionName)
    }

    fun buildConfirmationPrompt(actionName: String, params: Map<String, String>): String {
        return when (actionName) {
            "send_sms", "send_whatsapp" -> "Are you sure you want to send this message to ${params["contact"]}?"
            "make_call" -> "Are you sure you want to call ${params["contact"]}?"
            else -> "Please confirm if you want to execute $actionName."
        }
    }

    fun setTrusted(actionName: String) {
        trustedActions.add(actionName)
    }
}
