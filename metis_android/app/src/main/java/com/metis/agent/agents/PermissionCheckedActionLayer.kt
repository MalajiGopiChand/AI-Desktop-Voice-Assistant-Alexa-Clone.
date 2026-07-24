package com.metis.agent.agents

import android.content.Context
import android.content.pm.PackageManager
import androidx.core.content.ContextCompat

class PermissionCheckedActionLayer(private val context: Context) {

    fun hasPermission(permission: String): Boolean {
        return ContextCompat.checkSelfPermission(context, permission) == PackageManager.PERMISSION_GRANTED
    }

    fun executeWithCheck(
        permission: String,
        actionName: String,
        onGranted: () -> Unit,
        onPermissionNeeded: (String) -> Unit
    ) {
        if (hasPermission(permission)) {
            onGranted()
        } else {
            onPermissionNeeded(permission)
        }
    }
}
