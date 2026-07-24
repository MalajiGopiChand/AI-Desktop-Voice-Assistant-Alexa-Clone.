package com.metis.agent.network

import android.util.Log
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import kotlin.concurrent.thread

data class MetisActionResponse(
    val status: String,
    val target: String,
    val agent: String,
    val action: String,
    val params: Map<String, String>,
    val spokenReply: String,
    val response: String,
    val confirmationRequired: Boolean
)

class MetisBrainClient(private val backendUrl: String = "https://metis-brain.vercel.app") {

    fun sendCommand(
        commandText: String,
        model: String = "llama-3.3-70b-versatile",
        onSuccess: (MetisActionResponse) -> Unit,
        onError: (String) -> Unit
    ) {
        thread {
            try {
                val url = URL("$backendUrl/api/command")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json")
                conn.doOutput = true
                conn.connectTimeout = 10000
                conn.readTimeout = 10000

                val payload = JSONObject().apply {
                    put("command", commandText)
                    put("model", model)
                }

                OutputStreamWriter(conn.outputStream).use { writer ->
                    writer.write(payload.toString())
                    writer.flush()
                }

                if (conn.responseCode == 200) {
                    val responseStr = BufferedReader(InputStreamReader(conn.inputStream)).use { it.readText() }
                    val json = JSONObject(responseStr)

                    val paramsMap = mutableMapOf<String, String>()
                    if (json.has("params")) {
                        val pObj = json.getJSONObject("params")
                        pObj.keys().forEach { key ->
                            paramsMap[key] = pObj.getString(key)
                        }
                    }

                    val actionResp = MetisActionResponse(
                        status = json.optString("status", "success"),
                        target = json.optString("target", "mobile"),
                        agent = json.optString("agent", "ResearchAgent"),
                        action = json.optString("action", "speak"),
                        params = paramsMap,
                        spokenReply = json.optString("spoken_reply", "Request complete."),
                        response = json.optString("response", ""),
                        confirmationRequired = json.optBoolean("confirmation_required", false)
                    )
                    onSuccess(actionResp)
                } else {
                    onError("HTTP Error: ${conn.responseCode}")
                }
            } catch (e: Exception) {
                Log.e("MetisBrainClient", "Network error: ${e.message}")
                onError("Connection error: ${e.message}")
            }
        }
    }
}
