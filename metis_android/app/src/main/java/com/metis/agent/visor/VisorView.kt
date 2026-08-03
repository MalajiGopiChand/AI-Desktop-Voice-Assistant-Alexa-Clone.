package com.metis.agent.visor

import android.animation.ValueAnimator
import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.util.AttributeSet
import android.view.View
import android.view.animation.LinearInterpolator

/**
 * Animated Cyberpunk Visor View for METIS AI.
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
    private var phase = 0f

    private val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor(VisorState.IDLE.colorHex)
        textSize = 48f
        textAlign = Paint.Align.CENTER
        isFakeBoldText = true
    }

    private val wavePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        color = Color.parseColor(VisorState.IDLE.colorHex)
        strokeWidth = 5f
        style = Paint.Style.STROKE
    }

    private val pulseAnimator = ValueAnimator.ofFloat(0f, (Math.PI * 2).toFloat()).apply {
        duration = 2000L
        repeatCount = ValueAnimator.INFINITE
        interpolator = LinearInterpolator()
        addUpdateListener { animator ->
            phase = animator.animatedValue as Float
            invalidate()
        }
    }

    init {
        pulseAnimator.start()
    }

    fun setState(state: VisorState) {
        currentState = state
        textPaint.color = Color.parseColor(state.colorHex)
        wavePaint.color = Color.parseColor(state.colorHex)
        invalidate()
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        val cx = width / 2f
        val cy = height / 2f

        canvas.drawText(currentState.asciiRepresentation, cx, cy - 10f, textPaint)

        val radius = 100f + (Math.sin(phase.toDouble()).toFloat() * 12f)
        canvas.drawCircle(cx, cy, radius, wavePaint)
    }

    override fun onDetachedFromWindow() {
        pulseAnimator.cancel()
        super.onDetachedFromWindow()
    }
}
