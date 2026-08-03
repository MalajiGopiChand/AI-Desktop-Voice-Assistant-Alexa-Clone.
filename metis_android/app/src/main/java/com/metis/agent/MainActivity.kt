package com.metis.agent

import android.Manifest
import android.content.Context
import android.content.DialogInterface
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.metis.agent.agents.CommsAgent
import com.metis.agent.agents.DeviceControlAgent
import com.metis.agent.agents.MediaAgent
import com.metis.agent.agents.NotificationAgent
import com.metis.agent.agents.SecurityAgent
import com.metis.agent.network.MetisActionResponse
import com.metis.agent.network.MetisBrainClient
import com.metis.agent.service.MetisWakeWordService
import com.metis.agent.speech.MetisTTS
import com.metis.agent.visor.VisorView
import java.util.Locale

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
    private lateinit var mediaAgent: MediaAgent
    private lateinit var notifAgent: NotificationAgent
    private lateinit var securityAgent: SecurityAgent

    private var speechRecognizer: SpeechRecognizer? = null

    private val requiredPermissions: Array<String> = arrayOf(
        Manifest.permission.RECORD_AUDIO,
        Manifest.permission.CALL_PHONE,
        Manifest.permission.SEND_SMS,
        Manifest.permission.READ_SMS,
        Manifest.permission.READ_CONTACTS,
        Manifest.permission.CAMERA,
        Manifest.permission.ACCESS_FINE_LOCATION
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Explicit Type Parameters for findViewById<T> to prevent Android Studio type inference errors
        visorView = findViewById<VisorView>(R.id.visorView)
        tvStatus = findViewById<TextView>(R.id.tvStatus)
        etCommand = findViewById<EditText>(R.id.etCommand)
        btnSend = findViewById<Button>(R.id.btnSend)
        btnMic = findViewById<Button>(R.id.btnMic)

        val ctx: Context = this
        tts = MetisTTS(ctx)
        brainClient = MetisBrainClient()
        deviceAgent = DeviceControlAgent(ctx)
        commsAgent = CommsAgent(ctx)
        mediaAgent = MediaAgent(ctx)
        notifAgent = NotificationAgent(ctx)
        securityAgent = SecurityAgent(ctx)

        setupSpeechRecognizer()

        // Request all runtime permissions on launch
        checkAndRequestPermissions()

        btnSend.setOnClickListener {
            val cmd: String = etCommand.text.toString().trim()
            if (cmd.isNotEmpty()) {
                etCommand.setText("")
                processCommand(cmd)
            }
        }

        etCommand.setOnEditorActionListener { _, actionId, _ ->
            if (actionId == android.view.inputmethod.EditorInfo.IME_ACTION_SEND) {
                btnSend.performClick()
                true
            } else {
                false
            }
        }

        btnMic.setOnClickListener {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                startVoiceRecognition()
            } else {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.RECORD_AUDIO), 1002)
            }
        }
    }

    private fun setupSpeechRecognizer() {
        if (SpeechRecognizer.isRecognitionAvailable(this)) {
            speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this).apply {
                setRecognitionListener(object : RecognitionListener {
                    override fun onReadyForSpeech(params: Bundle?) {
                        visorView.setState(VisorView.VisorState.PROCESSING)
                        tvStatus.text = "Listening for voice command..."
                    }

                    override fun onBeginningOfSpeech() {}

                    override fun onRmsChanged(rmsdB: Float) {}

                    override fun onBufferReceived(buffer: ByteArray?) {}

                    override fun onEndOfSpeech() {
                        tvStatus.text = "Processing voice command..."
                    }

                    override fun onError(error: Int) {
                        visorView.setState(VisorView.VisorState.IDLE)
                        tvStatus.text = "Speech recognition error ($error). Tap microphone to try again."
                    }

                    override fun onResults(results: Bundle?) {
                        val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                        if (!matches.isNullOrEmpty()) {
                            val recognizedText = matches[0]
                            etCommand.setText(recognizedText)
                            processCommand(recognizedText)
                        } else {
                            visorView.setState(VisorView.VisorState.IDLE)
                            tvStatus.text = "Could not hear any speech. Try again."
                        }
                    }

                    override fun onPartialResults(partialResults: Bundle?) {}

                    override fun onEvent(eventType: Int, params: Bundle?) {}
                })
            }
        }
    }

    private fun startVoiceRecognition() {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault())
            putExtra(RecognizerIntent.EXTRA_PROMPT, "Speak command for METIS...")
        }
        try {
            speechRecognizer?.startListening(intent)
        } catch (e: Exception) {
            Toast.makeText(this, "Voice recognition error: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    private fun checkAndRequestPermissions() {
        val missing: List<String> = requiredPermissions.filter { perm ->
            ContextCompat.checkSelfPermission(this, perm) != PackageManager.PERMISSION_GRANTED
        }
        if (missing.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, missing.toTypedArray(), 1001)
        } else {
            startWakeWordService()
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == 1001 || requestCode == 1002) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                startWakeWordService()
                if (requestCode == 1002) {
                    startVoiceRecognition()
                }
            }
        }
    }

    private fun startWakeWordService() {
        try {
            val serviceIntent = Intent(this, MetisWakeWordService::class.java)
            ContextCompat.startForegroundService(this, serviceIntent)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun processCommand(commandText: String) {
        visorView.setState(VisorView.VisorState.PROCESSING)
        tvStatus.text = "Processing: '$commandText'"

        val lower: String = commandText.lowercase().trim()

        // Full Native Android Mobile Voice Intent Fast Path
        val isMobileNative: Boolean = when {
            lower.startsWith("open ") || lower.contains("gallery") || lower.contains("camera") || lower.contains("settings") -> {
                val target: String = lower.removePrefix("open ").trim()
                val result: String = when {
                    lower.contains("flashlight on") || lower.contains("torch on") -> deviceAgent.toggleFlashlight(true)
                    lower.contains("flashlight off") || lower.contains("torch off") -> deviceAgent.toggleFlashlight(false)
                    else -> deviceAgent.openAppByName(target)
                }
                speakAndDisplay(result)
                true
            }
            lower.startsWith("call ") -> {
                val contact: String = lower.removePrefix("call ").trim()
                speakAndDisplay(deviceAgent.makeCall(contact))
                true
            }
            lower.contains("flashlight") || lower.contains("torch") -> {
                val enable: Boolean = lower.contains("on") || !lower.contains("off")
                speakAndDisplay(deviceAgent.toggleFlashlight(enable))
                true
            }
            lower.startsWith("set alarm") || lower.startsWith("alarm") -> {
                val timeStr: String = lower.removePrefix("set alarm").removePrefix("alarm").trim()
                speakAndDisplay(deviceAgent.setAlarm(if (timeStr.isNotEmpty()) timeStr else "07:00 AM"))
                true
            }
            lower.contains("read notification") -> {
                speakAndDisplay(notifAgent.getSummarizedNotifications())
                true
            }
            lower.contains("play music") || lower.contains("pause music") || lower.contains("toggle music") -> {
                speakAndDisplay(mediaAgent.togglePlayPause())
                true
            }
            lower.contains("next song") || lower.contains("next track") -> {
                speakAndDisplay(mediaAgent.nextTrack())
                true
            }
            else -> false
        }

        if (isMobileNative) return

        // Brain Client fallback for general LLM reasoning queries
        brainClient.sendCommand(
            commandText = commandText,
            onSuccess = { actionResp: MetisActionResponse ->
                runOnUiThread {
                    handleActionResponse(actionResp)
                }
            },
            onError = { error: String ->
                runOnUiThread {
                    visorView.setState(VisorView.VisorState.IDLE)
                    tvStatus.text = "Error: $error"
                }
            }
        )
    }

    private fun handleActionResponse(resp: MetisActionResponse) {
        if (resp.confirmationRequired || securityAgent.requiresConfirmation(resp.action)) {
            val prompt: String = securityAgent.buildConfirmationPrompt(resp.action, resp.params)
            showConfirmationDialog(prompt) {
                executeMobileAction(resp)
            }
        } else {
            executeMobileAction(resp)
        }
    }

    private fun showConfirmationDialog(message: String, onConfirm: () -> Unit) {
        tts.speak(message)
        val builder = AlertDialog.Builder(this)
        builder.setTitle("METIS Security Confirmation")
        builder.setMessage(message)
        builder.setPositiveButton("Confirm") { dialog: DialogInterface, _: Int ->
            dialog.dismiss()
            onConfirm()
        }
        builder.setNegativeButton("Cancel") { dialog: DialogInterface, _: Int ->
            dialog.dismiss()
            visorView.setState(VisorView.VisorState.IDLE)
            tvStatus.text = "Action cancelled by user."
        }
        builder.show()
    }

    private fun executeMobileAction(resp: MetisActionResponse) {
        val resultMessage: String = when (resp.action) {
            "open_app" -> deviceAgent.openAppByName(resp.params["app"] ?: resp.params["name"] ?: "")
            "open_gallery" -> deviceAgent.openAppByName("gallery")
            "open_camera" -> deviceAgent.openAppByName("camera")
            "make_call" -> deviceAgent.makeCall(resp.params["contact"] ?: "")
            "send_sms" -> commsAgent.sendSMS(resp.params["contact"] ?: "", resp.params["message"] ?: "")
            "send_whatsapp" -> commsAgent.sendWhatsAppMessage(resp.params["contact"] ?: "", resp.params["message"] ?: "")
            "set_alarm" -> deviceAgent.setAlarm(resp.params["time"] ?: "07:00 AM")
            "toggle_flashlight" -> deviceAgent.toggleFlashlight(resp.params["state"] == "on")
            "read_notifications" -> notifAgent.getSummarizedNotifications()
            else -> resp.spokenReply
        }

        speakAndDisplay(resultMessage)
    }

    private fun speakAndDisplay(message: String) {
        visorView.setState(VisorView.VisorState.SPEAKING)
        tvStatus.text = message
        tts.speak(message) {
            runOnUiThread {
                visorView.setState(VisorView.VisorState.IDLE)
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        try {
            speechRecognizer?.destroy()
        } catch (e: Exception) {
            e.printStackTrace()
        }
        tts.shutdown()
    }
}
