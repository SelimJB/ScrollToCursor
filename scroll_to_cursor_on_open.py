import sublime
import sublime_plugin

initialized_views = set()

print("ScrollToCursor plugin loaded")


class ScrollToCursorWhenActivatedCommand(sublime_plugin.EventListener):
    def load_settings(self):
        settings = sublime.load_settings("scroll_to_cursor_on_open.sublime-settings")
        self.enable_scroll_to_cursor = settings.get("enable_scroll_to_cursor", True)
        self.scroll_to_top_if_no_cursor = settings.get(
            "scroll_to_top_if_no_cursor", True
        )
        self.verbose = settings.get("verbose", False)
        if self.verbose:
            print(
                "enable_scroll_to_cursor={} scroll_to_top_if_no_cursor={}".format(
                    self.enable_scroll_to_cursor, self.scroll_to_top_if_no_cursor
                )
            )

    def on_load_async(self, view):
        self.load_settings()
        for window in sublime.windows():
            for group in range(window.num_groups()):
                active_view_in_group = window.active_view_in_group(group)
                if active_view_in_group:
                    if active_view_in_group.id() not in initialized_views:
                        initialized_views.add(active_view_in_group.id())
                        if self.verbose:
                            print(
                                "On load :",
                                active_view_in_group.id(),
                                active_view_in_group.file_name(),
                            )

    def on_activated_async(self, view):
        self.load_settings()
        if view.id() in initialized_views:
            return

        if self.verbose:
            print("Open :", view.id(), view.file_name())

        initialized_views.add(view.id())

        if view.settings().get("is_widget"):
            return

        sel = view.sel()

        if len(sel) == 0:
            if self.verbose:
                print("No cursor detected in view :", view.id())
            if self.scroll_to_top_if_no_cursor:
                view.set_viewport_position((0, 0), False)

        else:
            cursor_layout_pos = view.text_to_layout(sel[0].begin())
            view_height = view.viewport_extent()[1]
            current_x_scroll = view.viewport_position()[0]

            # Calculate the new vertical scroll position to center the cursor
            new_scroll_pos_y = max(0, cursor_layout_pos[1] - view_height / 2)

            view.set_viewport_position((current_x_scroll, new_scroll_pos_y), False)
