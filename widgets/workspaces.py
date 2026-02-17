from fabric.hyprland.widgets import HyprlandWorkspaces, WorkspaceButton
from json import loads as parse_json
from fabric.hyprland.service import Hyprland

def special_is_active(workspace_id: int) -> bool:
	jsonstring: str = Hyprland.send_command("-j monitors").reply.decode()
	active_id: int = parse_json(
			jsonstring
	)[0]["specialWorkspace"]["id"]
	return active_id == workspace_id

def is_special(workspace_id: int) -> bool:
	return workspace_id < 0

def button_creation(workspace_id: int) -> WorkspaceButton:
	add_class: list[str] = ["special-workspace"] if is_special(workspace_id) else []
	return WorkspaceButton(
		id=workspace_id,
		style_classes=["workspace"] + add_class
	)

def main(spacing: int = 5) -> HyprlandWorkspaces:
	return HyprlandWorkspaces(
		name="workspaces",
		spacing=spacing,
		buttons_factory=button_creation
	)
