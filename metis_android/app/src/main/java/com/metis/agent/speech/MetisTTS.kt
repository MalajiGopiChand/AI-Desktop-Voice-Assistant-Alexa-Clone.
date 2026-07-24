package com.metis.agent.speech

import android.content.Context
import android.speech.tts.TextToSpeech
import android.util.Log
import java.util.Locale

class MetisTTS(context: Context, private val onInitCompleted: (() -> Unit)? = null) : TextToSpeech.OnInitListener {

    private var tts: TextToSpeech? = TextToSpeech(context, this)
    private var isReady = false

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            val result = tts?.setLanguage(Locale.US)
            if (result != TextToSpeech.LANG_MISSING_DATA && result != TextToSpeech.LANG_NOT_SUPPORTED) {
                isReady = true
                onInitCompleted?.invoke()
            }
        } else {
            Log.e("MetisTTS", "TextToSpeech initialization failed.")
        }
    }

    fun speak(text: String, onComplete: (() -> Unit)? = null) {
        if (!isReady || text.isBlank()) return
        // Truncate to maximum 300 characters as mandated by Metis spec
        val spokenText = if (text.length > 300) text.substring(0, 297) + "..." else text
        tts?.speak(spokenText, TextToSpeech.QUEUE_FLUSH, null, "MetisSpeechID")
    }

    fun stop() {
        tts?.stop()
    }

    fun shutdown() {
        tts?.stop()
        tts?.shutdown()
    }
}
