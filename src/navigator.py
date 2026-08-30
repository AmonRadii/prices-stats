from PySide6.QtCore import Qt, QEvent, QObject


class KeyboardNavigator(QObject):
    """Manages focus and keyboard navigation between widgets."""
    
    def __init__(self, widgets: dict, parent=None):
        super().__init__(parent)
        self.w = widgets

    def _set_focus(self, widget):
        """
        Sets input focus to a target widget while maintaining keyboard focus styling.

        Applies `Qt.FocusReason.TabFocusReason` when transferring focus. This ensures 
        that the operating system's widget style correctly renders visual focus 
        indicators (such as outlines or focus rings) for keyboard-driven navigation.

        Args:
            widget (QWidget, optional): The target Qt widget to receive focus. 
            If set to None, defaults to `self.price_input`. Defaults to None.

        Returns:
            None
            """
        widget.setFocus(Qt.FocusReason.TabFocusReason)

    def eventFilter(self, watched, event):
        """Intercepts keyboard events to handle directional arrow-key navigation.

        Monitors `KeyPress` events dispatched to registered UI elements. Overrides
        default widget arrow-key behavior to allow seamless bidirectional focus
        traversal between input fields, buttons, and the product list.

        Args:
            watched (QObject): The Qt object or widget currently receiving the event.
            event (QEvent): The event being processed.

        Returns:
            bool: True if the key press event was handled and should be consumed;
            False if it should be passed down to the base class event filter."""
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()

            # From Name Input
            if watched == self.w['name'] and key == Qt.Key.Key_Down:
                self._set_focus(self.w['price'])
                return True

            # From Price Input
            elif watched == self.w['price']:
                if key == Qt.Key.Key_Up:
                    self._set_focus(self.w['name'])
                    return True
                elif key == Qt.Key.Key_Down:
                    self._set_focus(self.w['add'])
                    return True

            # From Add Product Button
            elif watched == self.w['add']:
                if key in (Qt.Key.Key_Up, Qt.Key.Key_Left):
                    self._set_focus(self.w['price'])
                    return True
                elif key in (Qt.Key.Key_Down, Qt.Key.Key_Right):
                    self._set_focus(self.w['list'])
                    if self.w['list'].count() > 0 and self.w['list'].currentRow() < 0:
                        self.w['list'].setCurrentRow(0)
                    return True

            # From Product List Widget
            elif watched == self.w['list']:
                curr = self.w['list'].currentRow()
                count = self.w['list'].count()
                if key == Qt.Key.Key_Up and (count == 0 or curr <= 0):
                    self._set_focus(self.w['add'])
                    return True
                elif key == Qt.Key.Key_Down and (count == 0 or curr >= count - 1):
                    self._set_focus(self.w['save'])
                    return True

            # From Save Button
            elif watched == self.w['save']:
                if key in (Qt.Key.Key_Up, Qt.Key.Key_Left):
                    self._set_focus(self.w['list'])
                    if self.w['list'].count() > 0:
                        self.w['list'].setCurrentRow(self.w['list'].count() - 1)
                    return True
                elif key in (Qt.Key.Key_Down, Qt.Key.Key_Right):
                    self._set_focus(self.w['delete'])
                    return True

            # From Delete Selected Button
            elif watched == self.w['delete']:
                if key in (Qt.Key.Key_Up, Qt.Key.Key_Left):
                    self._set_focus(self.w['save'])
                    return True
                elif key in (Qt.Key.Key_Down, Qt.Key.Key_Right):
                    self._set_focus(self.w['clear'])
                    return True
            
            # From Clear All Button
            elif watched == self.w['clear']:
                if key in (Qt.Key.Key_Up, Qt.Key.Key_Left):
                    self._set_focus(self.w['delete'])
                    return True
                elif key in (Qt.Key.Key_Down, Qt.Key.Key_Right):
                    self._set_focus(self.w['name'])
                    return True

        return super().eventFilter(watched, event)