package com.metis.agent.agents

import android.content.Context
import android.content.Intent
import android.content.pm.ApplicationInfo
import android.content.pm.PackageManager
import android.hardware.camera2.CameraManager
import android.net.Uri
import android.provider.AlarmClock
import android.provider.ContactsContract
import android.provider.MediaStore
import android.provider.Settings
import android.util.Log

class DeviceControlAgent(private val context: Context) {

    fun makeCall(numberOrContact: String): String {
        val trimmed = numberOrContact.trim()
        if (trimmed.isEmpty()) return "Please specify a contact or phone number to call."

        var phoneNumber = trimmed
        // If query is not a numeric phone number, attempt contact resolution by name
        if (!trimmed.all { it.isDigit() || it == '+' || it == '-' || it == ' ' || it == '(' || it == ')' }) {
            val resolvedNumber = resolveContactPhoneNumber(trimmed)
            if (resolvedNumber != null) {
                phoneNumber = resolvedNumber
            } else {
                return "Could not find phone number for contact '$trimmed'."
            }
        }

        try {
            val intent = Intent(Intent.ACTION_CALL).apply {
                data = Uri.parse("tel:$phoneNumber")
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
            return "Placing phone call to $trimmed."
        } catch (e: Exception) {
            Log.e("DeviceControlAgent", "Call failed: ${e.message}")
            return "Unable to place call automatically. Please verify call permissions."
        }
    }

    private fun resolveContactPhoneNumber(contactName: String): String? {
        return try {
            val uri = ContactsContract.CommonDataKinds.Phone.CONTENT_URI
            val projection = arrayOf(
                ContactsContract.CommonDataKinds.Phone.NUMBER,
                ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME
            )
            val selection = "${ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME} LIKE ?"
            val selectionArgs = arrayOf("%$contactName%")

            var resolved: String? = null
            context.contentResolver.query(uri, projection, selection, selectionArgs, null)?.use { cursor ->
                if (cursor.moveToFirst()) {
                    val numberIndex = cursor.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)
                    if (numberIndex != -1) {
                        resolved = cursor.getString(numberIndex)
                    }
                }
            }
            resolved
        } catch (e: Exception) {
            Log.e("DeviceControlAgent", "Contact lookup failed: ${e.message}")
            null
        }
    }

    fun setAlarm(timeStr: String, label: String = "Metis Alarm"): String {
        try {
            val (hour, minute) = parseTime(timeStr)
            val intent = Intent(AlarmClock.ACTION_SET_ALARM).apply {
                putExtra(AlarmClock.EXTRA_MESSAGE, label)
                putExtra(AlarmClock.EXTRA_HOUR, hour)
                putExtra(AlarmClock.EXTRA_MINUTES, minute)
                putExtra(AlarmClock.EXTRA_SKIP_UI, true)
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            context.startActivity(intent)
            return "Alarm set for %02d:%02d.".format(hour, minute)
        } catch (e: Exception) {
            return "Failed to set alarm: ${e.message}"
        }
    }

    private fun parseTime(timeStr: String): Pair<Int, Int> {
        val lower = timeStr.lowercase().trim()
        val isPm = lower.contains("pm")
        val isAm = lower.contains("am")
        val clean = lower.replace("am", "").replace("pm", "").trim()

        val parts = clean.split(":", " ")
        var hour = 7
        var minute = 0

        if (parts.isNotEmpty()) {
            hour = parts[0].toIntOrNull() ?: 7
        }
        if (parts.size > 1) {
            minute = parts[1].toIntOrNull() ?: 0
        }

        if (isPm && hour < 12) {
            hour += 12
        } else if (isAm && hour == 12) {
            hour = 0
        }

        return Pair(hour.coerceIn(0, 23), minute.coerceIn(0, 59))
    }

    fun toggleFlashlight(enable: Boolean): String {
        try {
            val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
            val cameraId = cameraManager.cameraIdList.firstOrNull()
                ?: return "No camera flashlight detected on this device."
            cameraManager.setTorchMode(cameraId, enable)
            return if (enable) "Flashlight turned on." else "Flashlight turned off."
        } catch (e: Exception) {
            return "Flashlight error: ${e.message}"
        }
    }

    /**
     * Smart App Launcher & Intent Handler
     * Resolves voice requests like "gallery", "photos", "camera", "spotify", "whatsapp", "settings"
     */
    fun openAppByName(appNameQuery: String): String {
        val query = appNameQuery.lowercase().trim()
        val pm = context.packageManager

        try {
            // 1. Gallery / Photos Intent
            if (query.contains("gallery") || query.contains("photo") || query.contains("album")) {
                val galleryIntent = Intent(Intent.ACTION_VIEW).apply {
                    type = "image/*"
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK
                }
                if (galleryIntent.resolveActivity(pm) != null) {
                    context.startActivity(galleryIntent)
                    return "Opening Gallery."
                }
            }

            // 2. Camera Intent
            if (query.contains("camera") || query.contains("photo capture")) {
                val cameraIntent = Intent(MediaStore.INTENT_ACTION_STILL_IMAGE_CAMERA).apply {
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK
                }
                if (cameraIntent.resolveActivity(pm) != null) {
                    context.startActivity(cameraIntent)
                    return "Opening Camera."
                }
            }

            // 3. Settings Intent
            if (query.contains("setting") || query.contains("preferences")) {
                val settingsIntent = Intent(Settings.ACTION_SETTINGS).apply {
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK
                }
                context.startActivity(settingsIntent)
                return "Opening Settings."
            }

            // 4. Well-known package names mapping
            val knownPackages = mapOf(
                "whatsapp" to "com.whatsapp",
                "spotify" to "com.spotify.music",
                "youtube" to "com.google.android.youtube",
                "chrome" to "com.android.chrome",
                "maps" to "com.google.android.apps.maps",
                "gmail" to "com.google.android.gm",
                "instagram" to "com.instagram.android",
                "facebook" to "com.facebook.katana",
                "telegram" to "org.telegram.messenger"
            )

            for ((key, pkg) in knownPackages) {
                if (query.contains(key)) {
                    val intent = pm.getLaunchIntentForPackage(pkg)
                    if (intent != null) {
                        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                        context.startActivity(intent)
                        return "Opening ${key.replaceFirstChar { it.uppercase() }}."
                    }
                }
            }

            // 5. Package Manager Full Installed App Label Match
            val installedApps = pm.getInstalledApplications(PackageManager.GET_META_DATA)
            for (appInfo in installedApps) {
                if ((appInfo.flags and ApplicationInfo.FLAG_SYSTEM) != 0 &&
                    pm.getLaunchIntentForPackage(appInfo.packageName) == null
                ) {
                    continue
                }

                val appLabel = pm.getApplicationLabel(appInfo).toString().lowercase()
                if (appLabel.contains(query) || query.contains(appLabel)) {
                    val launchIntent = pm.getLaunchIntentForPackage(appInfo.packageName)
                    if (launchIntent != null) {
                        launchIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                        context.startActivity(launchIntent)
                        return "Opening ${pm.getApplicationLabel(appInfo)}."
                    }
                }
            }

            return "Could not find application '$appNameQuery' installed on this device."
        } catch (e: Exception) {
            Log.e("DeviceControlAgent", "App launch error: ${e.message}")
            return "Error opening app: ${e.message}"
        }
    }

    fun openApp(packageName: String): String {
        return openAppByName(packageName)
    }
}
