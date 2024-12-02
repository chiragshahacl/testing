from textual.widgets import Placeholder, Static


class Header(Static):
    title: str

    DEFAULT_CSS = """
    Header {
        height: 3;
        content-align-horizontal: center;
        content-align-vertical: middle;
        dock: top;
    }
    """


class Footer(Placeholder):
    DEFAULT_CSS = """
    Footer {
        height: 3;
        dock: bottom;
    }
    """


class LeftPanel(Placeholder):
    DEFAULT_CSS = """
    LeftPanel {
        height: 100%;
        width: 30%;
        dock: left;
    }
    """


class RightPanel(Placeholder):
    DEFAULT_CSS = """
    RightPanel {
        height: 100%;
        width: 20%;
        dock: right;
    }
    """
