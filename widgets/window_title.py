# from typing import Any, Literal
from fabric.hyprland.service import Hyprland, HyprlandEvent
from fabric.widgets.image import Image
from fabric.hyprland.widgets import HyprlandActiveWindow
from fabric.utils import Any, FormattedString
from fabric.widgets.box import Box
from gi.repository import Gio # type: ignore

APPS: list = Gio.AppInfo.get_all()
icon_name: str = ""

def _truncate(string: str, length: int = 40, suffix: str = "...") -> str:
	_s: str = string.title().replace("-", " ")
	_s = _s if "Unknown" != _s else "Desktop"
	if len(_s) <= length: return _s
	return _s[:length-len(suffix)] + suffix

def find_app(cl: str) -> Any:
	app = next(
		(
			app for app in APPS
			if app.get_id().removesuffix('.desktop') == cl),
		None)
	return app

def get_icon(_: Hyprland, event: HyprlandEvent) -> str:
	cl: str = event.data[0]
	if not cl or cl == 'unknown':
		return 'user-desktop'
	app = find_app(cl)
	app_icon = app.get_icon() if app else None
	return app_icon.to_string() if app_icon else 'application-x-executable'

def get_title(cl: str, title: str) -> str:
	if not title: return 'Desktop'
	global icon_name
	app = find_app(cl)
	icon_widget = app.get_icon() if app else None
	icon_name = icon_widget.to_string() if icon_widget else 'application-x-executable'
	return (
		_truncate(app.get_name() if app else title) #,
	)

def main(icon: bool = True, title: bool = True, ) -> Box:
	global icon_name
	children: list = []
	title_widget: HyprlandActiveWindow = HyprlandActiveWindow(
		name="window-titlename",
		formatter=FormattedString(
			"{get_title(win_class, win_title)}",
			 get_title=get_title),
		image=Image(icon=icon_name)
	)
	if icon:
		connection: Hyprland = title_widget.connection
		icon_widget: Image = Image(
			name="window-icon",
			image=Image(icon=icon_name))
		connection.connect(
			"event::activewindow",
			lambda s, e: icon_widget.set_from_icon_name(get_icon(s, e)))
		connection.connect(
			"event::closewindow",
			lambda s, e: icon_widget.set_from_icon_name(get_icon(s, e)))
		children.append(icon_widget)
	if title:
		children.append(title_widget)
	return Box(
		name="window-title",
		children=children,
		spacing=8
	)
