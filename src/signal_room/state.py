"""Pure state transitions for Signal Room interactions."""


def resolve_selected_entity(previous: str | None, points: list[dict] | None, scope_changed: bool) -> str | None:
    """Return the valid entity selection after a chart event or filter change."""
    if scope_changed:
        return None
    if points is None:
        return previous
    if not points:
        return None
    return points[0]["customdata"][0]


def resolve_location_selection(previous: list[str], options: list[str], view_changed: bool) -> list[str]:
    """Keep location choices valid when the dependent View control changes."""
    if view_changed:
        return options
    return [location for location in previous if location in options]
