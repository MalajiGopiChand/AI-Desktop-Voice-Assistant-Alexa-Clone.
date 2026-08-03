package com.metis.agent.speech

import android.content.Context
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.util.Log
import java.util.Locale

class MetisTTS(context: Context, private val onInitCompleted: (() -> Unit)? = null) : TextToSpeech.OnInitListener {

    private var tts: TextToSpeech? = TextToSpeech(context, this)
    private var isReady = false
    private var currentOnComplete: (() -> Unit)? = null

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            val result = tts?.setLanguage(Locale.US)
            if (result != TextToSpeech.LANG_MISSING_DATA && result != TextToSpeech.LANG_NOT_SUPPORTED) {
                isReady = true
                setupProgressListener()
                onInitCompleted?.invoke()
            }
        } else {
            Log.e("MetisTTS", "TextToSpeech initialization failed.")
        }
    }

    private fun setupProgressListener() {
        tts?.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
            override fun onStart(utteranceId: String?) {}

            override fun onDone(utteranceId: String?) {
                currentOnComplete?.invoke()
                currentOnComplete = null
            }

            @Deprecated("Deprecated in Java")
            override fun onError(utteranceId: String?) {
                currentOnComplete?.invoke()
                currentOnComplete = null
            }

            override fun onError(utteranceId: String?, errorCode: Int) {
                currentOnComplete?.invoke()
                currentOnComplete = null
            }
        })
    }

    fun speak(text: String, onComplete: (() -> Unit)? = null) {
        if (text.isBlank()) {
            onComplete?.invoke()
            return
        }
        if (!isReady) {
            Log.w("MetisTTS", "TTS not ready yet, skipping audio playback.")
            onComplete?.invoke()
            return
        }

        currentOnComplete = onComplete
        val spokenText = if (text.length > 300) text.substring(0, 297) + "..." else text
        tts?.speak(spokenText, TextToSpeech.QUEUE_FLUSH, null, "MetisSpeechID")
    }

    fun stop() {
        tts?.stop()
        currentOnComplete?.invoke()
        currentOnComplete = null
    }

    fun shutdown() {
        tts?.stop()
        tts?.shutdown()
        currentOnComplete = null
    }
}
