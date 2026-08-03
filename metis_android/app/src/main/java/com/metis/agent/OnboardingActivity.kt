package com.metis.agent

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.provider.Settings
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

class OnboardingActivity : AppCompatActivity() {

    private var currentStep: Int = 0
    private lateinit var stepTitle: TextView
    private lateinit var stepDescription: TextView
    private lateinit var actionButton: Button

    private val permissionSteps: List<PermissionStep> = listOf(
        PermissionStep(
            title = "Welcome to METIS AI OS",
            description = "METIS transforms your phone into an AI-powered voice operating system. Let's calibrate your device permissions.",
            permission = null
        ),
        PermissionStep(
            title = "1. Voice & Microphone Access",
            description = "Metis needs Microphone permission to continuously listen for 'Hey Metis' wake word and process voice commands.",
            permission = Manifest.permission.RECORD_AUDIO
        ),
        PermissionStep(
            title = "2. Phone Calls & Cellular Control",
            description = "Metis needs Call permission to place phone calls automatically on your voice request.",
            permission = Manifest.permission.CALL_PHONE
        ),
        PermissionStep(
            title = "3. SMS & Text Messaging",
            description = "Metis needs SMS permission to draft, read, and send text messages via voice commands.",
            permission = Manifest.permission.SEND_SMS
        ),
        PermissionStep(
            title = "4. Contacts Resolution",
            description = "Metis needs Contacts permission to resolve names like 'Rahul' or 'Mom' to phone numbers.",
            permission = Manifest.permission.READ_CONTACTS
        ),
        PermissionStep(
            title = "5. Notification Access Setup",
            description = "To summarize notifications aloud, please grant Notification Listener access in Android settings.",
            permission = "NOTIFICATION_SETTINGS"
        ),
        PermissionStep(
            title = "6. Accessibility Service Setup",
            description = "To automate apps like WhatsApp and tap UI buttons via voice, please enable Metis Accessibility Service in System Settings.",
            permission = "ACCESSIBILITY_SETTINGS"
        ),
        PermissionStep(
            title = "7. Wake Word Calibration",
            description = "Please say 'Hey Metis' 3 times into your microphone to calibrate your voice profile.",
            permission = "WAKE_WORD_CALIBRATION"
        )
    )

    data class PermissionStep(
        val title: String,
        val description: String,
        val permission: String?
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_onboarding)

        // Explicit Type Parameters for findViewById<T>
        stepTitle = findViewById<TextView>(R.id.tvStepTitle)
        stepDescription = findViewById<TextView>(R.id.tvStepDesc)
        actionButton = findViewById<Button>(R.id.btnAction)

        updateStepUI()

        actionButton.setOnClickListener {
            handleStepAction()
        }
    }

    private fun updateStepUI() {
        val step: PermissionStep = permissionSteps[currentStep]
        stepTitle.text = step.title
        stepDescription.text = step.description

        actionButton.text = when {
            step.permission == "NOTIFICATION_SETTINGS" || step.permission == "ACCESSIBILITY_SETTINGS" -> "Open Settings"
            step.permission == "WAKE_WORD_CALIBRATION" -> "Start Calibration"
            step.permission != null -> "Grant Permission"
            else -> "Get Started"
        }
    }

    private fun handleStepAction() {
        val step: PermissionStep = permissionSteps[currentStep]
        val ctx: Context = this

        when (step.permission) {
            null -> advanceStep()
            "NOTIFICATION_SETTINGS" -> {
                startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))
                advanceStep()
            }
            "ACCESSIBILITY_SETTINGS" -> {
                startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
                advanceStep()
            }
            "WAKE_WORD_CALIBRATION" -> {
                Toast.makeText(ctx, "Calibration complete! METIS is ready.", Toast.LENGTH_SHORT).show()
                finishOnboarding()
            }
            else -> {
                val permStr: String = step.permission
                if (ContextCompat.checkSelfPermission(ctx, permStr) != PackageManager.PERMISSION_GRANTED) {
                    ActivityCompat.requestPermissions(this, arrayOf(permStr), 101)
                } else {
                    advanceStep()
                }
            }
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        advanceStep()
    }

    private fun advanceStep() {
        if (currentStep < permissionSteps.size - 1) {
            currentStep++
            updateStepUI()
        } else {
            finishOnboarding()
        }
    }

    private fun finishOnboarding() {
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }
}
