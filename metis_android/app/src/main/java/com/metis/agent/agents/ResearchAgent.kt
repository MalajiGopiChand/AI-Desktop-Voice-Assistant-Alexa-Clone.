package com.metis.agent.agents

import android.content.Context
import com.metis.agent.network.MetisBrainClient
import com.metis.agent.network.MetisActionResponse

class ResearchAgent(private val context: Context) {

    private val brainClient = MetisBrainClient()

    fun queryKnowledge(
        query: String,
        onResult: (String) -> Unit,
        onError: (String) -> Unit
    ) {
        brainClient.sendCommand(
            commandText = query,
            onSuccess = { response: MetisActionResponse ->
                onResult(response.spokenReply)
            },
            onError = { err ->
                onError("Knowledge query failed: $err")
            }
        )
    }
}
