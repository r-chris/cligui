"""Make a gui from a command line interface."""
import argparse
import tkinter as tk
import threading
from .stdoutwrapper import Wrapper
import time
from collections import OrderedDict


class Frame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.pack(fill=tk.BOTH, expand=True)

class Widget(object):
    """A bridge between the GUI and the command line argument."""
    def __init__(self, action, parent):
        """
        :param argparse.Action action:
        :param tk.Frame parent:
        :return:
        """

        self.action = action
        self.frame = tk.Frame(parent)
        self.frame.pack(side=tk.TOP)

    def _dolabel(self):
        text = self.action.dest + ('*:' if self.action.required else ':')
        self._label = tk.Label(self.frame, text=text, anchor=tk.E, width=10)
        self._label.pack(side=tk.LEFT)

    def _dohelp(self):
        self._help = tk.Label(self.frame, text=self.action.help, anchor=tk.W, width=30)
        self._help.pack(side=tk.LEFT)


class _AppendWidget(Widget):

    def __init__(self, action, parent):
        """
        :param argparse.Action action:
        :return:
        """
        super().__init__(action, parent)

    def getval(self):
        pass


class _AppendConstWidget(Widget):

    def __init__(self, action, parent):
        """
        :param argparse.Action action:
        :return:
        """
        super().__init__(action, parent)

    def getval(self):
        pass


class _CountWidget(Widget):

    def __init__(self, action, parent):
        """
        :param argparse.Action action:
        :return:
        """
        super().__init__(action, parent)

    def getval(self):
        pass


class _HelpWidget(Widget):

    def __init__(self, action, parent):

        """
        :param argparse.Action action:
        :return:
        """
        super().__init__(action, parent)

    def getval(self):
        pass


class _StoreWidget(Widget):
    def __init__(self, action, parent):
        """
        :param argparse.Action action:
        :return:
        """
        super().__init__(action, parent)
        self._dolabel()
        self._entry = tk.Entry(self.frame, width=30)
        self._entry.pack(side=tk.LEFT)
        self._dohelp()
        if action.default:
            self._entry.insert(0, str(action.default))

    def getval(self):
        textval = self._entry.get()
        if self.action.type:
            return self.action.type(textval)
        else:
            return textval


class _StoreConstWidget(Widget):
    def __init__(self, action, parent):
        """
        :param argparse.Action action:
        :return:
        """
        super().__init__(action, parent)

    def getval(self):
        pass


class _StoreFalseWidget(Widget):
    def __init__(self, action, parent):
        """
        :param argparse.Action action:
        :return:
        """
        super().__init__(action, parent)

    def getval(self):
        pass


class _StoreTrueWidget(Widget):
    def __init__(self, action, parent):
        """
        :param argparse.Action action:
        :return:
        """
        super().__init__(action, parent)
        self._dolabel()
        self.state = tk.IntVar()
        self.cb = tk.Checkbutton(self.frame, width=30, anchor=tk.E, variable=self.state)
        self.cb.pack(side=tk.LEFT)
        self._dohelp()

    def getval(self):
        return self.state.get()


_widgetmap = {argparse._StoreAction: _StoreWidget,
              argparse._AppendAction: _AppendWidget,
              argparse._AppendConstAction: _AppendConstWidget,
              argparse._CountAction: _CountWidget,
              argparse._HelpAction: _HelpWidget,
              argparse._StoreConstAction: _StoreConstWidget,
              argparse._StoreFalseAction: _StoreFalseWidget,
              argparse._StoreTrueAction: _StoreTrueWidget}


class CliGui(object):
    def __init__(self, parser, onrun=None, show=True):
        """

        :param argparse.ArgumentParser parser: parser to turn into a gui
        :param callable run: callable to run when the run button is pressed.
          The callable must take an argparse.Namespace as its only argument.
        """
        self.parser = parser
        self.onrun = onrun
        self.widgets = OrderedDict()
        self.make_gui()
        self.stdout = Wrapper(self.onwrite)
        if show:
            self.show()

    def make_gui(self):
        self.root = tk.Tk()
        self.frame = Frame(self.root)
        for action in self.parser._actions:
            self.widgets[action] = self.add_action(action)

        # add run and cancel buttons to the bottom.
        buttonframes = tk.Frame(self.frame)
        self.run = tk.Button(buttonframes, text='Run',
                            command=self.parse_args)
        self.cancel = tk.Button(buttonframes, text='Cancel',
                                command=self.quit)
        self.run.pack(side=tk.LEFT)
        self.cancel.pack(side=tk.LEFT)
        buttonframes.pack()
        self.stdoutframe = Frame(self.frame)

        self.entry = tk.Text(self.stdoutframe)
        self.entry.configure(state='disabled')
        self.entry.pack(fill=tk.BOTH)

    def onwrite(self, text):
        self.entry.configure(state='normal')
        self.entry.insert(tk.INSERT, text)
        self.entry.configure(state='disabled')

    def parse_args(self):
        ns = argparse.Namespace()
        for action, widget in self.widgets.items():
            if isinstance(widget, _HelpWidget):
                continue
            val = widget.getval()
            setattr(ns, widget.action.dest, val)

        if self.onrun:
            self.onrun(ns)
        return ns

    def quit(self):
        self.frame.parent.quit()

    def show(self):
        self.root.geometry('600x400+300+300')
        self.root.mainloop()

    def add_action(self, action):
        """
        :param argparse.Action action:
        :return: None
        """
        widget = _widgetmap[type(action)](action, self.frame)
        return widget
