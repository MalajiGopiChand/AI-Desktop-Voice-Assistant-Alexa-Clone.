package com.metis.agent.agents

import android.content.Context
import android.content.Intent
import android.hardware.camera2.CameraManager
import android.net.Uri
import android.provider.AlarmClock
import android.provider.Settings
import android.util.Log

class DeviceControlAgent(private val context: Context) {

    fun makeCall(numberOrContact: String): String {
        try {
            val intent = Intent(Intent.ACTION_CALL).apply {
                data = Uri.parse("tel:$numberOrContact")
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
            return "Calling $numberOrContact."
        } catch (e: Exception) {
            Log.e("DeviceControlAgent", "Call failed: ${e.message}")
            return "Unable to place call automatically. Please check phone permissions."
        }
    }

    fun setAlarm(timeStr: String, label: String = "Metis Alarm"): String {
        try {
            val intent = Intent(AlarmClock.ACTION_SET_ALARM).apply {
                putExtra(AlarmClock.EXTRA_MESSAGE, label)
                putExtra(AlarmClock.EXTRA_HOUR, 7)
                putExtra(AlarmClock.EXTRA_MINUTES, 0)
                putExtra(AlarmClock.EXTRA_SKIP_UI, true)
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
            return "Alarm set for $timeStr."
        } catch (e: Exception) {
            return "Failed to set alarm: ${e.message}"
        }
    }

    fun toggleFlashlight(enable: Boolean): String {
        try {
            val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
            val cameraId = cameraManager.cameraIdList[0]
            cameraManager.setTorchMode(cameraId, enable)
            return if (enable) "Flashlight turned on." else "Flashlight turned off."
        } catch (e: Exception) {
            return "Flashlight error: ${e.message}"
        }
    }

    fun openApp(packageName: String): String {
        try {
            val launchIntent = context.packageManager.getLaunchIntentForPackage(packageName)
            if (launchIntent != null) {
                launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                context.startActivity(launchIntent)
                return "Opening application."
            }
            return "Application package $packageName not found."
        } catch (e: Exception) {
            return "Could not launch app: ${e.message}"
        }
    }
}
