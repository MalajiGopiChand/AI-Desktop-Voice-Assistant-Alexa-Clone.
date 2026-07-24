package com.metis.agent.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat

class MetisWakeWordService : Service() {

    override fun onCreate() {
        super.onCreate()
        startForegroundServiceNotification()
        startWakeWordDetection()
    }

    private fun startForegroundServiceNotification() {
        val channelId = "MetisWakeWordChannel"
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "METIS Voice Assistant Service",
                NotificationManager.IMPORTANCE_LOW
            )
            val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }

        val notification: Notification = NotificationCompat.Builder(this, channelId)
            .setContentTitle("METIS AI OS Active")
            .setContentText("Listening for 'Hey Metis' wake word...")
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setOngoing(true)
            .build()

        startForeground(1001, notification)
    }

    private fun startWakeWordDetection() {
        // Continuous low-power wake word listener setup ("Hey Metis")
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
    }
}
