package com.metis.agent

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import com.metis.agent.agents.CommsAgent
import com.metis.agent.agents.DeviceControlAgent
import com.metis.agent.agents.NotificationAgent
import com.metis.agent.agents.SecurityAgent
import com.metis.agent.network.MetisActionResponse
import com.metis.agent.network.MetisBrainClient
import com.metis.agent.service.MetisWakeWordService
import com.metis.agent.speech.MetisTTS
import com.metis.agent.visor.VisorView

class MainActivity : AppCompatActivity() {

    private lateinit var visorView: VisorView
    private lateinit var tvStatus: TextView
    private lateinit var etCommand: EditText
    private lateinit var btnSend: Button
    private lateinit var btnMic: Button

    private lateinit var tts: MetisTTS
    private lateinit var brainClient: MetisBrainClient
    private lateinit var deviceAgent: DeviceControlAgent
    private lateinit var commsAgent: CommsAgent
    private lateinit var notifAgent: NotificationAgent
    private lateinit var securityAgent: SecurityAgent

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        visorView = findViewById(R.id.visorView)
        tvStatus = findViewById(R.id.tvStatus)
        etCommand = findViewById(R.id.etCommand)
        btnSend = findViewById(R.id.btnSend)
        btnMic = findViewById(R.id.btnMic)

        tts = MetisTTS(this)
        brainClient = MetisBrainClient()
        deviceAgent = DeviceControlAgent(this)
        commsAgent = CommsAgent(this)
        notifAgent = NotificationAgent(this)
        securityAgent = SecurityAgent(this)

        // Start Foreground Wake Word Service ("Hey Metis")
        val serviceIntent = Intent(this, MetisWakeWordService::class.java)
        startService(serviceIntent)

        btnSend.setOnClickListener {
            val cmd = etCommand.text.toString().trim()
            if (cmd.isNotEmpty()) {
                etCommand.setText("")
                processCommand(cmd)
            }
        }

        btnMic.setOnClickListener {
            visorView.setState(VisorView.VisorState.PROCESSING)
            tvStatus.text = "Listening for voice command..."
        }
    }

    private fun processCommand(commandText: String) {
        visorView.setState(VisorView.VisorState.PROCESSING)
        tvStatus.text = "Processing: '$commandText'"

        brainClient.sendCommand(
            commandText = commandText,
            onSuccess = { actionResp ->
                runOnUiThread {
                    handleActionResponse(actionResp)
                }
            },
            onError = { error ->
                runOnUiThread {
                    visorView.setState(VisorView.VisorState.IDLE)
                    tvStatus.text = "Error: $error"
                }
            }
        )
    }

    private fun handleActionResponse(resp: MetisActionResponse) {
        if (resp.confirmationRequired || securityAgent.requiresConfirmation(resp.action)) {
            val prompt = securityAgent.buildConfirmationPrompt(resp.action, resp.params)
            showConfirmationDialog(prompt) {
                executeMobileAction(resp)
            }
        } else {
            executeMobileAction(resp)
        }
    }

    private fun showConfirmationDialog(message: String, onConfirm: () -> Unit) {
        tts.speak(message)
        AlertDialog.Builder(this)
            .setTitle("METIS Security Confirmation")
            .setMessage(message)
            .setPositiveButton("Confirm") { dialog, _ ->
                dialog.dismiss()
                onConfirm()
            }
            .setNegativeButton("Cancel") { dialog, _ ->
                dialog.dismiss()
                visorView.setState(VisorView.VisorState.IDLE)
                tvStatus.text = "Action cancelled by user."
            }
            .show()
    }

    private fun executeMobileAction(resp: MetisActionResponse) {
        val resultMessage = when (resp.action) {
            "make_call" -> deviceAgent.makeCall(resp.params["contact"] ?: "")
            "send_sms" -> commsAgent.sendSMS(resp.params["contact"] ?: "", resp.params["message"] ?: "")
            "send_whatsapp" -> commsAgent.sendWhatsAppMessage(resp.params["contact"] ?: "", resp.params["message"] ?: "")
            "set_alarm" -> deviceAgent.setAlarm(resp.params["time"] ?: "07:00 AM")
            "toggle_flashlight" -> deviceAgent.toggleFlashlight(resp.params["state"] == "on")
            "read_notifications" -> notifAgent.getSummarizedNotifications()
            else -> resp.spokenReply
        }

        visorView.setState(VisorView.VisorState.SPEAKING)
        tvStatus.text = resultMessage
        tts.speak(resultMessage) {
            runOnUiThread {
                visorView.setState(VisorView.VisorState.IDLE)
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        tts.shutdown()
    }
}
