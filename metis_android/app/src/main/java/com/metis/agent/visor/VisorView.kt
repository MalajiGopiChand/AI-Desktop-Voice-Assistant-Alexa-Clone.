package com.metis.agent.visor

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.util.AttributeSet
import android.view.View

/**
 * Animated Cyberpunk Visor View for METIS AI.
 * Visor States:
 *  - IDLE:       [ ⊙ ‿ ⊙ ]
 *  - PROCESSING: [ ⚡ ‿ ⚡ ]
 *  - SPEAKING:   [ 💬 ‿ 💬 ]
 */
class VisorView @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    enum class VisorState(val asciiRepresentation: String, val colorHex: String) {
        IDLE("METIS [ ⊙ ‿ ⊙ ]", "#10a37f"),
        PROCESSING("METIS [ ⚡ ‿ ⚡ ]", "#3b82f6"),
        SPEAKING("METIS [ 💬 ‿ 💬 ]", "#8b5cf6")
    }

    private var currentState: VisorState = VisorState.IDLE
    private val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#10a37f")
        textSize = 54f
        textAlign = Paint.Align.CENTER
        isFakeBoldText = true
    }

    private val wavePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor("#10a37f")
        strokeWidth = 6f
        style = Paint.Style.STROKE
    }

    private var phase = 0f

    fun setState(state: VisorState) {
        this.currentState = state
        textPaint.color = Color.parseColor(state.colorHex)
        wavePaint.color = Color.parseColor(state.colorHex)
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val cx = width / 2f
        val cy = height / 2f

        // Draw Visor Text State
        canvas.drawText(currentState.asciiRepresentation, cx, cy - 20f, textPaint)

        // Draw Animated Waveform Ring
        phase += 0.1f
        val radius = 120f + (Math.sin(phase.toDouble()).toFloat() * 15f)
        canvas.drawCircle(cx, cy, radius, wavePaint)

        invalidate()
    }
}
