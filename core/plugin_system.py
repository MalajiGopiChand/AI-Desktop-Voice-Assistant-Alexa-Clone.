"""
Metis AI OS — Plugin Marketplace & Skills Extensibility Engine.
Registers third-party skills (Spotify, Notion, GitHub, Discord, VS Code, Jira, Figma).
"""

class PluginSystem:
    def __init__(self):
        self.plugins = {
            "spotify": {"name": "Spotify Media Integration", "active": True, "skills": ["play", "pause", "skip", "playlist"]},
            "github": {"name": "GitHub & Git Integration", "active": True, "skills": ["commit", "push", "pull_requests", "issues"]},
            "vscode": {"name": "VS Code IDE Workspace", "active": True, "skills": ["open_project", "run_server", "explain_code"]},
            "gmail": {"name": "Gmail & Calendar Sync", "active": True, "skills": ["read_emails", "compose", "schedule_event"]},
            "notion": {"name": "Notion Knowledge Notes", "active": True, "skills": ["read_notes", "add_page"]}
        }

    fun_get_plugins = lambda self: self.plugins

    def list_active_plugins(self):
        return [p["name"] for p in self.plugins.values() if p["active"]]

    def register_plugin(self, plugin_id, name, skills):
        self.plugins[plugin_id] = {"name": name, "active": True, "skills": skills}
        return f"Plugin '{name}' successfully registered with skills: {', '.join(skills)}"


plugin_system = PluginSystem()
