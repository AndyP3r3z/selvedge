from importlib import import_module
from keyword import iskeyword
from types import ModuleType
from typing import Any, Callable, Iterable, Literal
from pathlib import Path

from fabric.widgets.box import Box
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.wayland import WaylandWindow
from gi.repository import Gtk, GObject # type: ignore

CONFIG_DIR: Path = Path(__file__).parent
_widgets: dict[str, ModuleType] = {}

def _assert_secure_module(name: str) -> None:
	"""
	Makes sure importing a `name` of a module is secure below this directory.
	Saves the `name` in `_widgets` with the format
	`'module_name:object_imported': <module>`

	Parameters
	----------
	name
		The name of the module.
	"""
	name = name.strip()
	identifier: str = name.split(":")[0]
	not_valid_identifier_error: str = f"'{identifier}' is not a valid identifier."
	not_existing_module_error: str = f"Neither 'widgets.{name}' nor '{name}' module exist. Make sure your module inside `{CONFIG_DIR}/widgets` or in a fabric component."
	name_not_widget_error: str = "{clss} is not a GTK widget."
	not_existing_callable_error: str = f"No callable named 'main' in 'widgets.{name}'. Make sure your module name and function are called the same."
	# 1. Make sure it is secure.
	all_identifiers: list[str] = identifier.split(".")
	if iskeyword(identifier) or not all([ident.isidentifier() for ident in all_identifiers]):
		print(identifier)
		raise ValueError(not_valid_identifier_error)
	# 2. Make sure it exists.
	new_module: ModuleType
	try:
		if ":" in name:
			module_name: str
			class_names: list[str]
			module_name, *class_names = name.rsplit(":")
			if "fabric" not in name:
				# TODO: Better explanation of why this raises an error.
				raise ModuleNotFoundError(not_existing_module_error)
			new_module = import_module(module_name)
			for clss in class_names:
				f: Any | None = getattr(new_module, clss, None)
				if not (isinstance(f, Gtk.Widget) or GObject.type_is_a(f.__gtype__, Gtk.Widget.__gtype__)): # type: ignore
					raise ImportError(name_not_widget_error.format(clss=clss))
				_widgets[f"{identifier}:{clss}"] = new_module
			return
		new_module = import_module(f".widgets.{name}", package="selvedge")
		func: Any | None = getattr(new_module, 'main', None)
		if not callable(func):
			raise ImportError(not_existing_callable_error)
		_widgets[name] = new_module
	except ModuleNotFoundError:
		raise ModuleNotFoundError(not_existing_module_error)
	return

def _create_widget(name: str, **kwargs) -> Any:
	name = name.strip()
	module_kwargs: dict[str, Any] | None = kwargs.get(name)
	module: ModuleType = _widgets[name]
	object_imported: str = 'main' if ':' not in name else name.split(":")[-1]
	func: Callable = getattr(module, object_imported)
	if module_kwargs is None: return func()
	return func(**module_kwargs)

def main(
	anchor: list[Literal['left', 'top', 'right', 'bottom']] = ["left", "top", "right"],
	margins: dict[Literal['top', 'left', 'right', 'bottom'], int] = {"top": 0, "left": 0, "right": 0, "bottom": 0},
	widgets: dict[Literal['start', 'center', 'end'], str | list[str] | None] = {"start": None, "center": None, "end": None},
	name: str = "stbar",
	style_classes: Iterable[str]| str | None = None,
	**kwargs: Any
	) -> WaylandWindow:
	"""
	Creates a Statusbar.

	Parameters
	----------
	anchor
		A list of anchors to the widget.
	margins
		A dictionary with the list of margins for the bar. If any is missing,
		it is treated as zero.
	widgets
		A dictionary with the [list of] widgets for the start, center and end
		of the statusbar.
	name
		Unique identifier of the Statusbar, defaults to "statusbar".
	style_classes
		All CSS classes this widget belongs to.

	Returns
	-------
	WaylandWindow
		The Window object.
	"""
	# Treat input.
	margin: dict[str, int] = {"top": 0, "left": 0, "right": 0, "bottom": 0} | margins
	# Assert the existence of the modules given.
	for value in widgets.values():
		if value is None: continue
		assert isinstance(value, (list, str)), "Widgets must be a string or a list of strings."
		if isinstance(value, str): value = [value]
		for mod_name in value:
			_assert_secure_module(mod_name)
		continue
	# Create and return the window.
	return WaylandWindow(
		name=name,
		anchor=" ".join(anchor),
		margin=" ".join([
			f"{margin[x]}px"
			for x in ("top", "right", "bottom", "left")]),
		style_classes=style_classes,
		layer="top",
		exclusivity="auto",
		child=CenterBox(
			name="inner-bar",
			orientation='horizontal',
			start_children=Box(
				name="stbar-start",
				style_classes="stbar-part",
				children=[
					_create_widget(m, **kwargs)
					for m in widgets["start"]], # type: ignore
			) if widgets.get("start") else None,
			center_children=Box(
				name="stbar-center",
				style_classes="stbar-part",
				children=[
					_create_widget(m, **kwargs)
					for m in widgets["center"]], # type: ignore
			) if widgets.get("center") else None,
			end_children=Box(
				name="stbar-end",
				style_classes="stbar-part",
				children=[
					_create_widget(m, **kwargs)
					for m in widgets["end"]], # type: ignore
			) if widgets.get("end") else None,
		)
	)
